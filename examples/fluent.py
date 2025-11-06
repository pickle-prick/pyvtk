import pyvista as pv
import numpy as np
import h5py
import glob
import typing as t
from dataclasses import dataclass

@dataclass
class FluentData:
  mtime:float
  phase_count:int
  cells:t.List[t.Dict[str, np.ndarray]] # multiple phases
  faces:t.List[t.Dict[str, np.ndarray]] # multiple phases

# load CFD Fluent .dat.h5 file
def load_dat_file(dat_filename:str) -> FluentData:
  ret: FluentData = FluentData(mtime=0, phase_count=0, cells=[], faces=[])
  with h5py.File(dat_filename, "r") as f:
    keys = list(f.keys())
    assert "results" in keys, f"'results' group not found in {dat_filename}"
    assert "settings" in keys, f"'settings' group not found in {dat_filename}"
    results = f["results"]
    settings = f["settings"]
    data = results["1"] 
    for phase_key in data.keys():
      ret.phase_count += 1
      phase = data[phase_key]
      cells = phase["cells"]
      faces = phase["faces"]
      cell_data = {}
      for key, value in cells.items():
        values = value
        if isinstance(value, h5py.Dataset):
          values = np.array(value)
        if isinstance(value, h5py.Group):
          values = np.array(value["1"])
        cell_data[key] = values
      face_data = {}
      for key, value in faces.items():
        values = value
        if isinstance(value, h5py.Dataset):
          values = np.array(value)
        if isinstance(value, h5py.Group):
          values = np.array(value["1"])
        face_data[key] = values
      ret.cells.append(cell_data)
      ret.faces.append(face_data)

    # mtime = f.attrs.get("mtime", 0)
    # data = {key: np.array(value) for key, value in f.items()}
  return ret

def main():
  # read case file, optionaly with a data file if there is a *.dat.h5
  filename = "./data/Fluent-result/FFF-5.cas.h5" 
  # filename = "./data/3D-Pipe/FFF.1-1.cas.h5" 
  reader = pv.get_reader(filename)
  blocks = reader.read()
  mesh = blocks[0]

  # load dat files
  dat_files = sorted(glob.glob("./data/Fluent-result/FFF*.dat.h5"))
  dats = [load_dat_file(f) for f in dat_files]
  
  # create an interactive plotter
  plotter = pv.Plotter()

  # change background
  # plotter.set_background("black")

  # for key, array in mesh.cell_data.items():
  #   print(f"Cell Data Array: {key}, dtype={array.dtype}, shape={array.shape}, values={array[:10]}...")

  # merge u,v,w
  sv_u = mesh.cell_data["SV_U"]
  sv_v = mesh.cell_data["SV_V"]
  # construct the w component as the mesh z coordinate
  z = mesh.points[0][2]
  sv_w = np.full_like(sv_u, z)
  # sv_w = mesh.cell_data["SV_W"]
  # vel = np.stack((sv_u, sv_v, sv_w), axis=-1)
  vel = np.stack((sv_u, sv_v, sv_w), axis=-1)
  vel_mag = np.linalg.norm(vel, axis=-1)
  vel /= np.expand_dims(vel_mag, axis=-1)
  vel_inverted = -1 * vel.copy()

  # assign velocity vector to the mesh
  mesh.cell_data["Velocity"] = vel
  mesh.cell_data["Velocity_Inverted"] = vel_inverted
  mesh.cell_data["Velocity_Mag"] = vel_mag

  # add mesh with the first available scalar field
  # first_scalar = next(iter(mesh.cell_data.keys()), None)
  first_scalar = "SV_V"
  if first_scalar:
    plotter.add_mesh(mesh, scalars=first_scalar, cmap="viridis")
    # plotter.add_scalar_bar(title=first_scalar, n_labels=5)
    plotter.add_scalar_bar(title=first_scalar)
  else:
    plotter.add_mesh(mesh)

  arrows = mesh.glyph(orient="Velocity", scale="Velocity", factor=0.005, tolerance=0.00)
  # plotter.add_mesh(arrows, color="red", label="Velocity Vectors")
  plotter.add_mesh(arrows, scalars="Velocity_Mag", cmap="viridis", label="Velocity Vectors")
  # arrows_inverted = mesh.glyph(orient="Velocity_Inverted", scale="Velocity_Inverted", factor=0.001, tolerance=0.05)
  # plotter.add_mesh(arrows_inverted, color="red", label="Inverted Velocity Vectors")

  plotter.add_legend()
  # plotter.show()
  plotter.show(screenshot='fluent.png')

if __name__ == '__main__':
  main()
