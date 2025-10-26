#!/usr/bin/env python3

# Different problems are solved with for-loops. Review each for-loop solution and 
# solve the problem with list comprehension or map function, as described in the
# task description.

# the following lists are given for all problems:
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
primes = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23]

# Task 1: copy all even elements from 'nums' into a new list.
print("\n---- Task 1 ----")
my_list = []
for n in nums:
  if not n%2:
    my_list.append(n)
print(f"for loop: {my_list=}")


# solution with list comprehension:
my_list=[]
my_list_1 = [i for i in nums if not i%2]
print(f"comprehension: my_list {my_list_1}")


# Task 2: calculate the square of each element in the list 'nums'.
print("\n---- Task 2 ----")
my_list = []
for n in nums:
  my_list.append(n*n)
print(f"for loop: {my_list=}")

# solution with list comprehension:
my_list = []
my_list = [i**2 for i in nums]
print(f"comprehension: my list = {my_list}")


# Task 3: calculate the square of each element in the list 'nums' by applying
# a lambda function on the list (using map function).
print("\n---- Task 3 ----")
my_list = []
for n in nums:
  my_list.append(n*n)
print(f"for loop: {my_list=}")

# solution with list comprehension:
my_list = list(map(lambda x:x*x, nums))
print(f"lambda: my_list {my_list}")

help("map")## if cannot find, see ultimate cheat sheet


# Task 4: create nested lists comprising all lower prime numbers up to the 
# given number in 'nums'.
print("\n---- Task 4 ----")
my_list = []
for n in nums:
  p_list = []
  for p in primes:
    if p <= n:
      p_list.append(p)
  my_list.append(p_list)
print(f"for loop: {my_list=}")

# solution with list comprehension:
my_list = []
my_list = [ [i for i in primes if i <= x] for x in nums]
print(f"comprehension: my_list {my_list}")

