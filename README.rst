Introduction
============


.. image:: https://readthedocs.org/projects/tm1637-display-for-circuitpython/badge/?version=latest
    :target: https://tm1637-display-for-circuitpython.readthedocs.io/
    :alt: Documentation Status


.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/Neradoc/CircuitPython_tm1637_display/workflows/Build%20CI/badge.svg
    :target: https://github.com/Neradoc/CircuitPython_tm1637_display/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Driver for the TM1637 display.

Protocol decoded from the Arduino library: https://github.com/avishorp/TM1637

.. image:: images/photo.jpg
    :alt: Picture of a 6 digits 4-segment display

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install tm1637_display

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import board
    from tm1637_display import TM1637Display

    display = TM1637Display(board.SCL, board.SDA, length=6)
    display.print("HELLO.")

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://tm1637-display-for-circuitpython.readthedocs.io//>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/Neradoc/CircuitPython_tm1637_display/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
