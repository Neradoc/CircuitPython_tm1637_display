"""
//  Author: avishorp@gmail.com
//
//  This library is free software; you can redistribute it and/or
//  modify it under the terms of the GNU Lesser General Public
//  License as published by the Free Software Foundation; either
//  version 2.1 of the License, or (at your option) any later version.
//
//  This library is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//  Lesser General Public License for more details.
//
//  You should have received a copy of the GNU Lesser General Public
//  License along with this library; if not, write to the Free Software
//  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import digitalio
import microcontroller

try:
    from typing import Union, List, Tuple, Optional, Dict
    from microcontroller import Pin
except ImportError:
    pass

SEG_A = 0b00000001
SEG_B = 0b00000010
SEG_C = 0b00000100
SEG_D = 0b00001000
SEG_E = 0b00010000
SEG_F = 0b00100000
SEG_G = 0b01000000
SEG_DP = 0b10000000

DEFAULT_BIT_DELAY = 100

TM1637_I2C_COMM1 = 0x40
TM1637_I2C_COMM2 = 0xC0
TM1637_I2C_COMM3 = 0x80

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
minus_segments = 0b01000000
letter_to_segment = {
    letter: digit_to_segment[pos] for pos, letter in enumerate("0123456789abcdef")
}
letter_to_segment.update(
    {
        "": 0,
        " ": 0,
        "-": minus_segments,
    }
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
    :param int bit_delay: the (minimum) delay between bit twiddlings in us.
    """

    def __init__(
        self,
        clock: Pin,
        data: Pin,
        length: int = 4,
        digit_order: tuple = None,
        auto_write: bool = True,
        bit_delay: int = DEFAULT_BIT_DELAY,
    ):
        if not digit_order:
            self.digit_order = (2, 1, 0, 5, 4, 3)
        else:
            if len(digit_order) != length:
                raise ValueError("digit_order is a list of all digit positions")
            self.digit_order = digit_order

        self._bit_delay = bit_delay
        self._auto_write = auto_write
        self.brightness = 7
        self.digits = bytearray(length)

        # Set the pin direction and default value.
        self.Clk = digitalio.DigitalInOut(clock)
        self.DIO = digitalio.DigitalInOut(data)
        self.Clk.switch_to_output(True)
        self.DIO.switch_to_output(True)

    def _set_brightness(self, brightness: int, on: bool = True):
        """Set the brightness from 0 to 7, and enable light or not"""
        self._brightness = (brightness & 0x7) | (0x08 if on else 0x00)

    @property
    def brightness(self):
        """Brightness is a value between 0 and 7. Set to None to turn off."""
        if self._brightness & 0x8:
            return False
        return self._brightness & 0x7

    @brightness.setter
    def brightness(self, value: int):
        if value is None:
            self._set_brightness(0, on=False)
        elif value not in range(8):
            raise ValueError("brightness must be in the range 0-7")
        else:
            self._set_brightness(value)

    def set_segments(self, segments: bytes, pos=0):
        """Directly set the bit values of the segments"""
        self._start()
        self._write_byte(TM1637_I2C_COMM1)
        self._stop()

        # Write COMM2 + first digit address
        self._start()
        self._write_byte(TM1637_I2C_COMM2)

        # Write the data bytes
        length = len(self.digit_order)
        digit_order = self.digit_order
        for offset in range(length):
            k = digit_order[(pos + offset) % length]
            self._write_byte(segments[k])
        self._stop()

        # Write COMM3 + brightness
        self._start()
        self._write_byte(TM1637_I2C_COMM3 + (self._brightness & 0x0F))
        self._stop()

    def clear(self):
        self.set_segments(bytearray(len(self.digits)))

    def bit_delay(self):
        microcontroller.delay_us(self._bit_delay)

    def _start(self):
        self.DIO.value = False  # ?
        self.bit_delay()

    def _stop(self):
        self.DIO.value = False  # ?
        self.bit_delay()
        self.Clk.value = True
        self.bit_delay()
        self.DIO.value = True
        self.bit_delay()

    def _write_byte(self, data: int):
        """Write a byte to the board, bit bangging... is it I2C ?"""
        # 8 Data Bits
        for i in range(8):
            # CLK low
            self.Clk.value = False
            self.bit_delay()

            # Set data bit
            if data & 0x01:
                self.DIO.value = True
            else:
                self.DIO.value = False  # ?

            self.bit_delay()

            # CLK high
            self.Clk.value = True
            self.bit_delay()
            data = data >> 1

        # Wait for acknowledge
        # CLK to zero
        self.Clk.value = False
        self.DIO.switch_to_input(digitalio.Pull.UP)
        self.bit_delay()

        # CLK to high
        self.Clk.value = True
        self.bit_delay()
        ack = self.DIO.value
        if ack is False:
            self.DIO.switch_to_output(False)
        else:
            # ?? do nothing ? raise ? (switch to output anyway)
            self.DIO.switch_to_output(True)

        self.bit_delay()
        self.Clk.value = False
        self.bit_delay()

        return ack

    def show_dots(self, dots: tuple):
        """Set the locations of dots on the display."""
        for i, num in enumerate(self.digits):
            if dots[i]:
                self.digits[i] |= 0x80
            else:
                self.digits[i] &= 0x7F
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

    def print(self, value: Union(int, float, str), decimal: int = 0):
        """Print the value to the display.

        :param str|float value: The value to print
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

    def print_hex(self, value: Union(int, float, str)):
        """Print the value as a hexidecimal string to the display.

        :param int|str value: The number to print
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
            self.digits[k] = letter_to_segment[letter.lower()]
            if dot:
                self.digits[k] |= SEG_DP
                dot = False
            k = k - 1
            if k < 0:
                break
        for i in range(k + 1):
            self.digits[i] = 0

    def _number(self, number: Union(float, int), decimal: int = 0) -> str:
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
