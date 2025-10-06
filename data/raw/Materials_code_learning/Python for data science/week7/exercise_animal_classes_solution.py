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

    def print_information(self):
        print("Hi, I'm a {} and my name is {}!".format(self.animal_type, self.name))
        pass

    def __str__(self):
        return "Hi, I'm a {} and my name is {}!".format(self.animal_type, self.name)

    def __repr__(self):
        return "Hello, I'm a {} and my name is {}!".format(self.animal_type, self.name)


#%% solution with file loop

with open('./animals.csv') as f:
    for line in f.readlines()[1:]:
        animal_type = line.split(", ")[0]
        name = line.split(", ")[1]
        age = int(line.split(", ")[2])
        weight = int(line.split(", ")[3])
        legs = int(line.split(", ")[4])
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

    def speak(self):
        print("Wuff, wuff!")

class Cat():

    def __init__(self, name, age, weight, legs):
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs

    def speak(self):
        print("Miaou!")

    def __str__(self):
        return "Hi, I'm a {} and my name is {}!".format(self.__class__.__name__, self.name)


class Snake():

    def __init__(self, name, age, weight, legs):
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs

    def speak(self):
        print("sss, sss!")


#%% solution with file loop
obj_list = []
with open('./animals.csv') as f:
    for line in f.readlines()[1:]:
        animal_type = line.split(", ")[0]
        name = line.split(", ")[1]
        age = int(line.split(", ")[2])
        weight = int(line.split(", ")[3])
        legs = int(line.split(", ")[4])
        #create objects
        if animal_type == 'dog':
            obj = Dog(name, age, weight, legs)
            obj_list.append(obj)
        if animal_type == 'cat':
            obj = Cat(name, age, weight, legs)
            obj_list.append(obj)
        if animal_type == 'snake':
            obj = Snake(name, age, weight, legs)
            obj_list.append(obj)

for elem in obj_list:
    elem.speak()
