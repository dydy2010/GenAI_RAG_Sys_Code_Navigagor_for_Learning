# task 1 using list comprehension
s = [1,2,3,4,11,22,33,44,111,222,333,444]
# goal:
# s_sorted = [[1,11,111], [2,22,222], [3,33,3331, [4,44,44411]

s_sorted = [[s[i::4]]for i in range(4)]
print(s_sorted)

# task 2
s = [1,11, 111,2,22,222,3,33,333,4,44,444]
# goal:
sasonted = [[1,11,111],[2,22,222],[3,33,3331,[4,44,4441]


"""ilias task w12
In data science, we often have the situation, that data appear in an unsorted order such as the following list:
my_list = [338, 693, 19, 144, 85, 958, 495, 218, 647, 50, 337, 869, 537, 477, 625, 31, 173, 795, 61, 257, 983, 415, 16, 112, 53]
However, a simple increasing or decreasing sort is not always meaningful.For instance, 
if you want to rate low values higher or only sort values below / above a certain threshold and keep others in the unsorted order.

Use the function sorted with lambda functions to sort my_list in two different ways:
1 sort my_list in increasing order while using the square for all values less than 30.
2 sort only values less than 100 and keep all others in original order after the sorted values.
e.g.[400, 60, 200, 7, 40, 300]  ->  [7, 40, 60, 400, 200, 300]
"""
# 1 sort my_list in increasing order while using the square for all values less than 30.
# solution task 1:
# [31, 50, 53, 61, 85, 112, 144, 173, 218, 16, 257, 337, 338, 19, 415, 477, 495, 537, 625, 647, 693, 795, 869, 958, 983]
my_list = [338, 693, 19, 144, 85, 958, 495, 218, 647, 50, 337, 869, 537, 477, 625, 31, 173, 795, 61, 257, 983, 415, 16, 112, 53]
sorted_list = sorted(my_list, key = lambda i:i**2 if i<30 else i)
print(sorted_list)

# task 2 sort only values less than 100 and keep all others in original order after the sorted values.
# solution task 2:
# [16, 19, 31, 50, 53, 61, 85, 338, 693, 144, 958, 495, 218, 647, 337, 869, 537, 477, 625, 173, 795, 257, 983, 415, 112]
my_list = [338, 693, 19, 144, 85, 958, 495, 218, 647, 50, 337, 869, 537, 477, 625, 31, 173, 795, 61, 257, 983, 415, 16, 112, 53]
sorted_list = sorted(my_list, key = lambda i: i if i<100 else i)
print(sorted_list)

"""w12 lias listed objects exercises
Frequently, it is useful to have data recordings or stream access in objects represented, 
especially if all are used in the same data analysis project.
Create 15 individual Stream objects in a list using list comprehension. 
To that, pass a unique random number in the range 1000 to 9999 (i.e. from range(1000, 9999)) 
to the id parameter of the Stream __init__ method.
Complete the following code and run it for testing. As result, it should output all given ids.
"""
# the class is template code
from random import sample
class Stream:
    def __init__(self, id):
        self.my_id = id

    def __repr__(self):
        return f"Stream obj: {self.my_id}"

stream_objects = [Stream(i) for i in sample(range(1000,9999),15) ] # TODO: create objects with list comprehension here.
print(*stream_objects, sep='\n')#*is unpacking the list



