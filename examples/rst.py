from ansys.mapdl import reader as pymapdl_reader
from ansys.mapdl.reader import examples
import pyvista as pv

def main():
  filename = "data/file.rst"
  # filename = examples.hexarchivefile
  ret = pymapdl_reader.read_binary(filename) 
  # ret.plot_nodal_solution(0, 'x', label='Displacement')
  # freqs = ret.time_values
  # print(freqs)
  mesh = ret.grid

  # load displacement
  _, disp = ret.nodal_solution(0)
  mesh["Displacement"] = disp

  # print(dir(ret))
  # load stress
  # stress = ret.nodal_stress(0)
  # mesh["Stress"] = stress

  # load strain
  # strain = ret.nodal_strain(0)
  # mesh["Strain"] = strain

  out = "./data/file.vtk"
  mesh.save(out)

  pl = pv.Plotter()
  mesh2 = pv.read(out)
  print(mesh2.point_data.keys())
  print(mesh2["Displacement"].shape)
  # warped = mesh2.warp_by_vector("Displacement", factor=1.000) # FIXME: 1.0 don't seem to work, we need to multiply it by 100 so it can be visiable
  warped = mesh2.warp_by_vector("Displacement", factor=1000)
  pl.add_mesh(warped, scalars="Displacement", show_edges=True)
  warped.plot()

if __name__ == '__main__':
  main()
