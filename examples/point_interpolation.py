import pyvista as pv
from pyvista import examples
import numpy as np

def main():
  probs = examples.download_thermal_probes()
  # add velocity to the point data
  velocities = []
  for point in probs.points:
    x, y, z = point
    # create a simple swirling velocity field
    u = -y
    v = x
    w = 0.1 * z
    # normalize
    mag = np.sqrt(u**2 + v**2 + w**2)
    u /= mag
    v /= mag
    w /= mag
    velocities.append((u, v, w))
  velocities = np.array(velocities)
  probs.point_data["velocity"] = velocities

  grid = pv.ImageData()
  grid.origin = (329700, 4252600, -2700)
  grid.spacing = (2500, 2500, 500)
  grid.dimensions = (60, 75, 100)

  interp = grid.interpolate(probs, radius=15000, sharpness=10, strategy="mask_points")
  arrows = interp.glyph(orient="velocity", scale="velocity", factor=200.0, tolerance=0.01)

  drags = dict(cmap="coolwarm", clim=[0, 300], scalars="temperature (C)")
  cpos = [
    (364280.5723737897, 4285326.164400684, 14093.431895014139),
    (337748.7217949739, 4261154.45054595, -637.1092549935128),
    (-0.29629216102673206, -0.23840196609932093, 0.9248651025279784),
  ]

  vol_opac = [0, 0, 0.2, 0.2, 0.5, 0.5]

  pl = pv.Plotter(shape=(1, 2))

  pl.add_volume(interp, opacity=vol_opac, **drags)
  pl.add_mesh(probs, render_points_as_spheres=True, point_size=10, **drags)
  pl.add_mesh(grid.outline(), color="k")

  pl.subplot(0, 1)

  pl.add_mesh(grid.outline(), color="k")
  # pl.add_mesh(interp.contour(9), opacity=0.5, **drags)
  pl.add_mesh(probs, render_points_as_spheres=True, point_size=10, **drags)
  pl.add_mesh(arrows, color="black")

  pl.show(cpos=cpos)

if __name__ == "__main__":
  main()
