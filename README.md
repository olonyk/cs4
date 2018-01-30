# cs4
### Todo:
1. Export window.
   + Table. √
   + Graph. √
   + Export button. √
   + Sort table by occurance. √
   + Meta data frame. √
2. Implement format fans.
3. Speed
   + Implement new iteration sequence.
4. Default settings.
   + The default value should be 5 vs. 1 2. √
   + Add reset options.
   + Put more stuff in settings file.

### Known bugs
1. After importing and running data once, without error, a second import and run lead to the following error message: `TypeError: ufunc 'isfinite' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''`.
2. Importing .xlsx leads to `UserWarning: Unknown extension is not supported and will be removed`.