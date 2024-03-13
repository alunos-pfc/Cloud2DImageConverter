# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_spherical_projections.ipynb.

# %% auto 0
__all__ = ['color_map', 'spherical_projection', 'colored_matrix_with_label']

# %% ../nbs/01_spherical_projections.ipynb 3
from . import data

# %% ../nbs/01_spherical_projections.ipynb 4
import matplotlib.pyplot as plt
import numpy as np

# %% ../nbs/01_spherical_projections.ipynb 5
color_map = dict(data.color_map)

# %% ../nbs/01_spherical_projections.ipynb 7
def spherical_projection(point_cloud, proj_fov_up, proj_fov_down, proj_W, proj_H):
    label_check = False
    
    # laser parameters
    fov_up = proj_fov_up / 180.0 * np.pi      # field of view up in rad
    fov_down = proj_fov_down / 180.0 * np.pi  # field of view down in rad
    fov = abs(fov_down) + abs(fov_up)  # get field of view total in rad

    # get point_cloud components
    scan_x = point_cloud[:, 0]
    scan_y = point_cloud[:, 1]
    scan_z = point_cloud[:, 2]
    reflec = point_cloud[:, 3]

    if point_cloud.shape[-1] == 5:
        labels = point_cloud[:, 4]
        label_check = True

    R = np.sqrt(scan_x**2 + scan_y**2 + scan_z**2)
    
    # get angles of all points
    yaw = -np.arctan2(scan_y, scan_x)
    pitch = np.arcsin(scan_z / R)

    # get projections in image coords
    proj_x = 0.5 * (yaw / np.pi + 1.0)          # in [0.0, 1.0]
    proj_y = 1.0 - (pitch + abs(fov_down)) / fov        # in [0.0, 1.0]

    # scale to image size using angular resolution
    proj_x *= proj_W                              # in [0.0, W]
    proj_y *= proj_H                              # in [0.0, H]

    # round and clamp for use as index
    proj_x = np.floor(proj_x)
    proj_x = np.minimum(proj_W - 1, proj_x)
    proj_x = np.maximum(0, proj_x).astype(np.int32)   # in [0,W-1]

    proj_y = np.floor(proj_y)
    proj_y = np.minimum(proj_H - 1, proj_y)
    proj_y = np.maximum(0, proj_y).astype(np.int32)   # in [0,H-1]

    # setup the image matrix 
    image_matrix_reflectance = np.zeros((proj_H, proj_W))
    image_matrix_depth = np.zeros((proj_H, proj_W))
    image_matrix_mask = np.zeros((proj_H, proj_W))
    
    # reflectance matrix
    for x, y, i in zip(proj_x, proj_y, reflec):
        image_matrix_reflectance[y, x] = i

    # depth matrix
    for x, y, i in zip(proj_x, proj_y, R):
        image_matrix_depth[y, x] = i
        
    # labels matrix
    if label_check:
        for x, y, i in zip(proj_x, proj_y, labels):
            image_matrix_mask[y, x] = i
    
    return image_matrix_reflectance, image_matrix_depth, image_matrix_mask

# %% ../nbs/01_spherical_projections.ipynb 8
'''
- Substitui as keys da matriz de label pela respectiva cor do dicionário color_map
- Retorna a matriz de label no formato (64, 1024, 3)
'''
def colored_matrix_with_label(image_matrix_with_label):
    colored_matrix =  np.empty(image_matrix_with_label.shape + (3,), dtype=np.uint8)
    
    for key, value in color_map.items():
        indices = np.where(image_matrix_with_label == key)
        colored_matrix[indices] = value
    
    image_matrix_with_label = colored_matrix

    return image_matrix_with_label
