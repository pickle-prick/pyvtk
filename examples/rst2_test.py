from ansys.mapdl import reader as pymapdl_reader
from ansys.mapdl.reader import examples
import numpy as np

import pyvista as pv

def main():
  # filename = "data/file.rst"
  # filename = "data/file-nocompression.rst"
  filename = "data/file_final.rst"
  # filename = examples.hexarchivefile
  ret = pymapdl_reader.read_binary(filename)
  # print(ret.result_dof(0))
  # ret.plot_principal_nodal_stress(0, "SEQV", show_displacement=True, treat_nan_as_zero=True, loop=False)
  # _, pstress = ret.principal_nodal_stress("")
  ret.plot_principal_nodal_stress(90, "SEQV", treat_nan_as_zero=True)
  return

  point_data = ret.grid.point_data
  ids_1 = ret.grid.point_data["GEAR1"].astype(int)
  ids_2 = ret.grid.point_data["GEAR2"].astype(int)
  seed_1 = np.where(point_data["GEAR1"] > 0)[0]
  seed_2 = np.where(point_data["GEAR2"] > 0)[0]
  blocks = []

  import time
  start = time.perf_counter()
  gear1 = pv.DataSetFilters.connectivity(ret.grid, "point_seed", point_ids=seed_1)
  gear2 = pv.DataSetFilters.connectivity(ret.grid, "point_seed", point_ids=seed_2)
  blocks.append(gear1)
  blocks.append(gear2)

  # labeld = pv.DataSetFilters.connectivity(ret.grid, "point_seed", point_ids=seed_1)
  # for i in [1, 0]:
  #   b = labeld.threshold([i-0.1,i+0.1], scalars="RegionId")
  #   blocks.append(b)

  # mblock = ret.grid.split_bodies()
  # blocks = []
  # for i in range(mblock.n_blocks):
  #   block = mblock.GetBlock(i)
  #   if block.n_points > 3:
  #     print(f"block points: {block.n_points}")
  #     blocks.append(block)

  # 158254
  # 79122*2 = 158244
  # plotter = pv.Plotter()
  # # plotter.add_mesh(mblock)
  # plotter.add_mesh(blocks[0], color="red")
  # plotter.add_mesh(blocks[1], color="blue")
  # plotter.show()
  # return

  print("--- File Info ---")
  print(f"Number of nodes: {ret.mesh.n_node}")
  print(f"Number of time steps: {ret.nsets}")

  nsets = ret.nsets
  mesh = ret.grid
  point_data = mesh.GetPointData()["angles"]

  nnum, pstress = ret.principal_nodal_stress(0)
  # ret.plot_nodal_stress(3, "Z", show_displacement=True)
  # for i in range(nsets):
  #   ret.plot_principal_nodal_stress(i, "SEQV", show_displacement=True, treat_nan_as_zero=True, loop=False)
  # return

  props = [i for i in dir(ret) if not i.startswith("_")]
  for i in props: print(i)

  # ['X', 'Y', 'Z', 'XY', 'YZ', 'XZ']
  # ret.plot_nodal_stress(5, 'X')
  # for i in range(len(ret.time_values)):
  #   ret.plot_nodal_solution(0, 'x', label='Displacement')

  # ret.plot_nodal_solution(0, show_displacement=True, displacement_factor=100)
  ret.animate_nodal_solution(0, show_displacement=False, treat_nan_as_zero=False, loop=False)
  # ret.animate_nodal_solution_set([0,1,2,3,4])
  # return
  # ret.animate_nodal_displacement(0)

  # ret.plot_nodal_solution(0, 'x', label='Displacement')
  # ret.plot_nodal_elastic_strain(0, 'x', label='ElasticStrain')
  # ret.plot_nodal_plastic_strain(0, 'x', label='PlasticStrain')
  # ret.plot_nodal_solution(0, 'x', label='PlasticStrain')
  # ret.plot_nodal_stress(0, 'x', label='PlasticStrain')
  # ret.plot_nodal_temperature(0, 'x', label='PlasticStrain')
  # ret.plot_principal_nodal_stress(3, 'x', label='PlasticStrain')

  # Get the initial (undeformed) points
  # ret.grid is a PyVista UnstructuredGrid
  original_points = ret.grid.points 

  # Get the total number of result sets (time steps)
  number_of_steps = ret.nsets

  print(f"Total steps found: {number_of_steps}")

  # Loop through each step (index starts at 0)
  for step_index in range(number_of_steps):
    # 1. Fetch the nodal displacement for this step
    # nnum: node numbers, disp_data: the displacement vectors (x, y, z)
    # The '0' usually refers to the first result type, which is displacement
    nnum, disp_data = ret.nodal_solution(step_index)
    disp_data = disp_data[:, 0:3]
    
    # 2. Calculate the deformed (rotated) coordinates
    # Note: disp_data is usually (N, 3), matching original_points shape
    current_deformed_points = original_points + disp_data
    
    print(f"Step {step_index}: Gear rotated.")
    print(f" - Sample Old Point: {original_points[-1]}")
    print(f" - Sample Displacement: {disp_data[-1]}")
    print(f" - Sample New Point: {current_deformed_points[-1]}")
    
    # --- OPTIONAL: If you want to update the PyVista grid object ---
    # Create a copy so you don't overwrite the original reference mesh
    deformed_grid = ret.grid.copy()
    deformed_grid.points = current_deformed_points
    
    # Now 'deformed_grid' is the actual rotated geometry for this step
    # You can save it or plot it:
    # deformed_grid.save(f"step_{step_index}.vtk")

  # steps
  freqs = ret.time_values
  print(freqs)

  # mesh
  mesh = ret.grid
  print("###")
  print(f"mesh: {ret.mesh}")
  print("###")
  print(f"grid: {ret.grid}")

  # test
  # Solution Type: NSL
  n_cells = mesh.n_cells
  n_points = mesh.n_points
  nnum, disp = ret.nodal_solution(0)

  # load displacement
  # _, disp = ret.nodal_solution(0)
  _, disp = ret.nodal_displacement(0)
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
