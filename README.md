# cs4
### Todo:
1. Export window.
   + Table. √
   + Graph. √
   + Export button. √
   + Sort table by occurance. √
   + Meta data frame. √
2. Implement format fans. √
3. Speed
   + Implement new iteration sequence.
4. Default settings.
   + The default value should be 5 vs. 1 2. √
   + Add reset options.
   + Put more stuff in settings file.
5. Minor addons
   + Implement minimum cluster size.
   + Remove or extend CSV-support.
   + Fix titles of windows.
   + Change the term "sex" to "gender".
   + Import by pressing `cmd + o`
6. Figure out how to make a standalone executable. √

### Known bugs
1. After importing and running data once, without error, a second import and run lead to the following error message: `TypeError: ufunc 'isfinite' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''`.
2. Importing .xlsx leads to `UserWarning: Unknown extension is not supported and will be removed`.
3. The file format `.xls`is not supportet.
4. Time estimate says -1 weeks.
5. Sometimes when scrolling is preformed the following error occurs: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`.