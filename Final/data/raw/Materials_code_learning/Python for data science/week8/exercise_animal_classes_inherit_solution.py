'''
Exercise Animals Inheritance:
Use the file animals.txt to read information about animals.

Part a)
Build a code structure where classes Dog, Cat and Snake are implemented as child classes of a base class Animal. Create the object variables in the base class, along with a method 'print_basic_information', which prints 'type' and 'name' to the console.
In each child class, use the base class constructor with 'super' and add an additional method 'speak', specific to that child class.
In each child class, add an additional method where you return the sum of the object variables 'age' and 'legs'.

For each elem in the animals.txt, create an object of the corresponding subclass, let it print basic information (method from 'Animal'), let it speak (method from child class) and get the sum of 'age' and 'legs' as a return value.
'''

print("Part a): \n\n")
class Animal():

    def __init__(self, animal_type, name, age, weight, legs):
        self.animal_type = animal_type
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs

    def print_basic_information(self):
        print("Hi, I'm a {} and my name is {}!".format(self.animal_type, self.name))


class Dog(Animal):

    def __init__(self, animal_type, name, age, weight, legs):
        super().__init__(animal_type, name, age, weight, legs)

    def speak(self):
        print("Wuff, wuff!")

    def sum_of_age_and_legs(self):
        value = self.age + self.legs
        return value

class Cat(Animal):

    def __init__(self, animal_type, name, age, weight, legs):
        super().__init__(animal_type, name, age, weight, legs)

    def speak(self):
        print("Miaou!")

    def sum_of_age_and_legs(self):
        value = self.age + self.legs
        return value


class Snake(Animal):

    def __init__(self, animal_type, name, age, weight, legs):
        super().__init__(animal_type, name, age, weight, legs)

    def speak(self):
        print("SSsshh, SSsshh!")

    def sum_of_age_and_legs(self):
        value = self.age + self.legs
        return value


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
            obj = Dog(animal_type, name, age, weight, legs)
            obj_list.append(obj)
        if animal_type == 'cat':
            obj = Cat(animal_type, name, age, weight, legs)
            obj_list.append(obj)
        if animal_type == 'snake':
            obj = Snake(animal_type, name, age, weight, legs)
            obj_list.append(obj)

for elem in obj_list:
    print("--\n")
    elem.print_basic_information()
    elem.speak()
    c_sum = elem.sum_of_age_and_legs()
    print(c_sum)

'''
Part b) and c)
Often there are many different solutions how one can solve a particular task. Ideas like code readability and avoiding code duplication become more important in more complex applications. Do you find a way to reduce code duplication in the structure of part a)?
'''

print("\n\n")
print("Part b) and c): \n\n")
print("Although the method 'sum_of_age_and_legs' uses object variables, there is no specific dependence to the child class itself. Hence, in that case, you can implement the method as a base class method. Verify that the example below produces the same result and observe that child classes only provide specific animal type methods.")

class Animal():

    def __init__(self, animal_type, name, age, weight, legs):
        self.animal_type = animal_type
        self.name = name
        self.age = age
        self.weight = weight
        self.legs = legs

    def print_basic_information(self):
        print("Hi, I'm a {} and my name is {}!".format(self.animal_type, self.name))

    def sum_of_age_and_legs(self):
        value = self.age + self.legs
        return value


class Dog(Animal):

    def __init__(self, animal_type, name, age, weight, legs):
        super().__init__(animal_type, name, age, weight, legs)

    def speak(self):
        print("Wuff, wuff!")

    def print_basic_information(self):
        print("Hi, I'm a {} and my name is {}!".format(self.__class__.__name__, self.name))

class Cat(Animal):

    def __init__(self, animal_type, name, age, weight, legs):
        super().__init__(animal_type, name, age, weight, legs)

    def speak(self):
        print("Miaou!")


class Snake(Animal):

    def __init__(self, animal_type, name, age, weight, legs):
        super().__init__(animal_type, name, age, weight, legs)

    def speak(self):
        print("SSsshh, SSsshh!")


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
            obj = Dog(animal_type, name, age, weight, legs)
            obj_list.append(obj)
        if animal_type == 'cat':
            obj = Cat(animal_type, name, age, weight, legs)
            obj_list.append(obj)
        if animal_type == 'snake':
            obj = Snake(animal_type, name, age, weight, legs)
            obj_list.append(obj)

for elem in obj_list:
    print("--\n")
    elem.print_basic_information()
    elem.speak()
    c_sum = elem.sum_of_age_and_legs()
    print(c_sum)
