import pyvista as pv
from pyvista import examples

def main():
  probs = examples.download_thermal_probes()

  grid = pv.ImageData()
  grid.origin = (329700, 4252600, -2700)
  grid.spacing = (250, 250, 50)
  grid.dimensions = (60, 75, 100)

  interp = grid.interpolate(probs, radius=15000, sharpness=10, strategy="mask_points")

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
  pl.add_mesh(interp.contour(9), opacity=0.5, **drags)
  pl.add_mesh(probs, render_points_as_spheres=True, point_size=10, **drags)
  pl.show(cpos=cpos)

if __name__ == "__main__":
  main()