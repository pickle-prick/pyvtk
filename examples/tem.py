#!/usr/bin/env python3

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
    vtkRenderer, vtkProperty
)
from vtkmodules.vtkCommonDataModel import vtkPointData


def main():
    colors = vtkNamedColors()
    colors.SetColor("ParaViewBkg", 82, 87, 110, 255)

    # Create a sphere.
    sphere_source = vtkSphereSource(center=(0.0, 0.0, 0.0), radius=5.0,
                                    phi_resolution=50, theta_resolution=50)
    sphere_source.Update()
    sphere = sphere_source.GetOutput()

    # Create a temperature array for each point
    num_points = sphere.GetNumberOfPoints()
    temperature = vtkFloatArray()
    temperature.SetName("Temperature")
    temperature.SetNumberOfValues(num_points)

    # Example: assign temperature based on Z coordinate (simulating gradient)
    for i in range(num_points):
        x, y, z = sphere.GetPoint(i)
        temp = (z + 5.0) / 10.0 * 100.0  # scale from 0–100
        temperature.SetValue(i, temp)

    # Attach to point data
    sphere.GetPointData().SetScalars(temperature)

    # Mapper and color setup
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(sphere)
    mapper.SetScalarRange(temperature.GetRange())
    mapper.SetColorModeToMapScalars()
    mapper.SetScalarModeToUsePointData()
    mapper.ScalarVisibilityOn()

    actor_prop = vtkProperty()
    actor_prop.SetEdgeVisibility(True)
    actor = vtkActor()
    actor.SetProperty(actor_prop)
    actor.SetMapper(mapper)

    # Rendering setup
    renderer = vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('ParaViewBkg'))
    render_window = vtkRenderWindow()
    render_window.SetSize(600, 600)
    render_window.SetWindowName('Sphere Temperature')
    render_window.AddRenderer(renderer)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    renderer.AddActor(actor)

    # Optional: orientation widget
    cow = vtkCameraOrientationWidget()
    cow.SetParentRenderer(renderer)
    cow.SetInteractor(interactor)
    cow.On()

    # Show
    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    main()

