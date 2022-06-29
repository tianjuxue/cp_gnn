import damask
import meshio
import numpy as np
import os


def generate_grid():
    size = np.ones(3)*1e-5
    cells = [64,64,64]
    N_grains = 200
    seeds = damask.seeds.from_random(size,N_grains,cells)
    grid = damask.Grid.from_Voronoi_tessellation(cells,size,seeds)
    grid.save(f'data/vti/Polycystal_{N_grains}_{cells[0]}x{cells[1]}x{cells[2]}')
    


def test_read_grid():
    msh_file_name = f'data/grid/simulation_fd_single_layer_030.msh'
    mesh = meshio.read(msh_file_name)
    mesh.write(vtu_file_name)
    oris = mesh.cell_data['gmsh:physical'].reshape()
 

def test_mesh_solver():
    os.system(f'DAMASK_mesh -l tensionZ.load -g mesh.msh --workingdirectory ./data/damask/mesh_solver')


def test_grid_solver():
    os.system(f'mpiexec -n 4 DAMASK_grid --load shearXY.yaml --geom selected.vti --workingdirectory ./data/damask/grid_solver')


def select_subdomain():
    offset_x = 0.5
    offset_y = 0.1
    # TODO
    offset_z = 0.05 - 1e-8
    select_x = 0.2
    select_y = 0.2
    select_z = 0.05
    Nx_s = 80
    Ny_s = 80
    Nz_s = 20

    x = np.linspace(offset_x, offset_x + select_x, Nx_s + 1)
    y = np.linspace(offset_y, offset_y + select_y, Ny_s + 1)
    z = np.linspace(offset_z, offset_z + select_z, Nz_s + 1)

    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')

    points_select = np.vstack([xx.reshape(-1), yy.reshape(-1), zz.reshape(-1)]).T

    print(f"Start reading vtu...")
    filepath_raw = f'data/vtu/u030.vtu'
    # filepath_raw = f'data/msh/domain.msh'
    print(f"Finish reading vtu...")

    mesh = meshio.read(filepath_raw)
    points = mesh.points
    cells =  mesh.cells_dict['hexahedron']
    
    cell_points = np.take(points, cells, axis=0)
    centroids = np.mean(cell_points, axis=1)

    min_x, min_y, min_z = np.min(points[:, 0]), np.min(points[:, 1]), np.min(points[:, 2])
    max_x, max_y, max_z = np.max(points[:, 0]), np.max(points[:, 1]), np.max(points[:, 2])
    domain_length = max_x - min_x
    domain_width = max_y - min_y
    domain_height = max_z - min_z

    Nx = round(domain_length / (points[1, 0] - min_x))
    Ny = round(domain_width / (points[Nx + 1, 1]) - min_y)
    Nz = round(domain_height / (points[(Nx + 1)*(Ny + 1), 2]) - min_z)
    tick_x, tick_y, tick_z =  domain_length / Nx, domain_width / Ny, domain_height / Nz  

    assert Nx*Ny*Nz == len(cells)

    indx = np.round((points_select[:, 0] - min_x - tick_x / 2.) / tick_x)
    indy = np.round((points_select[:, 1] - min_y - tick_y / 2.) / tick_y)
    indz = np.round((points_select[:, 2] - min_z - tick_z / 2.) / tick_z)
    total_ind = np.array(indx + indy * Nx + indz * Nx * Ny, dtype=np.int32)

    cell_ori_inds = mesh.cell_data['ori_inds'][0]

    select_cell_ori_inds = np.take(cell_ori_inds, total_ind, axis=0)

    grid = damask.Grid(material=select_cell_ori_inds.reshape(xx.shape), size=(select_x, select_y, select_z), origin=np.array([offset_x, offset_y, offset_z]))

    grid.save(f'data/vti/selected.vti')


if __name__ == "__main__":
    generate_grid()
    # test_read_grid()
    # test_mesh_solver()
    # test_grid_solver()
    # select_subdomain()
