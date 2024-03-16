# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_image_generator.ipynb.

# %% auto 0
__all__ = ['define_range', 'do_projection', 'save_image', 'create_images']

# %% ../nbs/02_image_generator.ipynb 2
from . import spherical_projection as sp
from . import data
from matplotlib import pyplot as plt
from tqdm import tqdm
from PIL import Image
import numpy as np
import pickle 
import shutil
import time
import os

# %% ../nbs/02_image_generator.ipynb 3
def define_range(batch, batch_size, max_len):
    start = batch - batch_size
    end = batch
    if (max_len - batch) < batch_size:
        end = max_len
    return start, end

# %% ../nbs/02_image_generator.ipynb 4
def do_projection(point_cloud, fov_up, fov_down, width, height, is_label):
    projection_dict = {"reflectance": [], "depth": []}
    if is_label:
        projection_dict["label"] = []
    for points in point_cloud:
        reflectance, depth, mask = sp.spherical_projection(points, fov_up, fov_down, width, height)
        projection_dict["reflectance"].append(reflectance)
        projection_dict["depth"].append(depth)
        if is_label:
            projection_dict["label"].append(mask)
    return projection_dict

# %% ../nbs/02_image_generator.ipynb 5
def save_image(matrix, results_folder, save_path):
    img = Image.fromarray(matrix)
    final_path = os.path.join(results_folder+save_path)
    file_number = len(os.listdir(final_path)) + 1
    file_name = f"{final_path}/{file_number:06d}.png"
    img.save(file_name)

def create_images(projection_dict, results_folder):
    reflectance = projection_dict["reflectance"]
    depth = projection_dict["depth"]
    labels = projection_dict.get("label", [])
    # Itera sobre cada posição do dicionário agrupando junto as matrizes de mesmo indice
    for zip_dict in zip(reflectance, depth, labels) if "label" in projection_dict else zip(reflectance, depth):
        # Alterna entre as chaves e os indices respectivos a cada chave
        aux_dict = {}
        for index, key in enumerate(projection_dict.keys()):
            matrix = zip_dict[index]  
            if key == "reflectance":
                matrix = matrix * 255
                matrix = matrix.astype(np.uint8)
            elif key == "depth":
                matrix = ((matrix - matrix.min()) / (matrix.max() - matrix.min())) * 255
                matrix = matrix.astype(np.uint8)
            elif key == "label":
                matrix = np.vectorize(data.learning_map.get)(matrix)
                matrix = matrix.astype(np.uint8)
            aux_dict[key] = matrix
        save_image(aux_dict["reflectance"], results_folder, "reflectance")
        save_image(aux_dict["depth"], results_folder, "depth")
        if "label" in aux_dict:
            save_image(aux_dict["label"], results_folder, "segmentation_mask")
