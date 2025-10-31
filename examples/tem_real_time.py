#!/usr/bin/env python3

import math
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkFloatArray
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionWidgets import vtkCameraOrientationWidget
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
)
from vtkmodules.vtkCommonDataModel import vtkPointData


def create_temperature_array(polydata):
    """Create initial temperature field."""
    num_points = polydata.GetNumberOfPoints()
    temp = vtkFloatArray()
    temp.SetName("Temperature")
    temp.SetNumberOfValues(num_points)
    for i in range(num_points):
      x, y, z = polydata.GetPoint(i)
      temp.SetValue(i, (z + 5.0) / 10.0 * 100.0)  # 0–100
    polydata.GetPointData().SetScalars(temp)
    return temp


def main():
    colors = vtkNamedColors()

    # Sphere geometry
    sphere_source = vtkSphereSource(center=(0.0, 0.0, 0.0), radius=5.0,
                                    phi_resolution=50, theta_resolution=50)
    sphere_source.Update()
    sphere = sphere_source.GetOutput()

    # Create initial temperature field
    temperature = create_temperature_array(sphere)

    # Mapper setup
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(sphere)
    mapper.SetScalarModeToUsePointData()
    mapper.SetScalarRange(temperature.GetRange())
    mapper.ScalarVisibilityOn()

    actor = vtkActor()
    actor.SetMapper(mapper)

    renderer = vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('ParaViewBkg'))

    render_window = vtkRenderWindow()
    render_window.SetSize(600, 600)
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    renderer.AddActor(actor)

    # Orientation widget
    cow = vtkCameraOrientationWidget()
    cow.SetParentRenderer(renderer)
    cow.SetInteractor(interactor)
    cow.On()

    # --- Real-time update logic ---
    frame = {"t": 0}  # use dict to make mutable in closure

    def update_temperature(obj, event):
      """Timer callback: update temperature dynamically."""
      frame["t"] += 1
      t = frame["t"]

      num_points = sphere.GetNumberOfPoints()
      for i in range(num_points):
          x, y, z = sphere.GetPoint(i)
          # Simulate some dynamic variation (wave pattern)
          temp = (math.sin(t * 0.05 + x * 0.3 + y * 0.3) + 1) * 50.0
          temperature.SetValue(i, temp)

      temperature.Modified()   # notify VTK the data changed
      sphere.Modified()        # mark dataset modified
      render_window.Render()   # re-render scene

    # Add timer event every 100ms
    interactor.AddObserver("TimerEvent", update_temperature)
    interactor.CreateRepeatingTimer(100)

    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()

