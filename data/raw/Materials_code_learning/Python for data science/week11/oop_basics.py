"""
Exercise 1:
Define a class 'Building' with the following specifications:

class variables
_counter:
_id_container:

object variables
_building_id:
_number_of_floors:

object methods
_get_new_id:
get_number_of_floors:


Exercise 2:
Each building must have it's unique building id. In each object creation process, update first the class variable _counter by adding 1 to its current value (start with 0). Use the object method '_get_new_id' to use the updated _counter variable as the building_id.
...
self._building_id = self._get_new_id()
...
In the _get_new_id method add the building_id to the _id_container class variable. (HINT: Later you can use that to throw an error in case the building_id has already been taken)


Exercise 3:
Define a class 'OfficeBuilding' as a subclass of 'Building'. Add an additional object variable '_number_of_working_places', use super to handle '_nr_of_floors'.


Exercise 4:
Create one Building and one OfficeBuilding object with different floor numbers and print each id with the corresponding number of floors to the console.


Exercise 5:(optional)
What happens to the building ids if you rerun your programm? How could you guarantee that uniqueness is maintained across multiple executions of your script?
"""
