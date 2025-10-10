# %% read_file, loops, list comprehension

# %% loops and dict comprehension
# Create a list 'mylist' containing all whole numbers between 32 and 218, including the borders.

...FILL HERE...

# Create a void dictionary 'mydict'. Iterate over your list using a for loop togehter with 'enumerate' and fill your dictionary according to the following scheme: keys: positions of the numbers in list, values: actual number at this position

...FILL HERE...

# Repeat the task using dict-comprehension syntax.

...FILL HERE...

# Create a list with 100 random numbers between 1 and 100 (use package 'random'). Use dictionary comprehension to keep track of how many times (value) each present number (key) appears in the list.

import random
mylist = [random.randint(1, 100) for _ in range(100)]

counter_dict = ...FILL HERE...

# %% read_file, list comprehension

# Read File using with open(), loop over your file with 'for line in file', use line.rstrip to remove trailing characters.  comprehension to create a list 'lines' containing every line ind the document as an element. Loop ove

file_path = ...FILL HERE...

with ...FILL HERE...:
    for line in file:
        ...FILL HERE...

# Remove empty lines using a for loop by first counting occurrences (n) with list.count(elem) and then removing with list.remove(elem) n times

...FILL HERE...

# Repeat the task, but use list comprehension in the definition of 'lines' and to remove the empty lines

file_path = ...FILL HERE...
with open(file_path, "r") as file:
    lines = ...FILL HERE...
...FILL HERE...

# Use the comprehension syntax to calculate the number of occurrences of "ar" on each line. The line number can be used as a key.

counter = {...FILL HERE...}



