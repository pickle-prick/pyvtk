import pyvista as pv
import numpy as np


def main():
  # read case file, optionaly with a data file if there is a *.dat.h5
  filename = "./data/Fluent-result/FFF-5.cas.h5" 
  # filename = "./data/3D-Pipe/FFF.1-1.cas.h5" 
  reader = pv.get_reader(filename)
  blocks = reader.read()
  mesh = blocks[0]
  
  # create an interactive plotter
  plotter = pv.Plotter()

  # change background
  plotter.set_background("black")

  for key, array in mesh.cell_data.items():
    print(f"Cell Data Array: {key}, dtype={array.dtype}, shape={array.shape}, values={array[:10]}...")

  # merge u,v,w
  sv_u = mesh.cell_data["SV_U"]
  sv_v = mesh.cell_data["SV_V"]
  # construct the w component as the mesh z coordinate
  z = mesh.points[0][2]
  sv_w = np.full_like(sv_u, z)
  # sv_w = mesh.cell_data["SV_W"]
  # vel = np.stack((sv_u, sv_v, sv_w), axis=-1)
  vel = np.stack((sv_u, sv_v, sv_w), axis=-1)
  vel_inverted = -1 * vel.copy()

  # assign velocity vector to the mesh
  mesh.cell_data["Velocity"] = vel
  mesh.cell_data["Velocity_Inverted"] = vel_inverted

  # Add mesh with the first available scalar field
  # first_scalar = next(iter(mesh.cell_data.keys()), None)
  first_scalar = "SV_V"
  if first_scalar:
    plotter.add_mesh(mesh, scalars=first_scalar, cmap="viridis")
    # plotter.add_scalar_bar(title=first_scalar, n_labels=5)
    plotter.add_scalar_bar(title=first_scalar)
  else:
    plotter.add_mesh(mesh)

  arrows = mesh.glyph(orient="Velocity", scale="Velocity", factor=0.01, tolerance=0.05)
  plotter.add_mesh(arrows, color="red", label="Velocity Vectors")
  # arrows_inverted = mesh.glyph(orient="Velocity_Inverted", scale="Velocity_Inverted", factor=0.001, tolerance=0.05)
  # plotter.add_mesh(arrows_inverted, color="red", label="Inverted Velocity Vectors")

  plotter.add_legend()
  # plotter.show()
  plotter.show(screenshot='fluent.png')

if __name__ == '__main__':
  main()