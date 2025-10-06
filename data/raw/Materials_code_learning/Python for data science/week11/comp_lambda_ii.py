#!/usr/bin/env python3

# Given are the first hundred words of the lorem ipsum text.
# Cont the occurence of each character (case insensitive) for the whole text.
# The variable 'chars' provides a list of all possible lower case characters.
# And the method count of a str object counts the number of occurrence for a 
# particular object.

import string
chars = string.ascii_lowercase

lorem = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
sed diam voluptua. At vero eos et accusam et justo duo dolores et ea
rebum. Stet clita gubergren, no sea takimata sanctus est Lorem ipsum dolor
sit amet."""

# Task 1: use the map function to apply a lambda function for counting all
# characters in the text.
count1 = {}
count1 = dict(map( ...FILL HERE... ))

print(count1)
print(count1["e"])


# Task 2: solve the same problem by means of a dictionary comprehension.
count2 = {}
count2 = { ...FILL HERE... }

print(count2)
print(count2["e"])




# The result will be:
# ~~~~~~~~~~~~~~~~~~~~
# {'a': 21, 'b': 3, 'c': 6, 'd': 12, 'e': 28, 'f': 0, 'g': 4, 'h': 0, 'i': 15,
# 'j': 1, 'k': 1, 'l': 9, 'm': 16, 'n': 10, 'o': 21, 'p': 5, 'q': 1, 'r': 16,
# 's': 17, 't': 25, 'u': 15, 'v': 3, 'w': 0, 'x': 0, 'y': 2, 'z': 0}
#
# 28
