
import string
chars = string.ascii_lowercase
lorem = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
sed diam voluptua. At vero eos et accusam et justo duo dolores et ea
rebum. Stet clita gubergren, no sea takimata sanctus est Lorem ipsum dolor
sit amet."""


# Task 1: use the map function to apply a lambda function for counting all
# characters in the text.
count1 = {}
count1 = dict(map(lambda x: (x, lorem.count(x)), chars))
print(count1)
print(count1["e"])

# Task 2: solve the same problem by means of a dictionary comprehension.
count2 = {}
count2 = {k:v for (k,v) in map(lambda x: (x, lorem.count(x)), chars)}

print(count2)
print(count2["e"])

