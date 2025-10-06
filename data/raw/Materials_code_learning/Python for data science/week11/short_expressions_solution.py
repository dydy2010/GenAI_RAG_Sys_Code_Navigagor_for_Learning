
# %% List Comprehension

# Create a list containing the numbers from 11 to 26 using list comprehension and the range function.

mylist = [elem for elem in range(11,27)]

# Use conditional list comprehension to create a list 'even_list' containing each even number (%2 == 0) from your previous list

even_list = [elem for elem in mylist if elem%2 == 0]


# %% Lambda Expression

# Define a lambda expression which returns True if a number is divisible by 3 and false if not. Use 'expr if expr else expr' syntax of the conditional statement. For this time, give the function a name "divisible_by_3".

divisible_by_3 = lambda x: True if x%3==0 else False

# Use the defined lambda function to create a new list based on your 'even_list', containing only numbers divisible by 3

d_list = [elem for elem in even_list if divisible_by_3(elem)]

# %% Dict Comprehension

# Use lambda functions and dict comprehension to create a dictionary consisting of
# keys: numbers in 'even_list'
# values: whether 98729 is divisible by key (-> True) or not (-> False)

divisible_by_key = lambda key: True if 9878990%key==0 else False

mydict = {key:divisible_by_key(key) for key in even_list}
