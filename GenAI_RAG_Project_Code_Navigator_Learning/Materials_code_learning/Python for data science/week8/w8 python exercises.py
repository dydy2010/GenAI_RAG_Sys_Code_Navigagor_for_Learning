"""Use the file animals.csv to read information about animals.
a) Produce a class structure where Dog, Cat and Snake are implemented as child classes of a base class Animal. Create the
object variables in the base class, along with a method 'print_basic_information', which prints 'type' and 'name' to the console.
• In each child class, use the base class constructor with 'super' and add an additional
method 'speak', specific to that child class.
• In each child class, add an additional method where you return the sum of the object
variables 'age' and 'legs'. For each element in the animals.csv, create an object of the
corresponding subclass, let it print basic information (method from 'Animal'), let it
speak (method from child class) and get the sum of 'age' and 'legs' as a return value.
b) Often, there are many different solutions how one can solve a particular task. Ideas like
code readability and avoiding code duplication become more important in more complex
applications. Do you find a way to reduce code duplication in the structure of part a)?
c) Override the 'print_basic_information' method in the child class Dog by using the class
name as a parameter instead of self.animal_type. You can access the name of the class
by: self.__class__.__name__
"""


class Animal:
    def __init__(self,animal_type,name,age,weight,legs):
        self.name=name
        self.age=age
        self.legs=legs
        self.weight=weight
        self.type=animal_type
    def print_basic_information(self):
        return f"Name: {self.name}, Type:{self.type}"

class Snake(Animal):
    def __init__(self,animal_type, name, age, weight, legs):
        super(). __init__(animal_type,name,age, weight, legs)
    def speak(self):
        return f"I am {self.name}, and I Psss"
    def count(self):
        return f"legs of {self.name} is{self.legs}"
    def print_basic_information(self):
        return super().print_basic_information()
    def print_basic_information(self):
        return super().print_basic_information()

class Dog(Animal):
    def __init__(self, animal_type, name, age, weight, legs):
        super(). __init__(animal_type,name,age, weight, legs)
    def speak(self):
        return f"I am {self.name}, and I Woof"
    def count(self):
        return f"legs of {self.name} is{self.legs}"
    def print_basic_information(self):
        return super().print_basic_information()

class Cat(Animal):
    def __init__(self, animal_type,name, age, weight, legs):
        super(). __init__(animal_type,name,age, weight, legs)
    def speak(self):
        return f"I am {self.name}, and I Miao"
    def count(self):
        return f"legs of {self.name} is{self.legs}"
    def print_basic_information(self):
        return super().print_basic_information()

###read file and get data
with open("/Users/dongyuangao/Library/CloudStorage/OneDrive-Personal/文档/学业/硕士hslu/Lectures Lessons Subjects/Python for data science/w8/animals.csv",encoding="utf-8") as f:
    next(f)  # Skip header if present
    for line in f:
        print("Reading line:", line)
        lst=line.strip().split(',')
        animal_type = lst[0]
        name = lst[1]
        age = lst[2]
        weight = lst[3]
        legs = lst[4]
        if animal_type=='dog':
            obj = Dog(animal_type,name, age, weight, legs)
            print(obj.speak(),obj.count(),obj.print_basic_information())
        elif lst[0]=='cat':
            obj = Cat(animal_type,name, age, weight, legs)
            print(obj.speak(), obj.count(),obj.print_basic_information())
        elif lst[0]=='snake':
            obj = Snake(animal_type,name, age, weight, legs)
            print(obj.speak(), obj.count(),obj.print_basic_information())
        else:
            continue


"""Write a new class called 'MyStr' that inherits from str. 
In addition 'MyStr' provides a function called bi_rev() that returns every 2nd character in reverse order, 
beginning by the last character (i.e. it prints the characters n, n-2, n-4, ...).
You can test it with the following code:

txt1 = MyStr('z!me ngosdf nsjir zbgocjx aewh!T')
print(txt1.bi_rev())
The correct result is obvious ;-)"""

class MyStr(str):
    ###self.str=str

    def bi_rev(self):
        nospace=self.replace(" ","")
        str_rev = nospace[::-1]
        str_rev_step2 = str_rev[1::2]
        return str_rev_step2[::-1]



txt1 = MyStr('z!me ngosdf nsjir zbgocjx aewh!T')
print(txt1.bi_rev())


"""Do again recursive exercise
Given is a list with an arbitrary number of nested lists. All nested lists may comprise nested lists too. We assume you know that a specific element must be somewere within the nested lists but you do not know at which position nor in which nested list.
Write a recursive function that returns the position of a specific element e within a list l with a sequence of numbers (e.g. a list) where each element refers to the next sublist containing the element e or the position of the element itself. The function returns None if the element is not in the list nor in any sublist.

Note:
using the function type(x) in a boolean statement like type(x)==list you can check if a list element x is of type list."""