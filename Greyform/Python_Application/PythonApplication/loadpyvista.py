#load in pyvisita for 2 frames
class StLloaderpyvista(object):
    def __init__(self, meshsplot, loader):
        # starting initialize
        super().__init__()
        self.meshsplot = meshsplot
        self.loader = loader
        self.loadstl()

    #load 2 frame implementation
    def loadstl(self):
        self.loader.remove_actor("roombuilding")
        self.loader.update()
        self.loader.add_mesh(
            self.meshsplot,
            color=(230, 230, 250),
            show_edges=False,
            edge_color=(128, 128, 128),
            cmap="terrain",
            clim=[1, 3],
            name="roombuilding",
            opacity="linear",
        )
        self.loader.show()
