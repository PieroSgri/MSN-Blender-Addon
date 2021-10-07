import bpy
import random
import os
import sys

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from pathlib import Path

import logging
logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    import open3d as o3d
    import numpy as np
    import torch
except ModuleNotFoundError as err:
    logging.debug(f"Errore import moduli in MSNImportPointCloud: {err}")


def resample_pcd(pcd, n):
    """Drop or duplicate points so that pcd has exactly n points"""
    
    idx = np.random.permutation(pcd.shape[0])
    if idx.shape[0] < n:
        idx = np.concatenate([idx, np.random.randint(pcd.shape[0], size = n - pcd.shape[0])])
    return pcd[idx[:n]]


def read_pcd(directory, file_list):
    """Read pcd file and prepare tensor"""
            
    partial = torch.zeros((50, 5000, 3), device='cuda')
    for j in range(50):
        pcd_file = os.path.join(directory, file_list[j])
        pcd_file = pcd_file.replace("\\", "/")
        print("pcd file:", pcd_file)
        pcd = o3d.io.read_point_cloud(pcd_file)
        print(pcd)
        partial[j, :, :] = torch.from_numpy(resample_pcd(np.array(pcd.points), 5000))

    idx = random.randint(0, 49)
    print(partial[idx].data.cpu().numpy())
    
    save_path = 'partial_pc.txt'
    np.savetxt(save_path, partial[idx].data.cpu().numpy(), fmt="%1.20s")
    return save_path


def import_pc(file_path):
    """Import point cloud data and return the object"""
    ob_name = "Point_Cloud"
    # Create new mesh and a new object
    me = bpy.data.meshes.new(ob_name)
    ob = bpy.data.objects.new(ob_name, me)
    
    cords_list = []
    with open(file_path, 'r') as file:
        logging.debug("Leggendo il file: " + file_path)
        for cords in file:
            temp = []       
            for cord in cords.split():
                cord = float(cord)
                temp.append(cord)
            cord_tuple = (temp[0], temp[1], temp[2])
            cords_list.append(cord_tuple)

    # Make a mesh from a list of vertices/edges/faces
    me.from_pydata(cords_list, edges=[], faces=[])

    # Display name and update the mesh
    ob.show_name = True
    me.update()
    return ob


class MSNImportPointCloud(Operator, ImportHelper):
    bl_idname = "msn.import_point_cloud"
    bl_label = "Import PCD file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
        default='*.txt;*.pcd;*',
        options={'HIDDEN'} )
    
    
    def execute(self, context):
               
        directory = Path(self.filepath).parent
        print('Selected directory:', directory)
        file_list = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        file_list.sort()
        for i in file_list:
            print(i) 
            
        filepath = read_pcd(directory, file_list)
        # Create the object
        pc = import_pc(filepath)
        # Link object to the active collection
        bpy.context.collection.objects.link(pc)
        logging.debug("Point cloud import completed.")
        return{'FINISHED'}
    