import vtk
import numpy as np
import pyvista as pv

def main():
  points = vtk.vtkPoints()
  points.InsertNextPoint(0, 0, 0)
  points.InsertNextPoint(1, 0, 0)
  points.InsertNextPoint(0, 1, 0)
  points.InsertNextPoint(0, 0, 1)

  tetra = vtk.vtkTetra()
  tetra.GetPointIds().SetId(0, 0)
  tetra.GetPointIds().SetId(1, 1)
  tetra.GetPointIds().SetId(2, 2)
  tetra.GetPointIds().SetId(3, 3)

  ugrid = vtk.vtkUnstructuredGrid()
  ugrid.SetPoints(points)
  ugrid.InsertNextCell(tetra.GetCellType(), tetra.GetPointIds())

  n_points = points.GetNumberOfPoints()
  n_cells = ugrid.GetNumberOfCells()

  # add point_data and cell_data

  # point scalar: pressure
  pressure = vtk.vtkFloatArray()
  pressure.SetName("pressure")
  for i in range(n_points):
    pressure.InsertNextValue(1.0 + 0.1*i)
  ugrid.GetPointData().AddArray(pressure)

  # point vector: velocity
  velocity = vtk.vtkFloatArray()
  velocity.SetName("velocity")
  velocity.SetNumberOfComponents(3)
  for i in range(n_points):
    velocity.InsertNextTuple((0.1*i, 0.2*i, 0.3*i))
  ugrid.GetPointData().AddArray(velocity)

  # cell scalar: region id
  region = vtk.vtkIntArray()
  region.SetName("region_id")
  region.InsertNextValue(69)
  ugrid.GetCellData().AddArray(region)

  # extract surface (polygonal mesh)
  geometry_filter = vtk.vtkGeometryFilter()
  geometry_filter.SetInputData(ugrid)
  geometry_filter.Update()

  # triangulate polygons
  triangle_filter = vtk.vtkTriangleFilter()
  triangle_filter.SetInputConnection(geometry_filter.GetOutputPort())
  triangle_filter.Update()

  polydata = triangle_filter.GetOutput()

  # Glyph
  # arrow source
  arrow_source = vtk.vtkArrowSource()
  arrow_source.SetTipLength(0.3)
  arrow_source.SetTipRadius(0.1)
  arrow_source.SetShaftRadius(0.03)
  # glyph3D
  glyph = vtk.vtkGlyph3D()
  glyph.SetSourceConnection(arrow_source.GetOutputPort())
  glyph.SetInputData(polydata)
  glyph.SetVectorModeToUseVector()
  glyph.SetScaleModeToScaleByVector()
  glyph.SetScaleFactor(0.1)
  glyph.SetInputArrayToProcess(
    0, # 0 = point_data
    0, # 0 = process active attribute
    0, # 0 = default
    vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
    "velocity"
  )

  # triangles -> numpy arrays
  # vtk_points = polydata.GetPoints()  
  # points_np = np.array([vtk_points.GetPoint(i) for i in range(vtk_points.GetNumberOfPoints())])
  # print(type(vtk_points))

  # polys = []
  # idlist = vtk.vtkIdList() # idlist per cell
  # polydata.GetPolys().InitTraversal()
  # while polydata.GetPolys().GetNextCell(idlist):
  #   # only handle triangles
  #   if idlist.GetNumberOfIds() == 3:
  #     polys.append([idlist.GetId(0), idlist.GetId(1), idlist.GetId(2)])
  # polys = np.array(polys, dtype=int)
  
  # def nparray_from_vtkarray(vtkarr: vtk.vtkArray) -> np.array:
  #   ncomp = vtkarr.GetNumberOfComponents()
  #   ret = np.array([vtkarr.GetTuple(i)] for i in range(vtkarr.GetNumberOfTuples()))
  #   return ret if ncomp > 1 else ret.flatten()

  # pressure_np = nparray_from_vtkarray(polydata.GetPointData().GetArray("pressure"))
  # velocity_np = nparray_from_vtkarray(polydata.GetPointData().GetArray("velocity"))

  # print(points_np)
  # print(polys)

  # add field_data (metadata)
  meta = vtk.vtkStringArray()
  meta.SetName("experiment name")
  meta.InsertNextValue("CFD test")
  polydata.GetFieldData().AddArray(meta)
  polydata.GetPointData().SetActiveScalars("pressure")

  # export
  # specify which array is the "active scalars" to link LUT
  writer = vtk.vtkPolyDataWriter()
  writer.SetLookupTableName("test_lut")
  writer.SetFileName("output.vtk")
  writer.SetInputData(polydata)
  writer.SetFileTypeToASCII()
  writer.Write()

  # put it all together (vtkMapper is an object that represents geometry and other types of visualization data)
  # 1. polygon (mapped actor)
  # 2. material (mapped actor) (vtk use phong/blinn material model btw)
  # 3. light source (scene)
  # 4. camera (scene)
  # 5. model proxy

  # test plot

  # pyvista
  # mesh = pv.wrap(polydata)
  # mesh.plot()

  # vtk
  mapper_1 = vtk.vtkPolyDataMapper()
  mapper_1.SetInputData(polydata)
  actor_1 = vtk.vtkActor()
  actor_1.SetMapper(mapper_1)

  # if polydata has many points, using vtkGlyph3D can be slow, consider vtkGlyph3DMapper (faster, GPU-based)
  mapper_2 = vtk.vtkPolyDataMapper()
  mapper_2.SetInputConnection(glyph.GetOutputPort())
  actor_2 = vtk.vtkActor()
  actor_2.SetMapper(mapper_2)
  actor_2.SetUserTransform(actor_1.GetUserTransform())
  def sync_glyphs(caller, event):
    # actor_2.SetUserTransform(actor_1.GetUserTransform())
    actor_2.SetUserMatrix(actor_1.GetMatrix())
    
  # glyph_mapper = vtk.vtkGlyph3DMapper()
  # glyph_mapper.SetInputData(polydata)
  # glyph_mapper.SetSourceConnection(arrow_source.GetOutputPort())
  # glyph_mapper.SetOrientationArray("vectors")  # name of your vector array
  # glyph_mapper.SetScaleArray("vectors")
  # glyph_mapper.SetScaleModeToScaleByVector()

  rend = vtk.vtkRenderer() 
  rend.AddActor(actor_1)
  rend.AddActor(actor_2)
  rend.SetBackground(0.1,0.1,0.2)
  rend_window = vtk.vtkRenderWindow()
  rend_window.AddRenderer(rend)
  rend_window.SetSize(800,600)

  style = vtk.vtkInteractorStyleTrackballActor()
  # style = vtk.vtkInteractorStyleRubberBandZoom()
  interactor = vtk.vtkRenderWindowInteractor()
  interactor.SetRenderWindow(rend_window)
  interactor.SetInteractorStyle(style)
  interactor.AddObserver("InteractionEvent", sync_glyphs)

  rend_window.Render()
  interactor.Start()

if __name__ == "__main__":
  main()
