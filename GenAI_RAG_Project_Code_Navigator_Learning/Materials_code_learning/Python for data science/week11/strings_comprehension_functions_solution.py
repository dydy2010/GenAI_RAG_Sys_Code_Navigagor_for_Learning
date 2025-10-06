#%% string manipulation, list comprehension, functions
# General hint: Check out the regular expressions package "re" in case you encounter problems of this kind. To focus on python basics, we do not use it in this exercise.

#%% Start
sentence = "Hello, I am the first sentence, I am happy and I am strong."

# Use str.split method to create a list of all elements separated by " "
result = sentence.split(" ")
print(result)

# Use list comprehension to add "__" to every entry of the word list
result = [elem + "__" for elem in sentence.split(" ")]
print(result)

# Use str.replace to previously remove "," and "." to get a list of only the words

result = sentence.replace(".","").replace(",", "").split(" ")
print(result)

# Now you would like to keep punctuation marks as ',' and '.' as separate entries in the list
# Write a function 'keep_punctuation_word_list', which takes a sentence, extracts "," and "." from sub-strings and adds them to the list of words at the right position.

def keep_punctuation_word_list(sentence):
    a_list = sentence.split(" ")
    b_list = []
    for elem in a_list:
        if ',' in elem:
            b_list.append(elem.replace(",",""))
            b_list.append(",")
        elif '.' in elem:
            b_list.append(elem.replace(".",""))
            b_list.append(".")
        else:
            b_list.append(elem)
    return b_list

result = keep_punctuation_word_list(sentence)
print(result)

# Now you want to keep "!" and "?" as well as separate entries in the list
# Modify your function: add an additional parameter (special_word_chars = [",", "."]), which contains all the characters which should be considered a word. -> here, pass the value [".", ",", "!", "?"]. Modify the body of the function accordingly. Use the given sentence_two.

sentence_two = "Hello, I am the second sentence! I am happy as well, but also a bit confused. How about you?"

def keep_punctuation_word_list_special(sentence, special_word_chars = [",", "."]):
    a_list = sentence.split(" ")
    b_list = []
    for elem in a_list:
        if any([substring in elem for substring in special_word_chars]):
            # assuming every punctuation mark is at the end of the substring!
            b_list.append(elem[:-1])
            b_list.append(elem[-1])
        else:
            b_list.append(elem)
    return b_list

special_chars =  [".", ",", "!", "?"]
result = keep_punctuation_word_list_special(sentence_two, special_chars)
print(result)

# Now write a function 'put_sentence_together', which takes a list of string elements and returns one string
# correctly formatted as a sentence. Use "".join,
# list comprehension and an if else condition to add correct spacing.
# You can treat the first word separately, but you have to handle words contained in the special_chars list (above) separately.
def put_sentence_together(string_list, special_chars=[".", ",", "!", "?"]):
    result = my_list[0] + "".join([" " + elem if elem not in special_chars else elem for elem in my_list[1:]])
    return result
my_list = keep_punctuation_word_list_special(sentence_two, special_chars)
result = put_sentence_together(my_list)
print(result)
