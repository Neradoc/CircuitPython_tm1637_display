# SPDX-FileCopyrightText: Copyright (c) 2023 Neradoc
#
# SPDX-License-Identifier: Unlicense

"""
4-digits 7-segments display with default order.
"""

import time
import board
from tm1637_display import TM1637Display

display = TM1637Display(board.GP13, board.GP12, length=4, digit_order=(0, 1, 2, 3))

message = "    3141592653589793    "

while True:
    for i in range(5):
        display.print("0000")
        time.sleep(0.1)
        display.print("    ")
        time.sleep(0.1)

    for pos in range(len(message) - 4):
        display.print(message[pos : pos + 4])
        time.sleep(0.2)

    for i in range(0, 10000, 7):
        display.print(f"{i:4}")
    display.print(9999)

    time.sleep(0.2)
