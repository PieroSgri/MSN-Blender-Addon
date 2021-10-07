import bpy
import sys
import argparse
import random
import os
import argparse

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from pathlib import Path

import logging
logging.basicConfig(level=logging.DEBUG)

current_path = Path(__file__).parent.resolve()

emd_path = Path(os.path.join(current_path, "emd/"))
expansion_penalty_path = Path(os.path.join(current_path, "expansion_penalty/"))
MDS_path = Path(os.path.join(current_path, "MDS/"))

sys.path.append(emd_path)
sys.path.append(expansion_penalty_path)
sys.path.append(MDS_path)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from .msnlib.model import MSN
    from .msnlib.utils import weights_init
    import open3d as o3d
    import msnlib.emd.emd_module as emd
    import msnlib.expansion_penalty.expansion_penalty_module as expansion
    import msnlib.MDS.MDS_module
    import numpy as np
    import torch
except ModuleNotFoundError as err:
    logging.debug(f"Errore import moduli in MSNImportPointCloud: {err}")
    

def resample_pcd(pcd, n):
    """Drop or duplicate points so that pcd has exactly n points"""

    idx = np.random.permutation(pcd.shape[0])
    if idx.shape[0] < n:
        idx = np.concatenate([idx, np.random.randint(pcd.shape[0], size=n - pcd.shape[0])])
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
    return partial


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


class MSNImportPredict(Operator, ImportHelper):
    bl_idname = "msn.import_predict"
    bl_label = "Import and fill PCD file"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(
        default='*.txt;*.pcd;*',
        options={'HIDDEN'})

    def execute(self, context):
        
        current_path = Path(__file__).parent.resolve()
        logging.debug(f"current_path: {current_path}")
        directory = Path(self.filepath).parent
        print('Selected directory:', directory)
        file_list = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        file_list.sort()
        for i in file_list:
            print(i)
                
        trained_model_path = Path(os.path.join(current_path, "msnlib/trained_model/network.pth"))
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--model', type=str, default=trained_model_path, help='optional reload model path')
        parser.add_argument('--num_points', type=int, default=8192, help='number of points')
        parser.add_argument('--n_primitives', type=int, default=16, help='number of primitives in the atlas')
        parser.add_argument('--env', type=str, default="MSN_VAL", help='visdom environment')
    
        opt = parser.parse_args()
        print(opt)
    
        network = MSN(num_points=opt.num_points, n_primitives=opt.n_primitives)
        network.cuda()
        network.apply(weights_init)
    
        if opt.model != '':
            network.load_state_dict(torch.load(trained_model_path))
            print("Previous weight loaded ")
    
        network.eval()
    
        EMD = emd.emdModule()
    
        labels_generated_points = torch.Tensor(range(1, (opt.n_primitives + 1) * (opt.num_points // opt.n_primitives) + 1)).view(opt.num_points // opt.n_primitives, (opt.n_primitives + 1)).transpose(0, 1)
        labels_generated_points = (labels_generated_points) % (opt.n_primitives + 1)
        labels_generated_points = labels_generated_points.contiguous().view(-1)
    
        with torch.no_grad():
            partial = read_pcd(directory, file_list)
            output1, output2, expansion_penalty = network(partial.transpose(2, 1).contiguous())
    
            idx = random.randint(0, 49)
            original = partial[idx].data.cpu()
            prediction = output2[idx].data.cpu()
    
            original_path = "partial_pc.txt"
            filled_path = "filled_pc.txt"
    
            np.savetxt(original_path, original.numpy(), fmt="%1.20s")
            np.savetxt(filled_path, prediction.numpy(), fmt="%1.20s")
    
            print("Filled point cloud and original point cloud saved to file")
        
        # Create the object
        original_pc = import_pc(original_path)
        filled_pc = import_pc(filled_path)
        # Link object to the active collection
        bpy.context.collection.objects.link(original_pc)
        bpy.context.collection.objects.link(filled_pc)
        logging.debug("Completato")
        return {'FINISHED'}
