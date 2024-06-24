Quick and dirty utility to look for one or two byte integers being compared to some other value in code.bin or .cro files.

Enter the integer you're looking for (in dec), then select the target binary file. When the search completes, the user will be prompted to save a text file. This file contains two lists. The first is all the occurences of the given integer that is written as is (e.g. 800 will return every address that has 0x20 03). This will have MANY false positives.

Sometimes there will a middle list if you are looking for a two-byte value. This will only pop up if the value in hex is either 0ZZ0 or ZZ00 (in these cases, the game can call a bitshifted cmp function in a single line).

The final list contains all the instances where the stated integer was compared via cmp (if one byte) or by sub followed by subs (if two bytes). This will often return no results at all.
