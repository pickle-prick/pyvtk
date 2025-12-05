from ansys.mapdl import reader as pymapdl_reader
from ansys.mapdl.reader import examples
import pyvista as pv

def main():
  filename = "data/file_1.rst"
  # filename = examples.hexarchivefile

  ret = pymapdl_reader.read_binary(filename) 
  props = [i for i in dir(ret) if not i.startswith("_")]
  for i in props: print(i)

  # ret.plot_nodal_solution(0, 'x', label='Displacement')
  # ret.plot_nodal_elastic_strain(0, 'x', label='ElasticStrain')
  # ret.plot_nodal_plastic_strain(0, 'x', label='PlasticStrain')
  # ret.plot_nodal_solution(0, 'x', label='PlasticStrain')
  # ret.plot_nodal_stress(0, 'x', label='PlasticStrain')
  # ret.plot_nodal_temperature(0, 'x', label='PlasticStrain')
  # ret.plot_principal_nodal_stress(3, 'x', label='PlasticStrain')

  # steps
  freqs = ret.time_values
  print(freqs)

  # mesh
  mesh = ret.grid
  print("###")
  print(f"mesh: {ret.mesh}")
  print("###")
  print(f"grid: {ret.grid}")

  # load displacement
  # _, disp = ret.nodal_solution(0)
  _, disp = ret.nodal_displacement(8)
  mesh["Displacement"] = disp[:, 0:3]
  # print(disp[90:180, 0:3])
  _, strain = ret.nodal_stress(0)
  mesh["Strain"] = strain[:, 0:3]
  _, temp = ret.nodal_temperature(0)
  mesh["Temp"] = temp

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
  print(mesh2)
  print(mesh2.point_data.keys())
  print(mesh2["Displacement"].shape)
  print(mesh2["Strain"].shape)
  print(mesh2["Temp"].shape)
  # mesh2.plot(scalars="Temp", show_edges=True)
  # warped = mesh2.warp_by_vector("Displacement", factor=1.000) # FIXME: 1.0 don't seem to work, we need to multiply it by 100 so it can be visiable
  # warped = mesh2.warp_by_vector("Displacement", factor=0.0000001)
  # pl.add_mesh(warped, scalars="Strain", show_edges=True)
  pl.add_mesh(mesh2, scalars="Strain", show_edges=True)
  pl.show()

if __name__ == '__main__':
  main()
