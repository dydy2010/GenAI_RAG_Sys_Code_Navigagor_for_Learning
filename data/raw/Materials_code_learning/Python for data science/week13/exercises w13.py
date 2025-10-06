print(list(range(6)))
print(list(range(1,6)))

"""Program a function strselect that returns all strings of a list having the letter passed to the parameter key at 
the given position p. Catch the IndexError that is raised if the position p is out of index range 
and print the error message "string index out of range" instead."""
  


def strselect(lst,key,position):
   for i in lst:
       try:
           i[position] == key
       except IndexError:
           print("string index out of range")
       else:
           if key == i[position]:
               print(i)

print(strselect(["hello", "of", "help", "world"], key="l", position=2))

"""
#possible function call:
strselect(["hello", "of", "help", "world"], key = "l", p = 2)

#output:
'hello'
'string index out of range'
'help' 

Extension:
Create yourbeeingrror type (class inheriting from Exception) and test it with a suitable example, 
which should raise your error in case of the letter provided by key never beeing in the given position p.
"""

