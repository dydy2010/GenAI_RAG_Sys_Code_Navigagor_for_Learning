#%% string manipulation, list comprehension, functions
# General hint: Check out the regular expressions package "re" in case you encounter problems of this kind. To focus on python basics, we do not use it in this exercise.

#%% Start
sentence = "Hello, I am the first sentence, I am happy and I am strong."

# Use str.split method to create a list of all elements separated by " "
# OUT: ['Hello,', 'I', 'am', 'the', 'first', 'sentence,', 'I', 'am', 'happy', 'and', 'I', 'am', 'strong.']

# Use list comprehension to add "__" to every entry of the word list

# OUT: ['Hello,__', 'I__', 'am__', 'the__', 'first__', 'sentence,__', 'I__', 'am__', 'happy__', 'and__', 'I__', 'am__', 'strong.__']

# Use str.replace to previously remove "," and "." to get a list of only the words

# OUT: ['Hello', 'I', 'am', 'the', 'first', 'sentence', 'I', 'am', 'happy', 'and', 'I', 'am', 'strong']

# Now you would like to keep punctuation marks as ',' and '.' as separate entries in the list
# Write a function 'keep_punctuation_word_list', which takes a sentence, extracts "," and "." from sub-strings and adds them to the list of words at the right position.

# OUT: ['Hello', ',', 'I', 'am', 'the', 'first', 'sentence', ',', 'I', 'am', 'happy', 'and', 'I', 'am', 'strong', '.']

# Now you want to keep "!" and "?" as well as separate entries in the list
# Modify your function: add an additional parameter (special_word_chars = [",", "."]), which contains all the characters which should be considered a word. -> here, pass the value [".", ",", "!", "?"]. Modify the body of the function accordingly. Use the given sentence_two.

# OUT: ['Hello', ',', 'I', 'am', 'the', 'second', 'sentence', '!', 'I', 'am', 'happy', 'as', 'well', ',', 'but', 'also', 'a', 'bit', 'confused', '.', 'How', 'about', 'you', '?']

sentence_two = "Hello, I am the second sentence! I am happy as well, but also a bit confused. How about you?"

special_chars =  [".", ",", "!", "?"]

# Now write a function 'put_sentence_together', which takes a list of string elements and returns one string correctly formatted as a sentence. Use "".join, list comprehension and an if else condition to add correct spacing. You can treat the first word separately, but you have to handle words contained in the special_chars list (above) separately.

# OUT: Hello, I am the second sentence! I am happy as well, but also a bit confused. How about you?

my_list = keep_punctuation_word_list_special(sentence_two, special_chars)
result = put_sentence_together(my_list)
