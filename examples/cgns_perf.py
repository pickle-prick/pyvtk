import os
import struct
import numpy as np
from ansys.mapdl.reader import _binary_reader 
from scipy.spatial import cKDTree
import pyvista as pv
import time

def read_bin_file(filepath: str, ncol: int):
  with open(filepath, "rb") as f:
    content = f.read()
    size = struct.unpack("Q", content[0:8])[0]
    data = [d[0] for d in struct.iter_unpack("d", content[8:(size+1)*8])]
    assert len(data) == size, (f"Invalid bin file, expect {size}, found {len(data)}")
    nrow, r = divmod(size, ncol)
    assert r == 0, ("Invalid column count {ncol}, can not reshape with size {size}")
    return np.reshape(np.array(data, dtype="f8"), (nrow, ncol))

def compute_principal_stress(stress: np.ndarray):
  pstress, isnan = _binary_reader.compute_principal_stress(stress)
  pstress[isnan] = np.nan
  np.nan_to_num(pstress, copy=False)
  return pstress[:,4]

def nn_index_map(A: np.ndarray, B: np.ndarray, tol: float | None = 1e-9):
  """
  A: (n,3) 参考点集
  B: (n,3) 待匹配点集
  返回：
    idx: (n,) 使得 A[idx[i]] 是 B[i] 在 A 中的最近点
    dist: (n,) 最近距离
  """
  A = np.ascontiguousarray(A, dtype=np.float64)
  B = np.ascontiguousarray(B, dtype=np.float64)

  tree = cKDTree(A)
  # workers=-1 用满 CPU
  workers = ((os.cpu_count() or 1) // 2) or -1
  dist, idx = tree.query(B, k=1, workers=-1)

  if tol is not None:
    md = float(dist.max()) if dist.size else 0.0
    if md > tol:
      raise ValueError(
        f"max nearest distance {md} > tol {tol}，"
        "点集可能不一致或有噪声/尺度问题"
      )

  return idx, dist


def perf(mesh_path: str, bin_path: str):
  # FIXME: time this whole operation
  start_time = time.perf_counter()

  # FIXME: time these two reads
  s = time.perf_counter()
  mesh = pv.read(mesh_path).get_block(0).get_block(0).get_block(0)
  point_data = read_bin_file(bin_path, 3)
  print(f"read time: {time.perf_counter() - s:.2f} seconds")

  assert len(point_data) == len(mesh.points), f"{len(point_data)} != {len(mesh.points)}"

  print(f"point_count: {len(mesh.points)}")
  print(f"cell_count: {len(mesh.cells)}")

  # compute index map
  s = time.perf_counter()
  point_idx_map, dist = nn_index_map(point_data, mesh.points)
  print(f"index map time: {time.perf_counter() - s:.2f} seconds")

  # surface extraction
  # FIXME: time this
  s = time.perf_counter()
  surface_mesh = mesh.extract_surface().triangulate()
  print(f"surface extraction time: {time.perf_counter() - s:.2f} seconds")

  # FIXME: time this
  s = time.perf_counter()
  vertices = [tuple(p) for p in surface_mesh.points.tolist()]
  raw_faces = surface_mesh.faces.reshape(-1, 4)[:, 1:]
  indices = [tuple(f) for f in raw_faces.tolist()]
  print(f"face extraction time: {time.perf_counter() - s:.2f} seconds")
  print(f"vertex_count: {len(vertices)}")
  print(f"face_count: {len(indices)}")

  # step
  # 1. copy mesh
  # 2. read bin file
  # 3. compute principal stress
  # s = time.perf_counter()
  # mesh_copy = mesh.copy(deep=True)
  # point_data = read_bin_file(bin_path, 3)
  # stress = point_data[point_idx_map]
  # pstress = compute_principal_stress(stress)
  # mesh.point_data["pstress"] = pstress
  # print(f"step time: {time.perf_counter() - s:.2f} seconds")

  print(f"total time: {time.perf_counter() - start_time:.2f} seconds")

  # mesh.plot()

def main():
  dt = [
    ("./data/zhicheng/zhicheng.cgns", "./data/zhicheng/points.bin"),
    ("./data/bot/link.cgns", "./data/bot/snapshot_1.bin"),
  ]

  for (mesh_path, bin_path) in dt:
    print(f"Testing {mesh_path} with {bin_path}")
    perf(mesh_path, bin_path)
    print("-" * 40)


if __name__ == "__main__":
  main()
