'''
Exercises regarding control structures.
The following exercises should be solved with loops, match case and
if-else conditions ONLY! Comprehensions are NOT part of this exercise.

Author: RCH
Date: 25.11.2024
'''

import random as rd
from operator import length_hint

# given is the following list numbers
nlh = rd.randrange(1,100)
rnd = rd.choices(range(1,100), k=nlh) + rd.choices(range(100,255), k=255-nlh) + [randrange(256,300)]
rd.shuffle(rnd)
numbers = rnd.copy()

# advanced: do all exercises with the 2d list numbers_ii
numbers_ii = [[rnd.pop() for _ in range(16)] for _ in range(16)]

# Exercise 1:
'''
find the largest number in numbers with for loops and remove it,
if it is at the last position. Do the remove in the else clause of the for loop. WHY???
'''


# Exercise 2:
'''replace all values <100 with 0.'''


# Exercise 3:
'''find the position of the largest number.'''


# Exercise 4:
'''write all numbers != 0 up to the position of the largest number into a new list.'''


# Exercise 5:
'''
count the number of remaining numbers for each decade with match-case statement.
That means, count the number of numbers in ranges:
100 - 125, 126 - 150, 151 - 175, 176 - 200, >200 
'''

