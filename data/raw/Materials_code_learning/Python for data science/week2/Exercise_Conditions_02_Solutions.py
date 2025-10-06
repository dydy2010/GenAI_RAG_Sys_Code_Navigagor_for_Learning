########################
# SOLUTION 1: if, else, elif
########################

a = int( input( "Input 'a': "))
b = int( input( "Input 'b': " ))
c = int( input( "Input 'c': " )) 

if a < b:
    if b < c:
        print(a,b,c)
    else:
        if a < c:
            print(a,c,b)
        else:
            print(c,a,b)
else:
    if b > c:
        print(c,b,a)
    else:
        if a > c:
            print(b,c,a)
        else:
            print(b,a,c)

########################
# SOLUTION 2a: if, else, elif
########################

a=1
b=2
c=2

if (a>b or a<(b/2) or a+c>b ):
    print("condition fulfilled")

########################
# SOLUTION 2b: if, else, elif
########################

a=5
b=5
c=1

if ((a-2)%4 == 0 or (b-c)%2 == 0 or (a != b) and (b != c)):
    print("condition fulfilled")
