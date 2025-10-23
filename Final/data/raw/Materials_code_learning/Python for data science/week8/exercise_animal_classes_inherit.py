'''
Exercise Animals Inheritance:
Use the file animals.csv to read information about animals.

Part a)
Produce a class structure where Dog, Cat and Snake are implemented as child classes of a base class Animal. Create the object variables in the base class,
along with a method 'print_basic_information', which prints 'type' and 'name' to the console.
In each child class, use the base class constructor with 'super' and add an additional method 'speak', specific to that child class.
In each child class, add an additional method where you return the sum of the object variables 'age' and 'legs'.

For each element in the animals.csv, create an object of the corresponding subclass,
let it print basic information (method from 'Animal'), let it speak (method from child class) and get the sum of 'age' and 'legs' as a return value.

Part b)
Often, there are many different solutions how one can solve a particular task. Ideas like code readability and avoiding code duplication
become more important in more complex applications. Do you find a way to reduce code duplication in the structure of part a)?

Part c)
Override the 'print_basic_information' method in the child class Dog by using the class name as a parameter
instead of self.animal_type. You can access the name of the class by self.__class__.__name__
'''

#%%  Base Class


class ...FILL HERE...:

    def __init__(self, animal_type, name, age, weight, legs):
        self.animal_type = animal_type
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs

    ...FILL HERE...


#%%  Child Classes

class Dog(...FILL HERE...):


    def __init__(self, animal_type, name, age, weight, legs):
        ...FILL HERE...

    ...FILL HERE...

class Cat():

    ...FILL HERE...

class Snake():

    ...FILL HERE...


#%% solution with file loop
obj_list = []
with open('./animals.csv') as f:
    for line in f.readlines()[1:]:
        animal_type = line.split(", ")[0]
        name = line.split(", ")[1]
        age = int(line.split(", ")[2])
        weight = int(line.split(", ")[3])
        legs = int(line.split(", ")[4])
        # create objects based on animal_type
        if ...FILL HERE...:
        ...FILL HERE...
        # add objects to obj_list
        obj_list.append(obj)

for elem in obj_list:
    print("--\n")
    elem.print_basic_information()
    elem.speak()
    c_sum = elem.sum_of_age_and_legs()
    print(c_sum)
