# import pyvista as pv
import numpy as np
import vtk
import matplotlib.cm as cm
from vtk.util import numpy_support
from vtkmodules.vtkIOFLUENTCFF import vtkFLUENTCFFReader
from vtkmodules.vtkRenderingCore import (
  vtkActor,
  vtkCamera,
  vtkPolyDataMapper,
  vtkRenderWindow,
  vtkRenderWindowInteractor,
  vtkRenderer,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
import h5py
import sexpdata
import time
import glob
import typing as t
from dataclasses import dataclass

@dataclass
class NamedArray:
  name:str
  n_component:int
  array:np.ndarray

@dataclass
class FluentData:
  phase_count:int
  cell_data:t.Dict[str,NamedArray]

@dataclass
class FrameInfo:
  cas_file:str
  dat_file:str
  step:int
  # flow_time:float # FIXME: don't know how to get

@dataclass
class Frame:
  info:FrameInfo
  cas:t.Any
  dat:FluentData

@dataclass
class CFF:
  frames:t.List[Frame]
  duration:float

def print_group(name, obj):
  print(name, type(obj))

def lut_from_name(cmap_name:str, n=256):
  cmap = cm.get_cmap(cmap_name, n)
  lut = vtk.vtkLookupTable()
  lut.SetNumberOfTableValues(n)
  for i in range(n):
    r,g,b,a = cmap(i/(n-1))
    lut.SetTableValue(i, r,g,b,a)
  lut.Build()
  return lut

# def frame_infos_from_cas(cas_file:str):
#   with h5py.File(cas_file, "r") as f:
#     s1 = f["/meshes/1"] # meshes
#     s2 = f["/settings"] # meshes
#     f.visititems(print_group)

#     for k in s2:
#       obj = s2[k]
#       value = obj[0]
#       print(s2[k])
#     dat_vars = f["/settings/Data Variables"][0]
#     assert(isinstance(dat_vars, bytes))
#     packed = sexpdata.loads(dat_vars.decode("ascii"))
#     for i in packed:
#       if(isinstance(i, list) and i[0] == sexpdata.Symbol("autosave/solution-points")):
#         print(i)

# load CFD Fluent .dat.h5 file
def load_dat_file(dat_filename:str) -> FluentData:
  ret: FluentData = FluentData(phase_count=0, cell_data={})
  # FIXME: mtime should be stored on some directory inside h5

  with h5py.File(dat_filename, "r") as f:
    # f.visititems(print_group)
    # import sys
    # sys.exit(0)

    obj_info = f["/results/1"]
    settings = f["/settings"]
    # datvars = f["/settings/Data Variables"][0].decode("ascii")
    if obj_info:
      iphase: int = 1
      phase = f.get(f"/results/1/phase-{iphase}", None)
      while phase:
        ret.phase_count += 1
        group_cell = phase.get("cells", None)
        assert group_cell
        dset = group_cell.get("fields", None)
        assert dset
        fields_raw = dset[()][0].decode()
        v_str = fields_raw.split(";")

        for section_name in v_str:
          if section_name in group_cell:
            groupdata = group_cell[section_name]
            if iphase > 1: section_name = f"phase_{iphase-1}-{section_name}"
            n_sections = int(groupdata.attrs["nSections"][0])
            for i_section in range(1, n_sections+1):
              dset = groupdata[str(i_section)]
              min_id = int(dset.attrs["minId"][0])
              max_id = int(dset.attrs["maxId"][0])
              data = dset[()]
              data = data.astype(np.float64)
              ndims = data.ndim
              dims = data.shape
              n_components = 1 if ndims == 1 else dims[-1]
              values: NamedArray = NamedArray(section_name, n_components, data)

              # # scalar values
              # if ndims == 1:
              #   values.n_component = 1
              #   values.array = data[(min_id-1):max_id]
              # # vector values
              # elif ndims <= 3:
              #   vector_data = []
              #   for k in range(ndims):
              #     for j in range(min_id-1, max_id):
              #       vector_data.append(float(data[j][k]))
              #   values.n_component = ndims
              #   values.array = vector_data

              # insert into cell_data
              ret.cell_data[section_name] = values

        # advance
        phase = f.get(f"/results/1/phase-{iphase}", None)
        iphase += 1
  return ret

def main():
  project_dir = "./data/Fluent-result"
  # project_dir = "./data/3D-Pipe"
  # read case file, optionaly with a data file if there is a *.dat.h5
  cas_file = glob.glob(f"{project_dir}/*.cas.h5")[0]
  # cas_file = "./data/Fluent-result/FFF-5.cas.h5"
  # filename = "./data/3D-Pipe/FFF.1-1.cas.h5" 
  reader = vtkFLUENTCFFReader()
  reader.SetFileName(cas_file)
  reader.Update()
  blocks:vtk.vtkMultiBlockDataSet = reader.GetOutput()
  assert(isinstance(blocks, vtk.vtkMultiBlockDataSet))
  n_blocks:int = blocks.GetNumberOfBlocks()
  assert n_blocks == 1
  mesh: vtk.vtkUnstructuredGrid = blocks.GetBlock(0)
  assert(isinstance(mesh, vtk.vtkUnstructuredGrid))

  # animating settings
  anim_duration_ms:float = 3000

  # parse frames 
  # FIXME: we should be able to extract frame info from cas file, but don't know how, just use glob for now
  frames: t.List[Frame]  = []
  for dat_file in sorted(glob.glob(f"{project_dir}/*.dat.h5")):
    step = int(dat_file.split("-")[-1].split(".")[0])
    info: FrameInfo = FrameInfo(cas_file, dat_file, step)
    dat: FluentData = load_dat_file(dat_file)
    frame: Frame = Frame(info, mesh, dat)
    frames.append(frame)

  # pipeline
  geom = vtk.vtkGeometryFilter()
  geom.SetInputData(mesh)

  # mapper
  mapper = vtkPolyDataMapper()
  mapper.SetInputConnection(geom.GetOutputPort())
  # "viridis", "plasma", "inferno", "magma", "coolwarm"…
  lut = lut_from_name("inferno")
  lut.SetTableRange((0,1))
  mapper.SetLookupTable(lut)
  mapper.SetScalarRange(0, 1)
  mapper.SetUseLookupTableScalarRange(False)

  # actor
  actor = vtkActor()
  actor.SetMapper(mapper)
  # # Lighting
  # actor.GetProperty().SetAmbient(0.3)
  # actor.GetProperty().SetDiffuse(0.0)
  # actor.GetProperty().SetSpecular(1.0)
  # actor.GetProperty().SetSpecularPower(20.0)

  # render
  ren = vtkRenderer()
  win = vtkRenderWindow()
  win.AddRenderer(ren)
  iren = vtk.vtkRenderWindowInteractor()
  iren.SetRenderWindow(win)
  ren.AddActor(actor)
  win.SetSize(1024,512)

  # camera
  # camera = vtkCamera()
  # camera.SetPosition(4.6, -2.0, 3.8)

  # update hook
  tick_idx:int = 0
  n_cells = mesh.GetNumberOfCells()
  def update_callback(caller:vtk.vtkObject, event_id:int):
    nonlocal tick_idx
    frame_idx:int = tick_idx%len(frames)
    frame = frames[frame_idx]
    for k,arr in frame.dat.cell_data.items():
      array_name = k
      vtk_array = mesh.GetCellData().GetArray(array_name)
      if not vtk_array:
        vtk_array = vtk.vtkFloatArray()
        vtk_array.SetName(k)
        vtk_array.SetNumberOfComponents(arr.n_component)
        vtk_array.SetNumberOfTuples(n_cells)
        mesh.GetCellData().AddArray(vtk_array)
      np_array: np.ndarray = numpy_support.vtk_to_numpy(vtk_array)
      assert isinstance(np_array, np.ndarray)
      # FIXME: different number of component for the same named array, what fuck?
      try:
        np_array[:] = arr.array
      except: pass

    sv_u = numpy_support.vtk_to_numpy(mesh.cell_data["SV_U"])
    sv_v = numpy_support.vtk_to_numpy(mesh.cell_data["SV_V"])
    # z = mesh.points[0][2]
    z = 0
    sv_w = np.full_like(sv_u, z)
    vel = np.stack((sv_u, sv_v, sv_w), axis=-1)
    vel_mag = np.linalg.norm(vel, axis=-1)
    # vel /= np.expand_dims(vel_mag, axis=-1)
    # vel_inverted = -1 * vel.copy()

    vtk_array = mesh.GetCellData().GetArray("VelocityMag")
    if not vtk_array:
      vtk_array = vtk.vtkFloatArray()
      vtk_array.SetName("VelocityMag")
      vtk_array.SetNumberOfComponents(1)
      vtk_array.SetNumberOfValues(n_cells)
      mesh.GetCellData().SetScalars(vtk_array)
    np_wrapper = numpy_support.vtk_to_numpy(vtk_array)
    np_wrapper[:] = vel_mag
    geom.SetInputData(mesh)
    geom.Modified()

    tick_idx += 1
    win.Render()

  iren.AddObserver("TimerEvent", update_callback)
  iren.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
  iren.Initialize()
  timer_id = iren.CreateRepeatingTimer(int(anim_duration_ms/len(frames)))
  iren.Start()
  iren.DestroyTimer(timer_id)
  
  # create an interactive plotter
  # plotter = pv.Plotter()
  # change background
  # plotter.set_background("black")
  # for key, array in mesh.cell_data.items():
  #   print(f"Cell Data Array: {key}, dtype={array.dtype}, shape={array.shape}, values={array[:10]}...")

  # plotter.add_mesh(mesh, scalars="SV_V", cmap="viridis")
  # plotter.add_on_render_callback(update_frame)
  # plotter.add_timer_event(len(frames), 100, callback=callback)
  # plotter.show()

  # # merge u,v,w
  # sv_u = mesh.cell_data["SV_U"]
  # sv_v = mesh.cell_data["SV_V"]
  # # construct the w component as the mesh z coordinate
  # z = mesh.points[0][2]
  # sv_w = np.full_like(sv_u, z)
  # # sv_w = mesh.cell_data["SV_W"]
  # # vel = np.stack((sv_u, sv_v, sv_w), axis=-1)
  # vel = np.stack((sv_u, sv_v, sv_w), axis=-1)
  # vel_mag = np.linalg.norm(vel, axis=-1)
  # vel /= np.expand_dims(vel_mag, axis=-1)
  # vel_inverted = -1 * vel.copy()

  # # assign velocity vector to the mesh
  # mesh.cell_data["Velocity"] = vel
  # mesh.cell_data["Velocity_Inverted"] = vel_inverted
  # mesh.cell_data["Velocity_Mag"] = vel_mag

  # # add mesh with the first available scalar field
  # # first_scalar = next(iter(mesh.cell_data.keys()), None)
  # first_scalar = "SV_V"
  # if first_scalar:
  #   plotter.add_mesh(mesh, scalars=first_scalar, cmap="viridis")
  #   # plotter.add_scalar_bar(title=first_scalar, n_labels=5)
  #   plotter.add_scalar_bar(title=first_scalar)
  # else:
  #   plotter.add_mesh(mesh)

  # arrows = mesh.glyph(orient="Velocity", scale="Velocity", factor=0.005, tolerance=0.00)
  # # plotter.add_mesh(arrows, color="red", label="Velocity Vectors")
  # plotter.add_mesh(arrows, scalars="Velocity_Mag", cmap="viridis", label="Velocity Vectors")
  # # arrows_inverted = mesh.glyph(orient="Velocity_Inverted", scale="Velocity_Inverted", factor=0.001, tolerance=0.05)
  # # plotter.add_mesh(arrows_inverted, color="red", label="Inverted Velocity Vectors")

  # plotter.add_legend()
  # # plotter.show()
  # plotter.show(screenshot='fluent.png')

if __name__ == '__main__':
  main()