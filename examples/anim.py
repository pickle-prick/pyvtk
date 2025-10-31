#!/usr/bin/env python3
import numpy as np

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkAnimationCue
)
from vtkmodules.vtkCommonDataModel import vtkAnimationScene
from vtkmodules.vtkFiltersSources import (
    vtkConeSource,
    vtkSphereSource,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor
)


def get_program_parameters():
    import argparse
    description = 'Animate Actors.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-r', '--real_time', action='store_true',
                        help='Sets the scene mode to real time instead of the default sequence mode.')
    args = parser.parse_args()
    return args.real_time


def main():
    scene_mode = get_program_parameters()

    colors = vtkNamedColors()
    cone_color = colors.GetColor3d('Tomato')
    sphere_color = colors.GetColor3d('Banana')
    background_color = colors.GetColor3d('Peacock')

    # Create the Renderer, RenderWindow and RenderWindowInteractor.
    ren = vtkRenderer(background=background_color)
    ren_win = vtkRenderWindow(window_name='AnimateActors')
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    # Create a cone.
    cone_mapper = vtkPolyDataMapper()
    vtkConeSource(resolution=31, height=1) >> cone_mapper
    cone_actor = vtkActor(mapper=cone_mapper)
    cone_actor.property.color = cone_color

    # Create a sphere.
    sphere_property = vtkProperty(color=sphere_color, diffuse=0.7, specular=0.3, specular_power=30.0)
    sphere_mapper = vtkPolyDataMapper()
    vtkSphereSource(phi_resolution=31, theta_resolution=31) >> sphere_mapper
    sphere_actor = vtkActor(mapper=sphere_mapper, property=sphere_property)

    # Create an Animation Scene.
    scene = vtkAnimationScene(loop=0, frame_rate=5, start_time=0, end_time=20)
    if scene_mode:
        scene.SetModeToRealTime()
        print('real-time mode')
    else:
        scene.SetModeToSequence()
        print('sequence mode')

    # Create an Animation Cue for each actor.
    cue1 = vtkAnimationCue(start_time=5, end_time=23)
    scene.AddCue(cue1)
    cue2 = vtkAnimationCue(start_time=1, end_time=10)
    scene.AddCue(cue2)

    # Create cue animators.
    sphere_animator = ActorAnimator(sphere_actor, start_position=(0, 0, 0), end_position=(0.5, 0.5, 0.5))
    cone_animator = ActorAnimator(cone_actor, start_position=(0, 0, 0), end_position=(-1, -1, -1))
    # Create Cue observers.
    # You can assign these to variables but there seems to be no need to do this.
    AnimationCueObserver(sphere_animator, cue1, ren, ren_win)
    AnimationCueObserver(cone_animator, cue2, ren, ren_win)

    ren.AddActor(cone_actor)
    ren.AddActor(sphere_actor)
    ren_win.Render()
    ren.ResetCamera()
    ren.active_camera.Dolly(0.5)
    ren.ResetCameraClippingRange()

    ren_win.Render()

    scene.Play()
    scene.Stop()

    iren.Start()


class AnimationCueObserver:
    def __init__(self, animator, cue, renderer, ren_win):
        self.animator = animator
        self.cue = cue
        self.renderer = renderer
        self.ren_win = ren_win
        self.add_observers_to_cue()

    def __call__(self, info, event):
        if self.animator and self.renderer:
            if event == 'StartAnimationCueEvent':
                self.animator.start()
            if event == 'AnimationCueTickEvent':
                self.animator.tick(info)
            if event == 'EndAnimationCueEvent':
                self.animator.end()
            if self.ren_win:
                self.ren_win.Render()

    def add_observers_to_cue(self):
        self.cue.AddObserver('StartAnimationCueEvent', self)
        self.cue.AddObserver('EndAnimationCueEvent', self)
        self.cue.AddObserver('AnimationCueTickEvent', self)


class ActorAnimator:
    def __init__(self, actor, start_position, end_position):
        self.actor = actor
        self.start_position = start_position
        self.end_position = end_position

    def start(self):
        self.actor.SetPosition(self.start_position)

    def tick(self, info):
        t = (info.animation_time - info.start_time) / (info.end_time - info.start_time)
        delta_pos = (np.array(self.end_position) - np.array(self.start_position)) * t
        pos = np.array(self.start_position) + delta_pos
        self.actor.SetPosition(pos.tolist())

    def end(self):
        # Don't remove the actor for the regression image.
        # ren.RemoveActor(self.actor)
        self.actor.SetPosition(self.end_position)


if __name__ == '__main__':
    main()

