#!/bin/sh

printf '[ ] Cleaning workspace'
rm -rf build dist *.spec
printf '\r[x]\n'

printf '[ ] Building distributable .app'
pyinstaller --log-level ERROR --clean --icon=src/pyinstaller-hooks/icon.icns --windowed --add-data="src/resources/settings/settings.json:src/resources/settings/" --hidden-import scipy._lib.messagestream --additional-hooks-dir src/pyinstaller-hooks/ --runtime-hook src/pyinstaller-hooks/pyi_rth__tkinter.py CoreSound4.py
printf '\r[x]\n'

printf '[ ] Copying necessary but missed files'
cp src/pyinstaller-hooks/Tcl dist/CoreSound4.app/Contents/MacOS/
cp src/pyinstaller-hooks/Tcl dist/CoreSound4/
cp src/pyinstaller-hooks/Tk dist/CoreSound4.app/Contents/MacOS/
cp src/pyinstaller-hooks/Tk dist/CoreSound4/
printf '\r[x]\n'

printf '[x] If all boxes are ticked you are ready to roll!\n'
