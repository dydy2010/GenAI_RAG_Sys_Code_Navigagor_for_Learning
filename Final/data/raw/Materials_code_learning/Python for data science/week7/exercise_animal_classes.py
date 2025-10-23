'''
Exercise Animals:
Use the file animals.txt to read information about animals.

Part a)
For each animal, print "Hi, I'm a {animal_type} and my name is {name}!"
Solve the exercise by writing a class 'Animal' and adding a method allowing to print the requested string. Note that it is not necessary for this task, to differentiate between animal types!
'''

print("Part a): \n\n")

class Animal():

    def __init__(self, animal_type, name, age, weight, legs):
        self.animal_type = animal_type
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs

    def __str__(self):
        return f"Hi, I'm a {self.animal_type} and my name is {self.name}"



with open('/Users/dongyuangao/Library/CloudStorage/OneDrive-Personal/文档/学业/硕士hslu/Lectures Lessons Subjects/Python for data science/w7 oop/animals.csv') as f:
    for line in f.readlines()[1:]:
        parts=line.strip().split(",")
        animal_type = parts[0]
        name = parts[1]
        age = int(parts[2])
        weight = int(parts[3])
        legs = int(parts[4])
        #create objects
        obj = Animal(animal_type, name, age, weight, legs)
        print(obj)

'''
Part b)
Now we are interested in the various sounds the animal types make.
Write a separate class for each animal type. Provide a method "speak", which depending on the animal type prints different sounds.
'''

print("\n\nPart b): \n\n")
class Dog():

    def __init__(self, name, age, weight, legs):
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs
    def __str__(self):
        return f"Hi, I'm {self.name} and I say Woof"



class Cat():
    def __init__(self, name, age, weight, legs):
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs
    def __str__(self):
        return f"Hi, I'm {self.name} and I say Miao"


class Snake():
    def __init__(self, name, age, weight, legs):
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs
    def __str__(self):
        return f"Hi, I'm {self.name} and I say Pss"


#%% solution with file loop
obj_list=[]
with open('/Users/dongyuangao/Library/CloudStorage/OneDrive-Personal/文档/学业/硕士hslu/Lectures Lessons Subjects/Python for data science/w7 oop/animals.csv') as f1:
    for line in f1.readlines()[1:]:
        animal_data=line.strip().split(",")
        animal_type=animal_data[0]
        name=animal_data[1]
        age=int(animal_data[2])
        weight=int(animal_data[3])
        legs=int(animal_data[4])
        if animal_type=="dog":
            obj=Dog(name,age,weight,legs)
            print(obj)
        elif animal_type == "cat":
            obj = Cat(name, age, weight, legs)
            print(obj)

        elif animal_type == "snake":
            obj = Snake(name, age, weight, legs)
            print(obj)

"""For solving optimization problems, you write a class named Cylinder with the following content:
• parameters:
• float diameter (meter)
• float height (meter)
• bool empty -> this is by default true (optional parameter)

• object variables:
• diameter: represents objects diameter
• height: represents objects height
• empty: represents if the cylinder is empty
• level: represents the current fill level of the cylinder in percentage 0 .. 100"""

"""• methods:
• fill:
• sets the variable empty to false
• sets the level to 100
• returns true if it was empty before; else false.
• release:
• reduces the level by 10
• sets the variable empty to true if the level is 0 after reduction
• returns false if the level was < 10 before reduction; else true
• weight:
• returns the weight of the content: assuming a density of 1 kg/0.001 m^3
Generate few cylinder objects and experiment with the functions."""
import math
class Cylinder:
    def __init__(self, diameter, height, level,empty=True):
        self.diameter=diameter
        self.height=height
        self.empty=empty
        self.level=level


    def fill(self):
        if empty==True:
            x=1
        empty=False
        level=100
        if x==1:
            return True
        else:
            return False

    def release(self):
        if level<10:
            y=1
        level=-10
        if level==0:
            empty= True
        elif y==1:
            return True
        else:
            return False
    def weight(self):
        weight=self.diameter*math.pi*self.level
        return weight
obj=Cylinder(diameter=2, height=2, level=5, empty=True)
print(obj.weight())



