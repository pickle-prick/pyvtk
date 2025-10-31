#!/usr/bin/env python3

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkFiltersModeling import vtkRotationalExtrusionFilter
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer and Interactor.

    ren = vtkRenderer(background=colors.GetColor3d('Burlywood'))
    ren_win = vtkRenderWindow(size=(640, 512), window_name='Spring')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create the spring profile (a circle).
    points = vtkPoints()
    points.InsertPoint(0, 1.0, 0.0, 0.0)
    points.InsertPoint(1, 1.0732, 0.0, -0.1768)
    points.InsertPoint(2, 1.25, 0.0, -0.25)
    points.InsertPoint(3, 1.4268, 0.0, -0.1768)
    points.InsertPoint(4, 1.5, 0.0, 0.00)
    points.InsertPoint(5, 1.4268, 0.0, 0.1768)
    points.InsertPoint(6, 1.25, 0.0, 0.25)
    points.InsertPoint(7, 1.0732, 0.0, 0.1768)

    poly = vtkCellArray()
    poly.InsertNextCell(8)  # The number of points.
    for i in range(0, 8):
        poly.InsertCellPoint(i)

    profile = vtkPolyData(points=points, polys=poly)

    # Extrude the profile to make a spring.
    # Note: angle=360 * 6 corresponds to six revolutions.
    extrude = vtkRotationalExtrusionFilter(input_data=profile, resolution=360,
                                           translation=6, delta_radius=1.0,
                                           angle=360 * 6)

    normals = vtkPolyDataNormals(feature_angle=60)

    mapper = vtkPolyDataMapper()
    extrude >> normals >> mapper

    spring = vtkActor(mapper=mapper)
    spring.property.color = colors.GetColor3d("PowderBlue")
    spring.property.diffuse = 0.7
    spring.property.specular = 0.4
    spring.property.specular_power = 20
    spring.property.backface_culling = True

    # Add the actor to the renderer, set the background and size.
    ren.AddActor(spring)

    ren.ResetCamera()
    ren.active_camera.Azimuth(90)

    # Render the image.
    ren_win.Render()
    iren.Start()


if __name__ == '__main__':
    main()
