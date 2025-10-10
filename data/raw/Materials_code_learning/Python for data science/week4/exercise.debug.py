###################
# Exercise 5
###################
"""
Write a Python program to guess a number between 1 to 10.
First: Use the predefined code block to create a random number
Second:
The user is prompted to enter a guess. If the guess is wrong a message
"to big" or "to small" is printed to the console and the prompt (user
input) appears again until the guess is correct. If the guess is correct, "Well guessed!" will be printed and the program ends.
Extension:
The number of trials should be prompted as well: "Well done - you have tried it 4 times!"
Try debug functions while writing code
"""

# Code block to create a random number
from random import randint

random_number = randint(1, 10)
# End code block to create a random number

guess_num = int(input("Guess a number between 1 and 10:"))
number_of_guesses = 1
while random_number != guess_num:
    if random_number > guess_num:
        print("the number is too small")
    else:
        print("the number is too big")
    guess_num = int(input("Next try:"))
    number_of_guesses = number_of_guesses + 1
print("Well guessed: the random number was correct!")
print("It took you:", number_of_guesses, " guesses.")

