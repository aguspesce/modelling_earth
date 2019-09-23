import modelling_earth as me
import matplotlib.pyplot as plt

region = (0, 2000e3, -660e3, 0)
shape = (251, 81)

coordinates = me.grid_coordinates(region, shape)

vertices = [
    [[0, -100e3], [500e3, -100e3], [1000e3, -150e3], [2000e3, -150e3]],
    [[0, -20e3], [500e3, -20e3], [1000e3, -45e3], [2000e3, -45e3]],
]
names = ["lab", "crust"]

interfaces = me.interfaces(vertices, coordinates, names)
print(interfaces)

interfaces.crust.plot()
interfaces.lab.plot()
plt.show()
