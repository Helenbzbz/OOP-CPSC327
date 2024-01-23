class Bird():
    pass

class Parrot(Bird):
    def fly(self):
        print("Parrot can fly")

class Duck(Bird):
    def swim(self):
        print("Duck can swim")

    def fly(self):
        print("Duck can fly")

class Fish():
    def fly(self):
        print("Fish can not fly")


## We don't need to make fish a bird, but can still use the same function fly() for fish.
animals = [Duck(), Fish(), Parrot()]
for animal in animals:
    animal.fly()

## Multiple ways to import a module
    ## import module_name
    ## from module_name import function_name
    ## import module_name as new_name
    ## import module_name.function_name as new_name
    ## from module_name import *

