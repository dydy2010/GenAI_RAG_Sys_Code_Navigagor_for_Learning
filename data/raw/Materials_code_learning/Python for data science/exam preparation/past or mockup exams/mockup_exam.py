"""
Mockup Exam PDS HS 2024
Andreas Melillo, Ramon Christen

Important Information:
Write all of your code in this file!
For exam submission, upload it to ILIAS before the deadline.
"""

#%% TASK 1:
# subtask 1.1
'''
TODO: Import the module 'module_one' and use it to create one hundred random numbers between 1 and 10, save them in a list.
import random

def create_random_numbers():
    return [random.randint(1,10) for elem in range(100)]

'''
from module_one import create_random_numbers
x=create_random_numbers()
lst=x


# subtask 1.2
'''
TODO: Use list comprehension to add 4 to every elem in the list, name the new list 'updated_list'.

NOTE: In case you could not solve 1.1, use [1,2,3,4,5,6,7,8,9]
NOTE: In case you cannot solve 1.2 using list comprehension but in some other way, you still get points
'''
updated_list = [elem+4 for elem in lst]
    

# subtask 1.3
'''
TODO: Create a dictionary which contains as
keys:
- all elements from 'updated_list', which are < 10
values:
- their position in the list 'updated_list'.

NOTE: In case you could not solve 1.2, use [11,22,33,4,5,60,7,8,9] as the 'updated_list'
'''
dictionary_1 = {k:v for (v,k) in enumerate(updated_list) if k<10}
#%% TASK 2:
# subtask 2.1
'''
TODO: Create a class ExamClass with the following specification:

class variables:
  - _obj_counter = 0

object variables:
 -> none

object methods:
  - _add_one_to_obj_counter
  - _set_obj_id

TODO: Implement the object method '_add_one_to_obj_counter' such that when called, 1 is added to the class variable _obj_counter.
TODO: Execute this method in the __init__ method of ExamClass.
TODO: Implement the object method '_set_obj_id' such that :
 1) An obj variable 'self._obj_id' is created
 2) The value of 'self._obj_id is set to the current class variable _obj_counter
TODO: Execute this method in the __init__ method of ExamClass, after the execution of '_add_one_to_obj_counter'.
'''
Class ExamClass:
    _obj_counter=0
    def __init__(self):
        self.add_one_to_obj_counter()
        self._set_obj_id()
    def add_one_to_obj_counter():
        ExamClass._obj_counter+=1
    def _set_obj_id(self):
        self._obj_id=_ExamClass._obj_counter
        


        
        
# subtask 2.2
'''
TODO: Add an object method 'print_obj_id', that prints the variable 'obj_id' to the console.
'''
def print_obj_id(self):
    print(self._obj_id)
# subtask 2.3
'''
TODO: Instantiate 3 objects of ExamClass and store them in a list.
TODO: Use a for loop to call the 'print_obj_id' for each object.
'''
x=ExamClass()
y=ExamClass()
z=ExamClass()
lst=[x,y,z]

for i in lst:
    i.print_obj_id()
