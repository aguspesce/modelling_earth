import matplotlib.pyplot as plt
from modelling_earth import (
    empty_temperature_grid,
    litho_astheno_temperatures,
    add_subducting_slab,
)


region = [0, 2000, 0, 4, 0, 660]
shape = (251, 2, 81)
temperatures = empty_temperature_grid(region, shape)
print(temperatures)
temperatures = litho_astheno_temperatures(temperatures, boundary_depth=100)

print(temperatures)
temperatures = add_subducting_slab(
    temperatures, xmin=250, xmax=800, slope=15, thickness=100
)
print(temperatures)

temperatures[:, 0, :].plot.pcolormesh(x="x", y="z")
plt.show()
