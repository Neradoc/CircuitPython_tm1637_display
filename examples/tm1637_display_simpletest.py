# SPDX-FileCopyrightText: Copyright (c) 2023 Neradoc
#
# SPDX-License-Identifier: Unlicense

import time
import board
from tm1637_display import TM1637Display

display = TM1637Display(board.SCL, board.SDA)
DELAY = 0.5

display.print("HELLO")
time.sleep(DELAY)

for i in range(7):
    display.print(-31.141516, i)
    display.brightness = i
    time.sleep(DELAY)

display.print(0)  # Expect: _____0
time.sleep(DELAY)
display.print("0000")  # Expect: __0000
time.sleep(DELAY)
display.print(1)  # Expect: _____1
time.sleep(DELAY)
display.print(f"{1:06d}")  # Expect: 000001
time.sleep(DELAY)
display.print(301)  # Expect: ___301
time.sleep(DELAY)
display.clear()
display.print(f"{14}  ")  # Expect: ____14__
time.sleep(DELAY)
display.clear()
display.print(f"{4:02}")  # Expect: ____04
time.sleep(DELAY)
display.print(-1)  # Expect: ____-1
time.sleep(DELAY)
display.print(-12)  # Expect: ___-12
time.sleep(DELAY)
display.print(-999)  # Expect: __-999
time.sleep(DELAY)
display.clear()
display.print(f"{-5}  ")  # Expect: ____-5__
time.sleep(DELAY)
display.print_hex(0xADAF)  # Expect: __ADAF
time.sleep(DELAY)
display.print_hex(0x2C)  # Expect: ____2C
time.sleep(DELAY)
display.print_hex(f"{0xd1:06}")  # Expect: 0000d1
time.sleep(DELAY)
display.clear()
display.print_hex(f"{0xd1:<6}")  # Expect: d1____
time.sleep(DELAY)
