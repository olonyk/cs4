# cs4
### Todo:
+ Speed
   + Implement new iteration sequence.
+ Default settings.
   + Add reset options.
   + Put more stuff in settings file.
+ Minor addons
   + Implement minimum cluster size.
   + Remove or extend CSV-support.
   + Fix titles of windows.
   + Change the term "sex" to "gender".
+ Add progress bar.

### Done
| Item        | Subitem           | Date  |
| ------------- |-------------| -----|
| Export window| Table | 180131 |
|              | Graph | 180131 |
|              | Export button | 180131 |
|              | Sort table by occurance | 180131 |
|              | Meta data frame | 180131 |
| Implement format fans|  | 180201 |
| Default settings| The default value should be 5 vs. 1 2 | 180201 |
| Minor addons| Import by pressing `cmd+i` | 180209 |
|  | Slim imports by using precise imports (Compiled app before: 125.7 MB, After: 125.7 MB). | 180208 |
|  | Add option to view output log.| 180209 |
| Distribution | Figure out how to make a standalone executable | 180205 |


### Known bugs
+ After importing and running data once, without error, a second import and run lead to the following error message: `TypeError: ufunc 'isfinite' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''`.
+ Importing .xlsx leads to `UserWarning: Unknown extension is not supported and will be removed`.
+ Sometimes when scrolling is preformed the following error occurs: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`.