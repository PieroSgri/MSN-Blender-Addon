import open3d as o3d
import numpy as np
import torch
import random
import os


def resample_pcd(pcd, n):
    """Drop or duplicate points so that pcd has exactly n points"""
    idx = np.random.permutation(pcd.shape[0])
    if idx.shape[0] < n:
        idx = np.concatenate([idx, np.random.randint(pcd.shape[0], size = n - pcd.shape[0])])
    return pcd[idx[:n]]


partial_dir = "./data/val/"
pcd_file = "02691156_e138a98d82f3aa692142bc26f72ae44c"
print(pcd_file)
partial = torch.zeros((50, 5000, 3), device='cuda')
for j in range(50):
    pcd = o3d.io.read_point_cloud(os.path.join(partial_dir, pcd_file + '_' + str(j) + '_denoised.pcd'))
    partial[j, :, :] = torch.from_numpy(resample_pcd(np.array(pcd.points), 5000))

idx = random.randint(0, 49)
print(partial[idx].data.cpu().numpy())

np.savetxt('nuova_prova.txt', partial[idx].data.cpu().numpy(), fmt="%1.20s")
