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
        print("STL bounds:", self.meshsplot.bounds)
        print("Cube bounds:", self.robot_cube.bounds)
        self.loader.show()
