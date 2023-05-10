# SPDX-FileCopyrightText: Copyright (c) 2023 Neradoc
#
# SPDX-License-Identifier: Unlicense

import time
import board
from tm1637_display import TM1637Display

display = TM1637Display(board.SCL, board.SDA, length=6, digit_order=(2, 1, 0, 5, 4, 3))
DELAY = 0.5

message = "      3141592653589793      "

while True:
    for i in range(5):
        display.print("000000")
        time.sleep(0.1)
        display.print("    ")
        time.sleep(0.1)

    for pos in range(len(message) - 6):
        display.print(message[pos : pos + 6])
        time.sleep(0.2)

    for i in range(0, 1_000_000, 7):
        display.print(f"{i:4}")
    display.print(9999)

    time.sleep(0.2)
