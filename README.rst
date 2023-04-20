Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-tm1637-display/badge/?version=latest
    :target: https://circuitpython-tm1637-display.readthedocs.io/
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

.. image:: ../docs/_static/photo.jpg
    :alt: Picture of a 6 digits 4-segment display

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-tm1637-display/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-tm1637-display

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-tm1637-display

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-tm1637-display

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
API documentation for this library can be found on `Read the Docs <https://circuitpython-tm1637-display.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/Neradoc/CircuitPython_tm1637_display/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
