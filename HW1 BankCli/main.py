class Example:
    def __init__(self, names=[]):
        self.names = names

a = Example()
b = Example()
c = Example(["Sherry"])

a.names.append("Tim")

print(a.names, b.names, c.names)