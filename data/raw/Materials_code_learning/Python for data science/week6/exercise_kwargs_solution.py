

#%% Exercise arbitrary key word arguments (**kwargs)
'''
Write a function that accepts an arbitrary number of keyword arguments.
The function should number each key-value pair and print it in the following format:
1: keyword -> value
2: keyword -> value
...
n: keyword -> value

Solutions a), b), c), d)
'''

def print_numbered_kwargs(**kwargs):
    for ind, (key, value) in enumerate(kwargs.items()):
        print_string = "{}: ".format(str(ind)) + str(key) + " -> " + str(value)
        print(print_string)

#%% a) Test what happens if you pass key word arguments in the format your_function(a=2, b="hello")
print_numbered_kwargs(a=2, b="hello")

'''
0: a -> 2
1: b -> hello
'''

#%% b) Test what happens if you pass an positional argument
print_numbered_kwargs("hello")

# -> TypeError: print_numbered_kwargs() takes 0 positional arguments but 1 was given

#%% c) Test what happens if you pass key word arguments as a dictionary {"a":2, "b": "hello"}

my_dict = {"a":2,"b":"hello"}
print_numbered_kwargs(my_dict)

# -> TypeError: print_numbered_kwargs() takes 0 positional arguments but 1 was given
# The dictionary is interpreted as a positional argument!

#%% d) Use the unpack-operator (**) in the call of the function to pass the keyword arguments formatted as a dictionary

my_dict = {"a":2,"b":"hello"}
print_numbered_kwargs(**my_dict)




