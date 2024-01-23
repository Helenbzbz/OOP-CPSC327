
class Point:
    def __init__(self, a=0, b=0):
        self.move(a, b)

## When write (a=0, b=0) in the __init__ function, it means that if the user does not provide any input, then the default value of a and b will be 0.
## Positional arguments are the arguments that are passed to the function in correct positional order. 
## Optional arguments are the arguments that can be passed to the function in any order.
    
    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        
    def delta_move(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y

    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5

p1 = Point(5, 10)
p2 = Point(-5, 10)
p3 = Point(0, 0)

print(p1)
print(p2)

print(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)

## We can call the method from 2 methods below:
p3.delta_move(1,2) ## object.method_name(arguments)
Point.delta_move(p3, 1, 2) ## class_name.method_name(object, arguments)

print(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)