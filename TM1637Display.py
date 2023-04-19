'''
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
'''
import digitalio
import microcontroller

SEG_A = 0b00000001
SEG_B = 0b00000010
SEG_C = 0b00000100
SEG_D = 0b00001000
SEG_E = 0b00010000
SEG_F = 0b00100000
SEG_G = 0b01000000
SEG_DP= 0b10000000

DEFAULT_BIT_DELAY = 100

TM1637_I2C_COMM1 = 0x40
TM1637_I2C_COMM2 = 0xC0
TM1637_I2C_COMM3 = 0x80

'''
//
//      A
//     ---
//  F |   | B
//     -G-
//  E |   | C
//     ---
//      D
'''
digitToSegment = [
# XGFEDCBA
  0b00111111,    # 0
  0b00000110,    # 1
  0b01011011,    # 2
  0b01001111,    # 3
  0b01100110,    # 4
  0b01101101,    # 5
  0b01111101,    # 6
  0b00000111,    # 7
  0b01111111,    # 8
  0b01101111,    # 9
  0b01110111,    # A
  0b01111100,    # b
  0b00111001,    # C
  0b01011110,    # d
  0b01111001,    # E
  0b01110001     # F
]

minusSegments = 0b01000000

class TM1637Display:
    def __init__(self, pinClk, pinDIO, bitDelay=DEFAULT_BIT_DELAY):
        # Copy the pin numbers
        self.Clk = digitalio.DigitalInOut(pinClk)
        self.DIO = digitalio.DigitalInOut(pinDIO)
        self._bitDelay = bitDelay
        self.brightness = 0x0F

        # Set the pin direction and default value.
        # Both pins are set as inputs, allowing the pull-up resistors to pull them up
        self.Clk.switch_to_output(True)
        self.DIO.switch_to_output(True)

    def setBrightness(self, brightness, on=True):
        self.brightness = (brightness & 0x7) | ( 0x08 if on else 0x00)

    def setSegments(self, segments, length=0, pos=0):
        length = length or len(segments)
        self.start()
        self.writeByte(TM1637_I2C_COMM1)
        self.stop()

        # Write COMM2 + first digit address
        self.start()
        self.writeByte(TM1637_I2C_COMM2 + (pos & 0x03))

        # Write the data bytes
        for k in range(length):
            self.writeByte(segments[k])

        self.stop()

        # Write COMM3 + brightness
        self.start()
        self.writeByte(TM1637_I2C_COMM3 + (self.brightness & 0x0f))
        self.stop()

    def clear(self):
        self.setSegments((0, 0, 0, 0))

    def showNumberDec(self, num, leading_zero=False, length=4, pos=0):
        self.showNumberDecEx(num, 0, leading_zero, length, pos)

    def showNumberDecEx(self, num, dots=0, leading_zero=False, length=4, pos=0):
        self.showNumberBaseEx(
            -10 if num < 0 else 10,
            -num if num < 0 else num,
            dots,
            leading_zero,
            length,
            pos
        )

    def showNumberHexEx(self, num, dots=0, leading_zero=False, length=4, pos=0):
        self.showNumberBaseEx(16, num, dots, leading_zero, length, pos)

    def showNumberBaseEx(self, base, num, dots=0, leading_zero=False, length=4, pos=0):
        negative = False
        if base < 0:
            base = -base
            negative = True

        digits = bytearray(4)

        if num == 0 and not leading_zero:
            # Singular case - take care separately
            for i in range(length - 1):
                digits[i] = 0
            digits[length - 1] = self.encodeDigit(0)

        else:
            #uint8_t i = length-1
            #if (negative) {
            #	# Negative number, show the minus sign
            #    digits[i] = minusSegments
            #	i--
            #}
            for i in range(length-1, -1, -1):
                digit = num % base

                if digit == 0 and num == 0 and leading_zero == False:
                    # Leading zero is blank
                    digits[i] = 0
                else:
                    digits[i] = self.encodeDigit(digit)

                if digit == 0 and num == 0 and negative:
                    digits[i] = minusSegments
                    negative = False

                num //= base

        if dots != 0:
            self.showDots(dots, digits)
        self.setSegments(digits, length, pos)


    def bitDelay(self):
        microcontroller.delay_us(self._bitDelay)

    def start(self):
        self.DIO.value = True # ?
        microcontroller.delay_us(self._bitDelay)

    def stop(self):
        self.DIO.value = False # ?
        microcontroller.delay_us(self._bitDelay)
        self.Clk.value = True
        microcontroller.delay_us(self._bitDelay)
        self.DIO.value = True
        microcontroller.delay_us(self._bitDelay)

    def writeByte(self, byte):
        data = byte

        # 8 Data Bits
        for i in range(8):
            # CLK low
            self.Clk.value = False
            microcontroller.delay_us(self._bitDelay)

            # Set data bit
            if data & 0x01:
                self.DIO.value = True
            else:
                self.DIO.value = False # ?

            microcontroller.delay_us(self._bitDelay)

            # CLK high
            self.Clk.value = True
            microcontroller.delay_us(self._bitDelay)
            data = data >> 1

        # Wait for acknowledge
        # CLK to zero
        self.Clk.value = False
        self.DIO.switch_to_input(digitalio.Pull.UP)
        microcontroller.delay_us(self._bitDelay)

        # CLK to high
        self.Clk.value = True
        microcontroller.delay_us(self._bitDelay)
        ack = self.DIO.value
        if ack is False:
            print("ack")
            self.DIO.switch_to_output(False) #?
        else:
            print("noack")
            self.DIO.switch_to_output(True)


        microcontroller.delay_us(self._bitDelay)
        self.Clk.value = False
        microcontroller.delay_us(self._bitDelay)

        return ack

    def showDots(self, dots, digits):
        for i in range(4):
            digits[i] |= (dots & 0x80)
            dots <<= 1
        return digits

    def encodeDigit(self, digit):
        return digitToSegment[digit & 0x0f]
