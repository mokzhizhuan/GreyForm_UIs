import vtk

def create_wall_actor(position, size, color):
    """Creates a wall (rectangular plane) at a given position, size, and color."""
    # Define the plane source
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(0, 0, 0)
    plane.SetPoint1(size[0], 0, 0)  # Width
    plane.SetPoint2(0, size[1], 0)  # Height

    # Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(plane.GetOutputPort())

    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.SetPosition(position)

    return actor


# Initialize renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Wall definitions (positions, sizes, colors)
walls = {
    "front": {"position": (0, 0, 1.5), "size": (2, 2), "color": (1, 0, 0)},  # Red
    "back": {"position": (0, 0, -1.5), "size": (2, 2), "color": (0, 1, 0)},   # Green
    "top": {"position": (0, 1.5, 0), "size": (2, 2), "color": (0, 0, 1)},     # Blue
    "bottom": {"position": (0, -1.5, 0), "size": (2, 2), "color": (1, 1, 0)}, # Yellow
    "left": {"position": (-1.5, 0, 0), "size": (2, 2), "color": (1, 0, 1)},   # Magenta
    "right": {"position": (1.5, 0, 0), "size": (2, 2), "color": (0, 1, 1)},   # Cyan
    "partition1": {"position": (0.5, 0, 0), "size": (2, 2), "color": (0.5, 0.5, 0)}, # Brown
    "partition2": {"position": (-0.5, 0, 0), "size": (2, 2), "color": (0, 0.5, 0.5)}, # Teal
}

# Create and add wall actors
for wall, properties in walls.items():
    actor = create_wall_actor(
        position=properties["position"],
        size=properties["size"],
        color=properties["color"]
    )
    renderer.AddActor(actor)

# Set up the renderer
renderer.SetBackground(0.1, 0.1, 0.1)  # Dark background
render_window.SetSize(800, 600)

# Start the rendering loop
render_window.Render()
render_window_interactor.Start()
