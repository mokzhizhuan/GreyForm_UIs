import pyvista as pv

# plotting setup
theme = pv.themes.DocumentTheme()
theme.show_edges = True

# create dummy meshes
mesh1 = pv.Cylinder(resolution=8, center=(0, 0, 0.5), direction=(0, 0, 1), capping=False).triangulate().subdivide(3)
mesh2 = pv.Cylinder(resolution=16, center=(0, 0, -0.5), direction=(0, 0, 1), capping=False).triangulate().subdivide(3)
mesh2.rotate_z(360/32, inplace=True)

# plot them together
plotter = pv.Plotter(theme=theme)
plotter.add_mesh(mesh1, color='pink')
plotter.add_mesh(mesh2, color='cyan')
plotter.show()

edge_kwargs = dict(
    manifold_edges=False,
    non_manifold_edges=False,
    feature_edges=False,
    boundary_edges=True,
)

def tag_and_extract(mesh):
    """The work we have to do for both meshes.

    This adds some scalars and extracts cells involved in the common
    edge of both meshes. You'll need to tweak the filtering that selects
    the appropriate feature edges below, see the "first hack" comment.

    This will also modify the input mesh by deleting edge points and
    the cells containing them. If you want to preserve your input
    mesh, pass in a copy, and use that copy after calling this
    function.

    """
    # grab interesting edges
    # add scalars to keep track of point and cell indices after extraction
    mesh.point_data['point_inds'] = range(mesh.n_points)
    mesh.cell_data['cell_inds'] = range(mesh.n_cells)
    mesh_edges = mesh.extract_feature_edges(**edge_kwargs)

    # first hack:
    # you'll need some way to locate corresponding pairs of edges; this is specific to your problem
    # in this example there's only one pair of edges so we'll clip with two planes
    mesh_edges = mesh_edges.clip('z', origin=mesh1.center).clip('-z', origin=mesh2.center)

    # extract original cells containing edge lines
    mesh_edge_cells = mesh.extract_points(mesh_edges['point_inds'])

    # delete edge points along with their containing cells
    # the example data is already triangulated, otherwise we'd have to triangulate it
    # (or have to do more work)
    mesh.remove_points(mesh_edges['point_inds'], inplace=True)

    return mesh_edge_cells

mesh1_edge_cells = tag_and_extract(mesh1)
mesh2_edge_cells = tag_and_extract(mesh2)

# triangulate the edge strip
edge_strip = (mesh1_edge_cells + mesh2_edge_cells).delaunay_3d().extract_surface()

# second hack that needs fitting to your problem: remove capping
normals = edge_strip.compute_normals().cell_data['Normals']
horizontals = abs(normals[:, -1]) < 0.9  # has lots of leeway
edge_strip = edge_strip.extract_cells(horizontals).extract_surface()

# merge meshes
merged = mesh1 + edge_strip + mesh2

# plot the result
plotter = pv.Plotter(theme=theme)
plotter.add_mesh(merged)
plotter.show()