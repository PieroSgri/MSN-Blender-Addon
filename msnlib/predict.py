import sys
import open3d as o3d
from model import *
from utils import *
import argparse
import random
import numpy as np
import torch
import os
import visdom
sys.path.append("./emd/")
import emd_module as emd

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default = './trained_model/network.pth',  help='optional reload model path')
parser.add_argument('--num_points', type=int, default = 8192,  help='number of points')
parser.add_argument('--n_primitives', type=int, default = 16,  help='number of primitives in the atlas')
parser.add_argument('--env', type=str, default ="MSN_VAL"   ,  help='visdom environment')

opt = parser.parse_args()
print(opt)

network = MSN(num_points = opt.num_points, n_primitives = opt.n_primitives)
network.cuda()
network.apply(weights_init)

if opt.model != '':
    network.load_state_dict(torch.load(opt.model))
    print("Previous weight loaded ")

network.eval()

model_list = ['04530566_fc71778c7daf92e49786591d9b03a096']

partial_dir = "./data/val/"

def resample_pcd(pcd, n):
    """Drop or duplicate points so that pcd has exactly n points"""
    idx = np.random.permutation(pcd.shape[0])
    if idx.shape[0] < n:
        idx = np.concatenate([idx, np.random.randint(pcd.shape[0], size = n - pcd.shape[0])])
    return pcd[idx[:n]]

EMD = emd.emdModule()

labels_generated_points = torch.Tensor(range(1, (opt.n_primitives+1)*(opt.num_points//opt.n_primitives)+1)).view(opt.num_points//opt.n_primitives,(opt.n_primitives+1)).transpose(0,1)
labels_generated_points = (labels_generated_points)%(opt.n_primitives+1)
labels_generated_points = labels_generated_points.contiguous().view(-1)

with torch.no_grad():
    for i, model in enumerate(model_list):
        print(model)
        partial = torch.zeros((50, 5000, 3), device='cuda')
        gt = torch.zeros((50, opt.num_points, 3), device='cuda')
        for j in range(50):
            pcd = o3d.io.read_point_cloud(os.path.join(partial_dir, model + '_' + str(j) + '_denoised.pcd'))
            partial[j, :, :] = torch.from_numpy(resample_pcd(np.array(pcd.points), 5000))

        output1, output2, expansion_penalty = network(partial.transpose(2,1).contiguous())

        idx = random.randint(0, 49)
        
        original = partial[idx].data.cpu()
        prediction = output2[idx].data.cpu()
        np.savetxt('partial_pc.txt', original.numpy(), fmt="%1.20s")
        np.savetxt('filled_pc.txt', prediction.numpy(), fmt="%1.20s")

        print("Filled and original point cloud saved to file")
