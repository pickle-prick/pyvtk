import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkRenderingCore import (
  vtkActor,
  vtkDataSetMapper,
  vtkPolyDataMapper,
  vtkRenderWindow,
  vtkRenderWindowInteractor,
  vtkRenderer
)

def main():
  colors = vtkNamedColors()
  # Set the background color.
  bkg = map(lambda x: x / 255.0, [26, 51, 102, 255])
  colors.SetColor("BkgColor", *bkg)

  sphere = vtkSphereSource()
  sphere.SetPhiResolution(12*2)
  sphere.SetThetaResolution(12*2)

  colorIt = vtkElevationFilter()
  colorIt.SetInputConnection(sphere.GetOutputPort())
  colorIt.SetLowPoint(0,0,-1)
  colorIt.SetHighPoint(0,0,1)

  mapper = vtkDataSetMapper()
  mapper.SetInputConnection(colorIt.GetOutputPort())

  actor = vtkActor()
  actor.SetMapper(mapper)

  # Create the graphics structure. The renderer renders into the render
  # window. The render window interactor captures mouse events and will
  # perform appropriate camera or actor manipulation depending on the
  # nature of the events.
  ren = vtkRenderer()
  renWin = vtkRenderWindow()
  renWin.AddRenderer(ren)
  iren = vtkRenderWindowInteractor()
  iren.SetRenderWindow(renWin)

  # Add the actors to the renderer, set the background and size
  ren.AddActor(actor)
  ren.SetBackground(colors.GetColor3d("BkgColor"))
  renWin.SetSize(1000, 1000)
  renWin.SetWindowName('CylinderExample')

  # This allows the interactor to initalize itself. It has to be
  # called before an event loop.
  iren.Initialize()

  # We'll zoom in a little by accessing the camera and invoking a "Zoom"
  # method on it.
  ren.ResetCamera()
  ren.GetActiveCamera().Zoom(1.5)
  renWin.Render()

  # Start the event loop.
  iren.Start()

if __name__ == '__main__':
  main()
