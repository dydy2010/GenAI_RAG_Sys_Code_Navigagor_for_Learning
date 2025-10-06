"""
TASK1:
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


TASK2:
Each building must have it's unique building id. In each object creation process, update first the class variable _counter by adding 1 to its current value (start with 0). Use the object method '_get_new_id' to use the updated _counter variable as the building_id.
...
self._building_id = self._get_new_id()
...
In the _get_new_id method add the building_id to the _id_container class variable. (HINT: Later you can use that to throw an error in case the building_id has already been taken)


TASK3:
Define a class 'OfficeBuilding' as a subclass of 'Building'. Add an additional object variable '_number_of_working_places', use super to handle '_nr_of_floors'.


TASK4:
Create one Building and one OfficeBuilding object with different floor numbers and print each id with the corresponding number of floors to the console.


TASK5 (optional):
What happens to the building ids if you rerun your programm? How could you guarantee that uniqueness is maintained across multiple executions of your script?
"""


class Building():

    _counter = 0
    _id_container = []

    def __init__(self, nr_of_floors):
        Building._counter += 1
        self._building_id = self._get_new_id()
        self._number_of_floors = nr_of_floors

    def _get_new_id(self):
        Building._id_container.append(Building._counter)
        return Building._counter

    def get_number_of_floors(self):
        return self._number_of_floors


class OfficeBuilding(Building):

    def __init__(self, nr_of_floors, nr_of_working_places):
        super().__init__(nr_of_floors)
        self._nr_of_working_places = nr_of_working_places


B = Building(3)
OB = OfficeBuilding(8,150)

print(B._building_id, B.get_number_of_floors())
print(OB._building_id, OB.get_number_of_floors())
