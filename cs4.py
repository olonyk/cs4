#!/usr/bin/python3.5
"""
    Usage:
        cs4.py gui
        cs4.py calc [--data=DATA_FILE]
"""
from docopt import docopt
from src.scripts.commands.calc_test import CalcTest
from src.scripts.gui.main_kernel import MainKernel

if __name__ == "__main__":
    args = docopt(__doc__)
    COMMAND = None
    if args["calc"]:
        COMMAND = CalcTest(args)
    if args["gui"]:
        COMMAND = MainKernel(args)
    if COMMAND:
        COMMAND.run()