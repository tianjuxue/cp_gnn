import numpy as np
import os
import gmsh
import meshio


def gmsh_mesh(mesh_filepath):
    '''
    References:
    https://gitlab.onelab.info/gmsh/gmsh/-/blob/master/examples/api/hex.py
    https://gitlab.onelab.info/gmsh/gmsh/-/blob/gmsh_4_7_1/tutorial/python/t1.py
    https://gitlab.onelab.info/gmsh/gmsh/-/blob/gmsh_4_7_1/tutorial/python/t3.py
    '''
    offset_x = 0.5
    offset_y = 0.1
    offset_z = 0.05
    select_x = 0.2
    select_y = 0.2
    select_z = 0.05

    # Nx_s = 80
    # Ny_s = 80
    # Nz_s = 20

    Nx_s = 40
    Ny_s = 40
    Nz_s = 10

    gmsh.initialize()
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)  # save in old MSH format
    Rec2d = True  # tris or quads
    Rec3d = True  # tets, prisms or hexas
    p = gmsh.model.geo.addPoint(offset_x, offset_y, offset_z)
    l = gmsh.model.geo.extrude([(0, p)], select_x, 0, 0, [Nx_s], [1])
    s = gmsh.model.geo.extrude([l[1]], 0, select_y, 0, [Ny_s], [1], recombine=Rec2d)
    v = gmsh.model.geo.extrude([s[1]], 0, 0, select_z, [Nz_s], [1], recombine=Rec3d)

    print(v)
    print(s)
  
    gmsh.model.geo.synchronize()

    pg_dim2_bottom = gmsh.model.addPhysicalGroup(2, [s[1][1]])
    gmsh.model.setPhysicalName(2, pg_dim2_bottom, "z0")

    pg_dim2_top = gmsh.model.addPhysicalGroup(2, [v[0][1]])
    gmsh.model.setPhysicalName(2, pg_dim2_top, "z1")

    pg_dim2_front = gmsh.model.addPhysicalGroup(2, [v[2][1]])
    gmsh.model.setPhysicalName(2, pg_dim2_front, "y0")

    pg_dim2_right = gmsh.model.addPhysicalGroup(2, [v[3][1]])
    gmsh.model.setPhysicalName(2, pg_dim2_right, "x1")

    pg_dim2_back = gmsh.model.addPhysicalGroup(2, [v[4][1]])
    gmsh.model.setPhysicalName(2, pg_dim2_back, "y1")

    pg_dim2_left = gmsh.model.addPhysicalGroup(2, [v[5][1]])
    gmsh.model.setPhysicalName(2, pg_dim2_left, "x0")

    pg_dim3_body = gmsh.model.addPhysicalGroup(3, [v[1][1]])
    gmsh.model.setPhysicalName(3, pg_dim3_body, "body")


    gmsh.model.mesh.generate(3)
    gmsh.write(mesh_filepath)
    gmsh.finalize()


def select_subdomain():
    mesh_filepath = "python/data/msh/simple.msh"
    gmsh_mesh(mesh_filepath)
  
    mesh_select = meshio.read(mesh_filepath)
    points_select = mesh_select.points
    cells_select =  mesh_select.cells_dict['hexahedron']
    cell_points_select = np.take(points_select, cells_select, axis=0)
    cell_centroids_select = np.mean(cell_points_select, axis=1)

    print(f"Start reading vtu...")
    filepath_raw = f'python/data/vtu/u030.vtu'
    print(f"Finish reading vtu...")

    mesh_domain = meshio.read(filepath_raw)
    points_domain = mesh_domain.points
    cells_domain =  mesh_domain.cells_dict['hexahedron']
    
    min_x, min_y, min_z = np.min(points_domain[:, 0]), np.min(points_domain[:, 1]), np.min(points_domain[:, 2])
    max_x, max_y, max_z = np.max(points_domain[:, 0]), np.max(points_domain[:, 1]), np.max(points_domain[:, 2])
    domain_length = max_x - min_x
    domain_width = max_y - min_y
    domain_height = max_z - min_z

    Nx = round(domain_length / (points_domain[1, 0] - min_x))
    Ny = round(domain_width / (points_domain[Nx + 1, 1]) - min_y)
    Nz = round(domain_height / (points_domain[(Nx + 1)*(Ny + 1), 2]) - min_z)
    tick_x, tick_y, tick_z =  domain_length / Nx, domain_width / Ny, domain_height / Nz  

    assert Nx*Ny*Nz == len(cells_domain)

    indx = np.round((cell_centroids_select[:, 0] - min_x - tick_x / 2.) / tick_x)
    indy = np.round((cell_centroids_select[:, 1] - min_y - tick_y / 2.) / tick_y)
    indz = np.round((cell_centroids_select[:, 2] - min_z - tick_z / 2.) / tick_z)
    total_ind = np.array(indx + indy * Nx + indz * Nx * Ny, dtype=np.int32)

    cell_ori_inds = mesh_domain.cell_data['ori_inds'][0]

    select_cell_ori_inds = np.take(cell_ori_inds, total_ind, axis=0)

    # print(mesh_select.cell_data['gmsh:physical'])
    # print(mesh_select.cell_data['gmsh:geometrical'])
    # print(mesh_select.cells_dict) 
    # print(f"len(mesh_select.cells_dict['quad']) = {len(mesh_select.cells_dict['quad'])}")
    # print(f"len(mesh_select.cells_dict['hexahedron']) = {len(mesh_select.cells_dict['hexahedron'])}")
    # print(f"len(mesh_select.cell_data['gmsh:physical'][0]) = {len(mesh_select.cell_data['gmsh:physical'][0])}")
    # print(f"len(mesh_select.cell_data['gmsh:physical'][1]) = {len(mesh_select.cell_data['gmsh:physical'][1])}")
    # print(f"len(mesh_select.cell_data['gmsh:geometrical'][0]) = {len(mesh_select.cell_data['gmsh:geometrical'][0])}")
    # print(f"len(mesh_select.cell_data['gmsh:geometrical'][1]) = {len(mesh_select.cell_data['gmsh:geometrical'][1])}")
    # print(f"len(select_cell_ori_inds) = {len(select_cell_ori_inds)}")


    mesh_select.cell_data['gmsh:physical'][1] = select_cell_ori_inds
    mesh_select.cell_data['gmsh:geometrical'][1] = select_cell_ori_inds

    mesh_select.write("python/data/msh/select.msh", file_format='gmsh22', binary=False)

    # print(mesh_select.cells_dict)
    # print(mesh_select.cell_data)
    # del mesh_select.cells_dict['quad']
    # mesh_select.cell_data['gmsh:physical'] = [select_cell_ori_inds]
    # mesh_select.cell_data['gmsh:geometrical'] = [select_cell_ori_inds]

    # TODO:
    # mesh_select.write("python/data/vtu/select.vtk", file_format='vtk42')
    mesh_select.write("python/data/vtu/select.e")


if __name__ == "__main__":
    select_subdomain()
