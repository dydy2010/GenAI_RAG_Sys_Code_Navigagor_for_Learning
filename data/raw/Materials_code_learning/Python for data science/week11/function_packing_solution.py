'''
Exercises regarding functions and packing operators.

Author: RCH
Date: 25.11.2024
'''
import random as rd

# given is the following function
def rnd_number(n=1, range=range(1,100), duplications=False):
    '''
    random number generator. This function returns a list of n random numbers being
    within the given range and possible duplicates if duplications is True.
    :param n: number of random numbers to generate
    :param range: numerical range for random numbers
    :param duplications: flag if duplications are allowed
    :return: list of random numbers with or without duplicates
    '''
    rnd_list = []
    if(duplications and n>len(range)):
        return "ERROR: too many elements requested."
    elif(duplications):
        rnd_list = rd.choices(range, k=n)
    else:
        rnd_list = rd.sample(range, k=n)
    return rnd_list


# Exercise 1:
'''
write a function that returns a list of n random numbers in ascending or descending order.
Call the given function to generate the list and return the sorted list.
'''
def sort_nr_list(n=10, order=0):
    '''
    returns a list with n random numbers sorted according to order
    :param n: number of elements in the list
    :param order: order of elements: 0 descending, 1 ascending.
    :return: list with n random numbers sorted according to order
    '''
    return sorted(rnd_number(n), reverse=order)

# Exercise 2:
'''
write a function that accepts arbitrary number of integer elements. The functions
calculates and returns the average of the difference of all subsequent elements.
Annotate the types to all interface variables more clarity.
'''
def step_avg(*n: int) -> int:
    '''
    calculates the average gap between all numbers
    :param n: numbers for calculating average gap
    :return: average gap between all numbers n
    '''
    sum = 0
    if len(n) >= 2:
        for i in range(1,len(n)):
            sum += n[i]-n[i-1]
        return(sum/(len(n)-1))

# Exercise 3:
'''
create two lists containing 10 sub-lists of random numbers.
Each of the two contains 10 sub-lists with n=10,11,12,13,14...19 elements.
One list is sorted in ascending order and the other in descending order.
'''
l0 = []
l1 = []
for i in range(10,20):
    l0.append(sort_nr_list(i, 0))
    l1.append(sort_nr_list(i, 1))

# Exercise 4:
'''
calculate the mean of the average element distance among all ascending and descending 
sorted lists. Use the function from Exercise 2.
Are the two absolute averages comparable?
'''
avg0 = avg1 = 0
for i in range(len(l0)):
    avg0 += step_avg(*l0[i])/len(l0)
    avg1 += step_avg(*l1[i])/len(l1)

print(f'{avg0=}', f'{avg1=}')