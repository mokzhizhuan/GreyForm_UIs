#load in pyvisita for 2 frames
class StLloaderpyvista(object):
    def __init__(self, meshsplot, loader, robot_cube , wall1_position):
        # starting initialize
        super().__init__()
        self.meshsplot = meshsplot
        self.loader = loader
        self.robot_cube = robot_cube
        self.wall1_position = wall1_position
        self.loadstl()

    #load frame implementation
    def loadstl(self):
        bounds = self.meshsplot.bounds  # same format as VTK: (xmin, xmax, ymin, ymax, zmin, zmax)
        x_center = (bounds[0] + bounds[1]) / 2
        y_center = (bounds[2] + bounds[3]) / 2
        z_center = (bounds[4] + bounds[5]) / 2
        parallel_scale = (bounds[3] - bounds[2])
        self.loader.camera.position = (x_center, y_center, z_center + 50)  # top-down
        self.loader.camera.focal_point = (x_center, y_center, z_center)
        self.loader.camera.up = (0, 1, 0)
        self.loader.camera.parallel_projection = True
        self.loader.camera.parallel_scale = parallel_scale
        self.loader.add_mesh(
            self.meshsplot,
            color=(230, 230, 250),
            show_edges=False,
            edge_color=(128, 128, 128),
            cmap="terrain",
            clim=[1, 3],
            name="roombuilding",
            opacity=1.0,
        )
        self.loader.add_mesh(self.robot_cube, color="blue")
        self.loader.show()
