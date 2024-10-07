#loader for pyvista frame
class StLloaderpyvista(object):
    def __init__(self, meshsplot, loader, loader_2):
        self.meshsplot = meshsplot
        self.loader = loader
        self.loader_2 = loader_2
        self.loadstl()

    def loadstl(self):
        self.loader.remove_actor("roombuilding")
        self.loader_2.remove_actor("roombuilding")
        self.loader.update()
        self.loader_2.update()
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
        self.loader_2.add_mesh(
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
        self.loader_2.show()
