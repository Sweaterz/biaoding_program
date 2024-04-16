from mayavi import mlab
# import open3d as o3d
import numpy as np
import os
import argparse
allFiles = []


def read_pcd(fullname):
    lidar = []
    with open(fullname,'r') as f:
        line = f.readline().strip()
        while line:
            linestr = line.split(" ")
            if len(linestr) == 4:
                linestr_convert = list(map(float, linestr))
                lidar.append([linestr_convert[0], linestr_convert[1], linestr_convert[2], linestr_convert[3]])
            line = f.readline().strip()
    pointcloud =np.array(lidar).reshape(-1, 4)
    x = pointcloud[:, 0]
    y = pointcloud[:, 1]
    z = pointcloud[:, 2]
    i = pointcloud[:, 3]
    vals = 'height'
    if vals == "height":
        col = z
    else:
        col = i
    return x, y, z, col


def read_bin(path):
    pointcloud = np.fromfile(path, dtype=np.float32).reshape(-1, 4)
    if pointcloud.size == 0:
        return [], [], [], []
    x = pointcloud[:, 0]
    y = pointcloud[:, 1]
    z = pointcloud[:, 2]
    i = pointcloud[:, 3]
    vals = 'height'
    if vals == "height":
        col = z
    else:
        col = i
    return x, y, z, col


def read_txt(fullname):
    lidar = []
    with open(fullname, 'r') as f:
        line = f.readline().strip()#去除空格
        while line:
            linestr = line.split(" ")
            if len(linestr) == 3:
                linestr_convert = list(map(float, linestr))
                lidar.append([linestr_convert[0], linestr_convert[1], linestr_convert[2], 200])
            line = f.readline().strip()
    pointcloud = np.array(lidar).reshape(-1, 4)
    x = pointcloud[:, 0] / 100
    y = pointcloud[:, 1] / 100
    z = pointcloud[:, 2] / 100
    i = pointcloud[:, 3]
    vals = 'height'
    if vals == "height":
        col = z
    else:
        col = i
    return x, y, z, col


def getAll(file_path):
    for filename in os.listdir(file_path):
        allFiles.append(os.path.join(file_path, filename))
    # return allFiles


@mlab.animate(delay=100)
def anim(l):
    for file in allFiles:
        x, y, z, col = read_pcd(file)
        l.mlab_source.reset(x=x, y=y, z=z, col=col)
        mlab.show(func=None, stop=False)
        yield



def biaoding_show(file_path, format):
    x = None
    y = None
    z = None
    col = None
    if format == "pcd":
        x, y, z, col = read_pcd(file_path)
    elif format == "bin":
        x, y, z, col = read_bin(file_path)
    elif format == "txt":
        x, y, z, col = read_txt(file_path)
    else:
        print("the format setting doesn't right!")
        exit(0)

    fig = mlab.figure(bgcolor=(0.136, 0.329, 0.222), size=(640, 500)) # fig = mlab.figure(bgcolor=(0.136, 0.329, 0.222), size=(640, 500))
    l = mlab.points3d(x, y, z,
                         col,  # Values used for Color
                         mode="point",
                         # 灰度图的伪彩映射
                         colormap='spectral',  # 'bone', 'copper', 'gnuplot'
                         # color=(0, 1, 0),   # Used a fixed (r,g,b) instead
                         figure=fig,
                         )
    # 绘制原点
    mlab.points3d(0, 0, 0, color=(1, 1, 1), mode="sphere", scale_factor=0.2)
    # 绘制坐标
    axes = np.array(
        [[2000.0, 0.0, 0.0, 0.0], [0.0, 75.4, 0.0, 0.0], [0.0, 0.0, 250, 0.0]],
        dtype=np.float64,
    )
    #x轴
    mlab.plot3d(
        [0, axes[0, 0]],
        [0, axes[0, 1]],
        [0, axes[0, 2]],
        color=(1, 0, 0),
        tube_radius=None,
        figure=fig,
    )

    #y轴
    mlab.plot3d(
        [0, axes[1, 0]],
        [0, axes[1, 1]],
        [0, axes[1, 2]],
        color=(0, 1, 0),
        tube_radius=None,
        figure=fig,
    )
    # max_l轴
    # mlab.plot3d(
    #     [0, axes[1, 0]],
    #     [0, 500],
    #     [0, axes[1, 2]],
    #     color=(1, 1, 0),
    #     tube_radius=None,
    #     figure=fig,
    # )
    #  min_l轴
    # mlab.plot3d(
    #     [50, 50],
    #     [0, 100],
    #     [0, axes[1, 2]],
    #     color=(0, 1, 0),
    #     tube_radius=None,
    #     figure=fig,
    # )
    #z轴
    mlab.plot3d(
        [0, axes[2, 0]],
        [0, axes[2, 1]],
        [0, axes[2, 2]],
        color=(0, 0, 1),
        tube_radius=None,
        figure=fig,
    )
    # l.mlab_source.reset(x=x, y=y, z=z, col=col)
    mlab.show(func=None, stop=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('main.py')
    parser.add_argument('--path', type=str, default='./data/my_bin/as2/20230412/20230412230422.bin', help='the dir of you need to check')
    parser.add_argument('--format', type=str, default='bin', help="the format of lidar you need to show")
    args = parser.parse_args()
    biaoding_show(args.path, args.format)



