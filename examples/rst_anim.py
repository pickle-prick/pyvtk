from ansys.mapdl import reader as pymapdl_reader
from ansys.mapdl.reader import examples
import numpy as np

import vtk
import time
from dataclasses import dataclass
import typing as t

@dataclass
class Frame:
  index:int
  timestep:float
  xml:str

def render_worker():
  global clock_begin
  global clock_started

  c = vtk.vtkCylinderSource()
  c.SetResolution(8)
  c.Update()

  reader = vtk.vtkXMLPolyDataReader()
  reader.ReadFromInputStringOn()

  # mapper.SetInputConnection(c.GetOutputPort())
  mapper = vtk.vtkPolyDataMapper()
  # mapper.SetArrayName("Colors")
  # mapper.SetScalarModeToUsePointData()
  mapper.SetScalarVisibility(1)
  mapper.SelectColorArray("Colors")
  mapper.SetScalarMode(vtk.VTK_SCALAR_MODE_USE_POINT_FIELD_DATA)
  # mapper.SetScalarMode(vtk.VTK_SCALAR_MODE_USE_POINT_DATA) # only active scalar
  mapper.SetColorModeToDirectScalars()
  mapper.SetInputData(c.GetOutput(0))
  actor = vtk.vtkActor()
  actor.SetMapper(mapper)

  # render
  ren = vtk.vtkRenderer()
  ren.SetBackground(0.9, 0.9, 0.9)
  win = vtk.vtkRenderWindow()
  win.AddRenderer(ren)
  iren = vtk.vtkRenderWindowInteractor()
  iren.SetRenderWindow(win)
  ren.AddActor(actor)
  win.SetSize(1024,512)

  def update_callback(caller:vtk.vtkObject, event_id:int):
    # NOTE: do this to release python GIL lock
    time.sleep(0)

  # iren.AddObserver("TimerEvent", update_callback)
  iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
  iren.Initialize()
  # timer_id = iren.CreateRepeatingTimer(1)
  # iren.Start()

  while not stop_evt.is_set():
    try:
      with lck:
        # Testing
        # for idx, f in enumerate(frames):
        #   prev = None
        #   if idx > 0: prev = frames[idx-1]
        #   next = None
        #   if idx < (len(frames)-1): next = frames[idx+1]
        #   if prev: assert f.timestep > prev.timestep
        #   if next: assert f.timestep < next.timestep

        if clock_started:
          elapsed = time.perf_counter()-clock_begin
          # time_scale = 0.10
          time_scale = 1.5
          elapsed = elapsed*time_scale

          # duration = frames[-1].timestep
          duration = 4.0
          if elapsed > duration:
            while elapsed > duration:
              elapsed -= duration
            if elapsed < 0: elapsed = 0
            clock_begin = time.perf_counter()

          # FIXME: use TemporalInterpolator
          # find the frame
          frame = None
          frame_idx = -1
          for idx, f in enumerate(frames):
            if (elapsed) < f.timestep:
              print(f"{elapsed} => {f.timestep}")
              # assert False
              break
            else:
              frame = f 
              frame_idx = idx

          if frame:
            print(f"Frame {frame_idx} picked")
            reader.SetInputString(frame.xml)
            reader.Update()
            mapper.SetInputData(reader.GetOutput())
            mapper.Modified()
            mapper.Update()
          
        iren.ProcessEvents()
        win.Render()
        # NOTE: do this to release python GIL lock
        time.sleep(0)
        # iren.Start()
        # iren.DestroyTimer(timer_id)
    except Exception as e:
      print(e)
      raise

def main():
  frames:t.List[Frame] = []

  # read file
  filename = "data/file-nocompression.rst"
  ret = pymapdl_reader.read_binary(filename)

  # parse frame
  grid = ret.grid

  ###################
  ## Render

  mapper.SetInputConnection(c.GetOutputPort())
  mapper = vtk.vtkPolyDataMapper()
  # mapper.SetArrayName("Colors")
  # mapper.SetScalarModeToUsePointData()
  mapper.SetScalarVisibility(1)
  mapper.SelectColorArray("Colors")
  mapper.SetScalarMode(vtk.VTK_SCALAR_MODE_USE_POINT_FIELD_DATA)
  # mapper.SetScalarMode(vtk.VTK_SCALAR_MODE_USE_POINT_DATA) # only active scalar
  mapper.SetColorModeToDirectScalars()
  mapper.SetInputData(c.GetOutput(0))
  actor = vtk.vtkActor()
  actor.SetMapper(mapper)

  # render
  ren = vtk.vtkRenderer()
  ren.SetBackground(0.9, 0.9, 0.9)
  win = vtk.vtkRenderWindow()
  win.AddRenderer(ren)
  iren = vtk.vtkRenderWindowInteractor()
  iren.SetRenderWindow(win)
  ren.AddActor(actor)
  win.SetSize(1024,512)

  # iren.AddObserver("TimerEvent", update_callback)
  iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
  iren.Initialize()
  # timer_id = iren.CreateRepeatingTimer(1)
  # iren.Start()

  clock_begin = time.perf_counter()
  while 1:
    elapsed = time.perf_counter()-clock_begin
    time_scale = 1.0
    elapsed = elapsed*time_scale

    # duration = frames[-1].timestep
    duration = 4.0
    if elapsed > duration:
      while elapsed > duration:
        elapsed -= duration
      if elapsed < 0: elapsed = 0
      clock_begin = time.perf_counter()

    # FIXME: use TemporalInterpolator
    # find the frame
    frame = None
    frame_idx = -1
    for idx, f in enumerate(frames):
      if (elapsed) < f.timestep:
        print(f"{elapsed} => {f.timestep}")
        # assert False
        break
      else:
        frame = f 
        frame_idx = idx

    if frame:
      print(f"Frame {frame_idx} picked")
      reader.SetInputString(frame.xml)
      reader.Update()
      mapper.SetInputData(reader.GetOutput())
      mapper.Modified()
      mapper.Update()
    
  iren.ProcessEvents()
  win.Render()
  # NOTE: do this to release python GIL lock
  time.sleep(0)
  # iren.Start()
    # iren.DestroyTimer(timer_id)

if __name__ == "__main__":
  main()