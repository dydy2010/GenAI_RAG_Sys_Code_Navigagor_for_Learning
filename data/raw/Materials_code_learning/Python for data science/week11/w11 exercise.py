"""
Function Input Assert for Libraries (Exercise)

Provide a function fuzz_sum in a new module called: exerc_lib.py
The function calculates a proportional sum (fuzzy hat-function) under a moving window along a passed data series. In fact, the
function takes three parameters:
• Data: Dict[str, str, List[float | int]] e.g. {‘name’:’test’, ‘loc’:’north’, ‘x’:[2, 3.9, 8, 5, 1.2]}
• Hat_coeff: List[float] e.g. coeff=[0.1, 0.55, 1, 0.55, 0.1]
• W_length: int e.g. w_length=5
Thereby, the hat-coefficients and the window length should be optional.
"""
from random import random


### How do you have to test the parameters passed to the function?
def fuzz_sum(Data, Hat_coeff, W_length):
    if not isinstance(Data, dict):
        raise TypeError("Data is not a dictionary.")
    if not isinstance(Hat_coeff, list):
        raise TypeError("Data is not a list")
    if not isinstance(W_length,int):
        raise TypeError("Data is not an integer")
    else:
        return "the parameters are okay"

a = {
    "first": "er",
    "second": "x",
    "third": 3,
    "fourth": [31, "q", "y"]
}
b=[1.9,8.2,9.8,3.0]
c= 9
test1=fuzz_sum(a,b,c)
print(test1)

a=[1:'er',2:'x',3:3,4:[31,"q","y"]]
b=[1.9,8.2,9.8,3.0]
c= 9
test2=fuzz_sum(a,b,c)
print(test2)




### lambda function practice
x  = [1, 2, 3, 4, 5]
x2 = list(map(lambda i: i**2, x))
print(x2)

### short hand practice
x3=[i**2 for i in x]
print(x3)

"""exercise SW11:
Given is a series my_num of 330 arbitrary numbers. 
The series is composed by 22 independent variables that you have to separate again.
part 2：
Use list comprehension to separate the 22 independent variables into sublists 
such that you can assign separate names and create a data frame.
The goal is to have a list of lists for all the independent variables like:
1 my_vars = [[a1, a2, a3, ... , a15], [b1, b2, b3, ... , b15], ... , [v1, v2, v3, ... , v15]]
"""
from random import random
my_num=[]
for i in range(330):
    my_num+=[int(random()*1000)]
my_vars=[]
for i in range(0,330,15):
    my_vars+=[my_num[i:i+15]]

print(my_vars)
len(my_vars)### to see if in total 22 lists in the list
print(*my_vars, sep = '\n') # *is to unpack the list


### list comprehension: nested practice, apply ll//10, simple return and nested
ll = [[1000, 200, 30], [22, 33], [555, 333, 222, 111]]
ll_integer_div_10_simple = [y//10 for sublist in ll for y in sublist] # 紧随其后的第一个for loop是第一个for loop
print(ll_integer_div_10_simple)

ll_integer_div_10_nested = [[y//10 for y in sublist ] for sublist in ll ] # 紧随其后的第一个for loop是第二个for loop
print(ll_integer_div_10_nested)