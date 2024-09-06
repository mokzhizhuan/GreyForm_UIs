import vtk

# Create a sphere source with a fixed radius
sphere_source = vtk.vtkSphereSource()
sphere_source.SetRadius(0.5)  # Set a fixed radius for the sphere
sphere_source.SetThetaResolution(30)
sphere_source.SetPhiResolution(30)
sphere_source.Update()

# Create a cube source smaller than the sphere
cube_source = vtk.vtkCubeSource()
cube_source.SetXLength(0.4)  # X length of the cube
cube_source.SetYLength(0.4)  # Y length of the cube
cube_source.SetZLength(0.4)  # Z length of the cube
cube_source.Update()

# Create an outline filter from the cube source
outline_filter = vtk.vtkOutlineFilter()
outline_filter.SetInputConnection(cube_source.GetOutputPort())

# Create a tube filter to add thickness to the outline
tube_filter = vtk.vtkTubeFilter()
tube_filter.SetInputConnection(outline_filter.GetOutputPort())
tube_filter.SetRadius(0.02)  # Set the radius of the tube (thickness)
tube_filter.SetNumberOfSides(12)  # Optional: set the number of sides for the tube (for smoother appearance)

# Create a mapper for the thickened outline
outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInputConnection(tube_filter.GetOutputPort())

# Create an actor for the thickened outline
outline_actor = vtk.vtkActor()
outline_actor.SetMapper(outline_mapper)
outline_actor.GetProperty().SetColor(1, 0, 0)  # Optional: set the color of the outline to red

# Create a mapper for the sphere
sphere_mapper = vtk.vtkPolyDataMapper()
sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

# Create an actor for the sphere
sphere_actor = vtk.vtkActor()
sphere_actor.SetMapper(sphere_mapper)
sphere_actor.GetProperty().SetColor(1, 0, 0)  # Set the color of the sphere to red
sphere_actor.GetProperty().SetOpacity(0.5)  # Set the sphere to be semi-transparent

# Create a renderer and add both actors
renderer = vtk.vtkRenderer()
renderer.AddActor(outline_actor)
renderer.AddActor(sphere_actor)

# Create a render window and add the renderer
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor and set the render window
render_interactor = vtk.vtkRenderWindowInteractor()
render_interactor.SetRenderWindow(render_window)

# Start the interaction
render_window.Render()
render_interactor.Start()
