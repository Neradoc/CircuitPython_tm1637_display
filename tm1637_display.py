# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Neradoc
#
# SPDX-License-Identifier: MIT
# pylint: disable=too-many-arguments
"""
`tm1637_display`
================================================================================

Driver for the TM1637 display.


* Author(s): Neradoc

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/Neradoc/CircuitPython_tm1637_display.git"

import digitalio
import microcontroller
from microcontroller import Pin
from micropython import const

try:
    from typing import Union
except ImportError:
    pass

_DOT_SEGMENT = const(0b10000000)

_DEFAULT_BIT_DELAY = const(100)

_TM1637_I2C_COMM1 = const(0x40)
_TM1637_I2C_COMM2 = const(0xC0)
_TM1637_I2C_COMM3 = const(0x80)

"""
//
//      A
//     ---
//  F |   | B
//     -G-
//  E |   | C
//     ---
//      D
"""
digit_to_segment = [
    # XGFEDCBA
    0b00111111,  # 0
    0b00000110,  # 1
    0b01011011,  # 2
    0b01001111,  # 3
    0b01100110,  # 4
    0b01101101,  # 5
    0b01111101,  # 6
    0b00000111,  # 7
    0b01111111,  # 8
    0b01101111,  # 9
    0b01110111,  # A
    0b01111100,  # b
    0b00111001,  # C
    0b01011110,  # d
    0b01111001,  # E
    0b01110001,  # F
]
_MINUS_SEGMENTS = const(0b01000000)
letter_to_segment = {
    letter: digit_to_segment[pos] for pos, letter in enumerate("0123456789abcdef")
}
letter_to_segment.update(
    {
        "": 0,
        " ": 0,
        "-": _MINUS_SEGMENTS,
        "g": 0b00111101,
        "h": 0b01110110,
        "i": 0b00110000,
        "j": 0b00001110,
        "l": 0b00111000,
        "n": 0b01010100,
        "o": 0b00111111,
        "p": 0b01110011,
        "q": 0b01100111,
        "r": 0b01010000,
        "s": 0b01101101,
        "t": 0b00110001,
        "u": 0b00111110,
        "v": 0b00011100,
        "y": 0b01100110,
    }
)


def _upside_down(val):
    """Upside down version of a letter in 7-segment coding"""
    return (
        (val & 0b10000000)  # dot
        | (val & 0b1000000)  # G segment
        | (val & 0b111) << 3  # ABC -> DEF
        | (val & 0b111000) >> 3  # DEF -> ABC
    )


class TM1637Display:
    """
    Numeric 7-segment display.

    :param microcontroller.Pin clock: The clock pin.
    :param microcontroller.Pin data: The data pin.
    :param int length: The number of characters on the display.
    :param int digit_order: The order of the digits on the display, if it doesn't
        match the internal order of the chip. Reverse it for LTR.
    :param bool auto_write: True if the display should immediately change when set.
        If False, `show` must be called explicitly.
    :param int bit_delay: The (minimum) delay between bit twiddlings in us.
    :param int brightness: The brightness, value from 0 to 7, False if off.
    :param int rotation: Rotate the display 180 degrees with a value of 180, default 0.
    """

    def __init__(
        self,
        clock: Pin,
        data: Pin,
        length: int = 4,
        digit_order: tuple = None,
        auto_write: bool = True,
        bit_delay: int = _DEFAULT_BIT_DELAY,
        brightness: int = 7,
        rotation: int = 0,
    ):
        if not digit_order:
            self.digit_order = list(range(length))
        else:
            if len(digit_order) != length:
                raise ValueError("digit_order is a list of all digit positions")
            self.digit_order = digit_order

        # don't auto write during setup
        self._auto_write = False
        self._bit_delay = bit_delay
        self._brightness = 0xF  # default full on
        self.brightness = brightness
        self._rotation = 0
        self.rotation = rotation
        self.digits = bytearray(length)

        # Set the pin direction and default value.
        if isinstance(clock, Pin):
            self.clk = digitalio.DigitalInOut(clock)
            self.clk.switch_to_output(True)
        else:
            self.clk = clock

        if isinstance(data, Pin):
            self.dio = digitalio.DigitalInOut(data)
            self.dio.switch_to_output(True)
        else:
            self.dio = data

        self._auto_write = auto_write

    def _set_brightness(self, brightness: int, enabled: bool = True):
        """Set the brightness from 0 to 7, and enable light or not"""
        self._brightness = (brightness & 0x7) | (0x08 if enabled else 0x00)

    @property
    def brightness(self):
        """Brightness is a value between 0 and 7. Set to False to turn off."""
        if self._brightness & 0x8:
            return False
        return self._brightness & 0x7

    @brightness.setter
    def brightness(self, value: int):
        if value is False:
            self._set_brightness(0, enabled=False)
        elif value not in range(8):
            raise ValueError("brightness must be in the range 0-7")
        else:
            self._set_brightness(value)
        if self._auto_write:
            self.show()

    @property
    def rotation(self):
        """Rotation is 0 or 180"""
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: int):
        if not rotation in (0, 180):
            raise ValueError("rotation must be 0 or 180")
        if rotation != self._rotation:
            self.digit_order = tuple(reversed(self.digit_order))
        self._rotation = rotation
        if self._auto_write:
            self.show()

    def set_segments(self, segments: bytes, pos=0):
        """Directly set the bit values of the segments"""
        self._start()
        self._write_byte(_TM1637_I2C_COMM1)
        self._stop()

        # Write COMM2 + first digit address
        self._start()
        self._write_byte(_TM1637_I2C_COMM2)

        # Write the data bytes
        length = len(self.digit_order)
        digit_order = self.digit_order
        for offset in range(length):
            k = digit_order[(pos + offset) % length]
            if self.rotation:
                self._write_byte(_upside_down(segments[k]))
            else:
                self._write_byte(segments[k])
        self._stop()

        # Write COMM3 + brightness
        self._start()
        self._write_byte(_TM1637_I2C_COMM3 + (self._brightness & 0x0F))
        self._stop()

    def clear(self):
        """Clear the display, nothing on it."""
        self.set_segments(bytearray(len(self.digits)))

    def _delay(self):
        microcontroller.delay_us(self._bit_delay)

    def _start(self):
        self.dio.value = False
        self._delay()

    def _stop(self):
        self.dio.value = False
        self._delay()
        self.clk.value = True
        self._delay()
        self.dio.value = True
        self._delay()

    def _write_byte(self, data: int):
        """Write a byte to the board, bit bangging... is it I2C ?"""
        # 8 Data Bits
        for _ in range(8):
            # CLK low
            self.clk.value = False
            self._delay()

            # Set data bit
            if data & 0x01:
                self.dio.value = True
            else:
                self.dio.value = False

            self._delay()

            # CLK high
            self.clk.value = True
            self._delay()
            data = data >> 1

        # Wait for acknowledge
        # CLK to zero
        self.clk.value = False
        self.dio.switch_to_input(digitalio.Pull.UP)
        self._delay()

        # CLK to high
        self.clk.value = True
        self._delay()
        ack = self.dio.value
        if ack is False:
            self.dio.switch_to_output(False)
        else:
            # ?? do nothing ? raise ? (switch to output anyway)
            self.dio.switch_to_output(True)

        self._delay()
        self.clk.value = False
        self._delay()

        return ack

    def show_dots(self, dots: tuple):
        """Set the locations of dots on the display."""
        for i, num in enumerate(self.digits):
            if dots[i]:
                self.digits[i] = num | 0x80
            else:
                self.digits[i] = num & 0x7F
        if self._auto_write:
            self.show()

    def show(self):
        """Refresh the display and show the changes."""
        self.set_segments(self.digits)

    @property
    def auto_write(self) -> bool:
        """Auto write updates to the display."""
        return self._auto_write

    @auto_write.setter
    def auto_write(self, auto_write: bool) -> None:
        self._auto_write = bool(auto_write)

    def print(self, value: Union[int, float, str], decimal: int = 0):
        """Print the value to the display.

        :param str|float|str value: The value to print
        :param int decimal: The number of decimal places for a floating point
            number if decimal is greater than zero, or the input number is an
            integer if decimal is zero.
        """
        if isinstance(value, str):
            self._text(value)
        elif isinstance(value, (int, float)):
            self._number(value, decimal)
        else:
            raise ValueError("Unsupported display value type: {}".format(type(value)))
        if self._auto_write:
            self.show()

    def print_hex(self, value: Union[int, float, str]):
        """Print the value as a hexidecimal string to the display.

        :param int|float|str value: The number to print
        """
        if isinstance(value, int):
            self.print("{0:x}".format(value))
        else:
            self.print(value)

    def _text(self, text: str) -> None:
        """Display the specified text."""
        length = len(self.digits)
        k = length - 1
        dot = False
        for letter in reversed(text):
            if letter == ".":
                dot = True
                continue
            if letter.lower() not in letter_to_segment:
                raise ValueError(f"Letter {letter} has not matching representation")
            self.digits[k] = letter_to_segment[letter.lower()]
            if dot:
                self.digits[k] |= _DOT_SEGMENT
                dot = False
            k = k - 1
            if k < 0:
                break
        for i in range(k + 1):
            self.digits[i] = 0

    def _number(self, number: Union[float, int], decimal: int = 0) -> str:
        """Format and siplay a number"""
        if isinstance(number, float) and decimal > 0:
            stnum = f"{number:f}"
        else:
            stnum = str(int(number)) + "."
        dot = stnum.find(".")
        # cut the decimals
        if dot >= 0:
            stnum = stnum[: dot + decimal + 1]
            stnum = stnum[: len(self.digits) + 1]
        # make it a text
        self._text(stnum)

    def deinit(self):
        """Deinit. Free the pins."""
        self.clk.deinit()
        self.dio.deinit()
