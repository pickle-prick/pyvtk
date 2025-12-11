from ansys.mapdl import reader as pymapdl_reader
from ansys.mapdl.reader import examples
import numpy as np
import pyvista as pv

def main():
  # filename = "data/file_final.rst"
  # filename = "data/file_final.rst"
  ret = pymapdl_reader.read_binary(filename)
  # ret.plot_principal_nodal_stress(0, "SEQV", treat_nan_as_zero=True)

  grid = ret.grid
  nsets = ret.nsets
  point_data = grid.point_data
  point_data["pstress"] = ret.principal_nodal_stress(0)[1][:,4]

  # split
  comp_names = ret.node_components.keys()
  comp_filters = [np.where(point_data[i] > 0)[0] for i in comp_names]
  # comps = [grid.connectivity("point_seed", point_ids=i) for i in comp_filters]
  comps = []
  mblock = grid.split_bodies()
  for i in range(mblock.n_blocks):
    block = mblock.GetBlock(i)
    if block.n_points > 3:
      comps.append(block)
  assert len(comps) == len(comp_names)

  vtk_names = [f"./data/test_{i}.vtu" for i in range(len(comps))]
  for idx, comp in enumerate(comps):
    comp.save(vtk_names[idx])

  pl = pv.Plotter()
  meshes = [pv.read(m) for m in vtk_names]
  # for comp in comps:
  #   pl.add_mesh(comp, scalars="pstress")
  for n in vtk_names:
    mesh = pv.read(n)
    pl.add_mesh(mesh, scalars="pstress")
    break
  pl.show()

  return

if __name__ == "__main__":
  main()
