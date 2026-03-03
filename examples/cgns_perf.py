import struct
import numpy as np
import pyvista as pv

def read_bin_file(filepath: str, ncol: int):
  with open(filepath, "rb") as f:
    content = f.read()
    size = struct.unpack("Q", content[0:8])[0]
    data = [d[0] for d in struct.iter_unpack("d", content[8:(size+1)*8])]
    assert len(data) == size, (f"Invalid bin file, expect {size}, found {len(data)}")
    nrow, r = divmod(size, ncol)
    assert r == 0, ("Invalid column count {ncol}, can not reshape with size {size}")
    return np.reshape(np.array(data, dtype="f8"), (nrow, ncol))


def perf(mesh_path: str, bin_path: str):
  mesh = pv.read(mesh_path).get_block(0).get_block(0).get_block(0)
  point_data = read_bin_file(bin_path, 3)

  assert len(point_data) == len(mesh.points), f"{len(point_data)} != {len(mesh.points)}"

  print(f"point_count: {len(mesh.points)}")
  print(f"cell_count: {len(mesh.cells)}")

  # surface extraction
  surface_mesh = mesh.extract_surface().triangulate()

  vertices = [tuple(p) for p in surface_mesh.points.tolist()]
  raw_faces = surface_mesh.faces.reshape(-1, 4)[:, 1:]
  indices = [tuple(f) for f in raw_faces.tolist()]

  # mesh.plot()

def main():
  dt = [
    ("./data/zhicheng/zhicheng.cgns", "./data/zhicheng/points.bin"),
    ("./data/bot/link.cgns", "./data/bot/snapshot_1.bin"),
  ]

  for (mesh_path, bin_path) in dt:
    perf(mesh_path, bin_path)


if __name__ == "__main__":
  main()
