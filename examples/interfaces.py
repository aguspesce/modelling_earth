import modelling_earth as me
import matplotlib.pyplot as plt

region = (0, 2000e3, -660e3, 0)
shape = (251, 81)

coordinates = me.grid_coordinates(region, shape)

vertices = [
    [[0, -150e3], [500e3, -100e3], [1000e3, -100e3], [2000e3, -120e3]],
    [[0, -300e3], [500e3, -450e3], [1000e3, -450e3], [2000e3, -500e3]],
]

interfaces = me.interfaces(vertices, coordinates)
print(interfaces)

interfaces.interface_0.plot()
plt.show()
