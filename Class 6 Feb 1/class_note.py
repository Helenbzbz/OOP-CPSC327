class Shape2D:
    "Abstract class defining a template for 2D shapes that should implement area"

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        raise NotImplementedError()

class Shape3D:
    "Abstract class defining a template for 3D shapes that should implement volume"

    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth

    def volume(self):
        raise NotImplementedError()

class Rectangle(Shape2D):
    def area(self):
        return self.width * self.height

class Triangle(Shape2D):
    def area(self):
        return self.width * self.height // 2

class Cube(Shape3D):
    def volume(self):
        return self.width * self.height * self.depth


rect = Rectangle(5, 7)
tri = Triangle(5, 7)
cube = Cube(5, 7, 8)
generic_shape = Shape2D(5, 7)


print(f"Total Rectangle area: {rect.area()}")
print(f"Total Triangle area: {tri.area()}")
print(f"Total Cube volume: {cube.volume()}")
print(f"Total General area: {generic_shape.area()}")