########################
# SOLUTION 1: if, else, elif
########################

daynumber = int(input("Input the day of Week: (1 = Montag, 2 = Dienstag, ..., 7 = Sonntag) "))

# print(type(daynumber))
# print("daynumber:", daynumber)

if daynumber == 1:
    print("You have to work ...!")  
elif daynumber == 2:    
    print("You have to work ...!")
elif daynumber == 3:    
    print("You have to work ...!")            
elif daynumber == 4:    
    print("You have to work ...!")            
elif daynumber == 5:    
    print("You have to work ...!")            
elif daynumber == 6:    
    print("Enjoy the time now ...!")            
elif daynumber == 7:    
    print("Enjoy the time now ...!")           
else:
    print("Wrong input or do you live on another planet?")

########################
# Alternative Solution 1: if, else, elif
########################

daynumber = int(input("Input the day of Week: (1 = Montag, 2 = Dienstag, ..., 7 = Sonntag) "))

# print(type(daynumber))
# print("daynumber:", daynumber)

if daynumber in (1,2,3,4,5):
    print("You have to work ...!")
elif daynumber in (6,7):
    print("Enjoy the time now ...!")
else:
    print("No valid input...")

########################
# SOLUTION 2: if, else, elif
########################

age = int(input("Input the age of the custumer:  "))

if age >= 18 and age <25:
    print("The customer belongs to the 'Youth' category")
elif age >= 25 and age <35:
    print("The customer belongs to the 'YoungAdult' category")
elif age >= 35 and age <60:
    print("The customer belongs to the 'MiddleAged' category")
elif age >= 60 :
    print("The customer belongs to the 'Senior' category")

########################
# SOLUTION 3: if, else, elif
########################

temp = input("Give a temperature you like to convert? (e.g., 45F, 102C etc.) : ")
degree = int(temp[:-1])
i_convention = temp[-1]

if i_convention.upper() == "C":
    result = int(round((9 * degree) / 5 + 32))  
    o_convention = "Fahrenheit"
elif i_convention.upper() == "F":
    result = int(round((degree - 32) * 5 / 9))
    o_convention = "Celsius"
else:
    print("No valid input...")
    quit()

print("The temperature in", o_convention, "is", result, "degrees.")
