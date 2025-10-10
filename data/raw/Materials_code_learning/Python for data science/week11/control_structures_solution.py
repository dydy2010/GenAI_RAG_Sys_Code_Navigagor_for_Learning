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
rnd = rd.choices(range(1,100), k=nlh) + rd.choices(range(100,255), k=255-nlh) + [rd.randrange(256,300)]
rd.shuffle(rnd)
numbers = rnd.copy()

# advanced: do all exercises with the 2d list numbers_ii
numbers_ii = [[rnd.pop() for _ in range(16)] for _ in range(16)]

# Exercise 1:
'''
find the largest number in numbers with for loops and remove it,
if it is at the last position. Do the remove in the else clause of the for loop. WHY???
'''
for i in numbers[:-1]:
    if i == max(numbers):
        break
else:
    numbers.pop()

# advanced:
for l in numbers_ii:
    for ll in l[:-1]:
        if ll == max(l):
            break
    else:
        if l == numbers_ii[-1]:
            ll.pop()


# Exercise 2:
'''replace all values <100 with 0.'''
for i in range(len(numbers)):
    if numbers[i] < 100:
        numbers[i] = 0

# advanced:
for i in range(len(numbers_ii)):
    for j in range(len(numbers_ii[i])):
        if numbers_ii[i][j] < 100:
            numbers_ii[i][j] = 0


# Exercise 3:
'''find the position of the largest number.'''
for i, j in enumerate(numbers):
    if j == max(numbers):
        break

# alternative solution:
n = 0
i = 0
for l in range(len(numbers)):
    if numbers[l] >n:
        i = l
        n = numbers[l]

# advanced:
max_i = 0
max_j = 0
max_n = 0
for i, l in enumerate(numbers_ii):
    for j, ll in enumerate(l):
        if ll >max_n:
            max_i, max_j = i, j


# Exercise 4:
'''write all numbers != 0 up to the position of the largest number into a new list.'''
k = 0
new_numbers = []
while k <= i:
    if numbers[k] != 0:
        new_numbers.append(numbers[k])
    k += 1

# advanced:
new_numbers_ii = []
for i in range(max_i + 1):
    for j in range(max_j + 1):
        if numbers_ii[i][j] != 0:
            new_numbers_ii += [numbers_ii[i][j]]


# Exercise 5:
'''
count the number of remaining numbers for each decade with match-case statement.
That means, count the number of numbers in ranges:
100 - 125, 126 - 150, 151 - 175, 176 - 200, >200 
Note: same solution for the simple and the advanced exercises.
'''
c1 = c2 = c3 = c4 = c5 = 0

for i in new_numbers:
    if i >= 100:        # not necessary since all values <100 were replaced by 0
        match i:
            case i if i <= 125:
                c1 += 1
            case i if i <= 150:
                c2 += 1
            case i if i <= 175:
                c3 += 1
            case i if i <= 200:
                c4 += 1
            case _:
                c5 += 1

print(f'{c1=}, {c2=}, {c3=}, {c4=}, {c5=}')

print(f'{len(new_numbers)=}')
print(f'{sum([c1, c2, c3, c4, c5])=}')

