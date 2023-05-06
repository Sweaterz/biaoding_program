import math
import os

import numpy as np

from mayavi import mlab

from standardization import standardization_dg, standardization_as
from show_only_for_biaoding import read_bin, read_pcd, read_txt


class Biaoding():
    def __init__(self, filePath, savePath, brand="as"):
        self.filePath = filePath
        self.savePath = savePath
        self.iHorizontalAngle = 0  # 84.53
        if brand == "dg":
            self.lidarAngleStep = 0.125
        elif brand == "as":
            self.lidarAngleStep = 0.25
        self.iHorizontalHeight = 0  # 1275
        self.start_idx = 0
        self.end_idx = 0
        self.min_l = 0
        self.max_l = 5000
        self.min_h = 0
        self.max_h = 4000
        self.brand = brand  # 品牌  "dg"  or   "as"
        self.all_data = []
        # self.readDatDG()
        # self.biaoding_show()

    def chooseDataDG(self):
        use_data = []
        with open(self.filePath, 'r') as fopen:
            lines = fopen.readlines()
            for idx, line in enumerate(lines):
                line_data = line.split(" ")
                if line_data[0] != 'FC':
                    continue
                if len(line_data) < 1813:
                    print('this scan data is not enough, discard it!')
                    continue
                num_points = int(line_data[19], 16) * 256 + int(line_data[18], 16)
                assert num_points * 2 + 49 - 1 == 1810
                use_data.append(line_data[49: 1810])
        return use_data

    # 用于读取广武杜格雷达点云数据，.dat格式, 仅根据是否有点判断是否为车辆,杜格从下开始扫描
    def readDatDG(self):
        use_data = self.chooseDataDG()
        if len(use_data) < 30:
            print("this data is not right! please check it! filePath is %s" % self.filePath)
            return self.all_data
        # 标定开始
        self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization_dg(use_data[0],
                                                                                                   self.lidarAngleStep)
        # 标定结束

        for idx, data in enumerate(use_data):
            size = len(data)
            for i in range(int(size / 2)):
                MSB = data[i * 2 + 1]
                LSB = data[i * 2]
                distance = int(MSB, 16) * 256 + int(LSB, 16)
                if distance < 100:
                    continue
                angle0 = i * self.lidarAngleStep
                # h = int(math.sin(math.radians(angle0)) * distance) + iHorizontalHeight
                # l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)
                if angle0 < self.iHorizontalAngle:
                    angle = self.iHorizontalAngle - angle0
                    h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > self.iHorizontalAngle:
                    angle = angle0 - self.iHorizontalAngle
                    h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = self.iHorizontalHeight
                    l = distance
                if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    if self.start_idx == 0:
                        self.start_idx = idx
                    self.end_idx = idx
                # if idx > 150:
                #     all_data.append([idx, l / 20.0, h / 20.0, 150])  # all_data.append([idx, h, l, 150, i])
                # if self.min_l < l < self.max_l:
                #     self.all_data.append([idx, l / 20.0, h / 20.0, 150])
                if l < 6000:
                    self.all_data.append([idx, l / 20.0, h / 20.0, 150])

        print("read format: the file:%s, start_idx:%d, end_idx:%d" % (self.filePath, self.start_idx, self.end_idx))
        if self.savePath is not "":
            savedir = "/".join(self.savePath.split('/')[:-1])
            if not os.path.exists(savedir):  # 如果路径不存在
                os.makedirs(savedir)
            binpc = np.array(self.all_data)
            binpc = binpc.reshape(-1, 4).astype(np.float32)
            binpc.tofile(self.savePath)
        return self.all_data

    def readDatDG2(self):
        use_data = self.chooseDataDG()
        if len(use_data) < 30:
            print("this data is not right! please check it! filePath is %s" % self.filePath)
            return self.all_data
        # 手动标定不需要这一步
        # self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization(use_data[0],                                                                                self.lidarAngleStep)
        # 标定结束

        for idx, data in enumerate(use_data):
            size = len(data)
            for i in range(int(size / 2)):
                MSB = data[i * 2 + 1]
                LSB = data[i * 2]
                distance = int(MSB, 16) * 256 + int(LSB, 16)
                if distance < 100:
                    continue

                angle0 = i * self.lidarAngleStep
                # h = int(math.sin(math.radians(angle0)) * distance) + iHorizontalHeight
                # l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)

                if angle0 < self.iHorizontalAngle:
                    angle = self.iHorizontalAngle - angle0
                    h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > self.iHorizontalAngle:
                    angle = angle0 - self.iHorizontalAngle
                    h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = self.iHorizontalHeight
                    l = distance
                if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    if self.start_idx == 0:
                        self.start_idx = idx
                    self.end_idx = idx
                # if idx > 150:
                #     all_data.append([idx, l / 20.0, h / 20.0, 150])  # all_data.append([idx, h, l, 150, i])
                if l < 6000:
                    self.all_data.append([idx, l / 20.0, h / 20.0, 150])
        print("read format: the file:%s, start_idx:%d, end_idx:%d" % (self.filePath, self.start_idx, self.end_idx))
        if self.savePath is not "":
            savedir = "/".join(self.savePath.split('/')[:-1])
            if not os.path.exists(savedir):  # 如果路径不存在
                os.makedirs(savedir)
            binpc = np.array(self.all_data)
            binpc = binpc.reshape(-1, 4).astype(np.float32)
            binpc.tofile(self.savePath)
        return self.all_data

    def final_show(self, format="bin"):
        final_data = []
        if self.brand == "dg":
            use_data = self.chooseDataDG()
            if len(use_data) < 30:
                print("this data is not right! please check it! filePath is %s" % self.filePath)
                return self.all_data
            # 手动标定不需要这一步
            # self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization(use_data[0],                                                                                self.lidarAngleStep)
            # 标定结束
            for idx, data in enumerate(use_data):
                size = len(data)
                for i in range(int(size / 2)):
                    MSB = data[i * 2 + 1]
                    LSB = data[i * 2]
                    distance = int(MSB, 16) * 256 + int(LSB, 16)
                    if distance < 100:
                        continue

                    angle0 = i * self.lidarAngleStep
                    # h = int(math.sin(math.radians(angle0)) * distance) + iHorizontalHeight
                    # l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)

                    if angle0 < self.iHorizontalAngle:
                        angle = self.iHorizontalAngle - angle0
                        h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    elif angle0 > self.iHorizontalAngle:
                        angle = angle0 - self.iHorizontalAngle
                        h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    else:
                        h = self.iHorizontalHeight
                        l = distance
                    if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                        if self.start_idx == 0:
                            self.start_idx = idx
                        self.end_idx = idx
                    # if idx > 150:
                    #     all_data.append([idx, l / 20.0, h / 20.0, 150])  # all_data.append([idx, h, l, 150, i])
                    if self.min_l < l < self.max_l and self.min_h < h < self.max_h:
                        final_data.append([idx, l / 20, h / 20, 150])
                    else:
                        continue
            if self.savePath is not "":
                binpc = np.array(final_data)
                binpc = binpc.reshape(-1, 4).astype(np.float32)
                binpc.tofile(self.savePath)
        elif self.brand == "as":
            use_data = self.chooseDataAS()
            # 手动标定不需要下面的代码
            # iHorizontalAngle, iHorizontalHeight, min_l, max_l = standardization_as(use_data[0], lidarAngleStep)
            for idx, data in enumerate(use_data):
                scan_data = []
                size = len(data)
                assert size % 6 == 0, 'the data is not a multiple of 6, please check it, size:%d!' % size
                for i in range(int(size / 6)):
                    D1 = data[i * 6]
                    D2 = data[i * 6 + 1]
                    D3 = data[i * 6 + 2]
                    D4 = data[i * 6 + 3]
                    i1 = data[i * 6 + 4]
                    i2 = data[i * 6 + 5]
                    distance = int(D1, 16) * 256 * 256 * 256 + int(D2, 16) * 256 * 256 + int(D3, 16) * 256 + int(D4, 16)
                    distance = int(distance / 10.0)
                    if distance < 100:
                        continue
                    angle0 = i * self.lidarAngleStep
                    # h = int(math.sin(math.radians(angle0)) * distance) + iHorizontalHeight
                    # l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)
                    if angle0 < self.iHorizontalAngle:
                        angle = self.iHorizontalAngle - angle0
                        h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    elif angle0 > self.iHorizontalAngle:
                        angle = angle0 - self.iHorizontalAngle
                        h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    else:
                        h = self.iHorizontalHeight
                        l = distance
                    if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                        if self.start_idx == 0:
                            self.start_idx = idx
                        self.end_idx = idx
                    if self.min_l < l < self.max_l and self.min_h < h < self.max_h:
                        final_data.append([idx, l / 10, h / 10, 150])
                    else:
                        continue
            if self.savePath is not "":
                binpc = np.array(final_data)
                binpc = binpc.reshape(-1, 4).astype(np.float32)
                binpc.tofile(self.savePath)
        self.biaoding_show()
        return final_data
    def biaoding_show(self, format="bin"):
        x = None
        y = None
        z = None
        col = None
        if format == "pcd":
            x, y, z, col = read_pcd(self.savePath)
        elif format == "bin":
            x, y, z, col = read_bin(self.savePath)
        elif format == "txt":
            x, y, z, col = read_txt(self.savePath)
        else:
            print("the format setting doesn't right!")
            exit(0)

        fig = mlab.figure(bgcolor=(0.136, 0.329, 0.222),
                          size=(640, 500))  # fig = mlab.figure(bgcolor=(0.136, 0.329, 0.222), size=(640, 500))
        l = mlab.points3d(x, y, z,
                          col,  # Values used for Color
                          mode="point",
                          # 灰度图的伪彩映射
                          colormap='spectral',  # 'bone', 'copper', 'gnuplot'
                          # color=(0, 1, 0),   # Used a fixed (r,g,b) instead
                          # figure=fig,
                          )
        # 绘制原点
        mlab.points3d(0, 0, 0, color=(1, 1, 1), mode="sphere", scale_factor=0.2)
        # 绘制坐标
        axes = np.array(
            [[1000.0, 0.0, 0.0, 0.0], [0.0, 500, 0.0, 0.0], [0.0, 0.0, 300, 0.0]],
            dtype=np.float64,
        )
        self.plot_biaoding_area()

        if self.brand == "dg":
            div_num = 20
        elif self.brand == "as":
            div_num = 10
        else:
            div_num = 1
        # x轴
        mlab.plot3d(
            [0, axes[0, 0]],
            [0, axes[0, 1]],
            [0, axes[0, 2]],
            color=(1, 0, 0),
            tube_radius=None,
            figure=fig,
        )

        # y轴
        mlab.plot3d(
            [0, axes[1, 0]],
            [0, self.min_l / div_num],
            [0, axes[1, 2]],
            color=(0, 1, 0),
            tube_radius=None,
            figure=fig,
        )
        mlab.plot3d(
            [0, axes[1, 0]],
            [self.max_l / div_num, axes[1, 1]],
            [0, axes[1, 2]],
            color=(0, 1, 0),
            tube_radius=None,
            figure=fig,
        )

        # z轴
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

    def plot_biaoding_area(self):
        # max_l轴
        if self.brand == "dg":
            div_num = 20
        elif self.brand == "as":
            div_num = 10
        else:
            div_num = 1

        mlab.plot3d(
            [self.start_idx, self.start_idx],
            [self.min_l / div_num, self.max_l / div_num],
            [self.min_h / div_num, self.min_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,

        )
        # min_l轴
        mlab.plot3d(
            [self.end_idx, self.end_idx],
            [self.min_l / div_num, self.max_l / div_num],
            [self.min_h / div_num, self.min_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        # max_h轴
        mlab.plot3d(
            [self.start_idx, self.start_idx],
            [self.min_l / div_num, self.min_l / div_num],
            [self.min_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.start_idx, self.start_idx],
            [self.max_l / div_num, self.max_l / div_num],
            [self.min_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.end_idx, self.end_idx],
            [self.min_l / div_num, self.min_l / div_num],
            [self.min_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.end_idx, self.end_idx],
            [self.max_l / div_num, self.max_l / div_num],
            [self.min_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.end_idx, self.end_idx],
            [self.min_l / div_num, self.max_l / div_num],
            [self.max_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.start_idx, self.start_idx],
            [self.min_l / div_num, self.max_l / div_num],
            [self.max_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.start_idx, self.end_idx],
            [self.min_l / div_num, self.min_l / div_num],
            [self.max_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.start_idx, self.end_idx],
            [self.max_l / div_num, self.max_l / div_num],
            [self.max_h / div_num, self.max_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.start_idx, self.end_idx],
            [self.max_l / div_num, self.max_l / div_num],
            [self.min_h / div_num, self.min_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )
        mlab.plot3d(
            [self.start_idx, self.end_idx],
            [self.min_l / div_num, self.min_l / div_num],
            [self.min_h / div_num, self.min_h / div_num],
            color=(1, 1, 0),
            tube_radius=None,
        )

    def chooseDataAS(self):
        use_data = []
        with open(self.filePath, 'r') as fopen:
            lines = fopen.readlines()
            oldpackagIdx = 0
            lineData = []
            lineData_ = []
            for idx, line in enumerate(lines):
                line_data = line.split(" ")
                if line_data[0] != '02' or line_data[1] != '00' or line_data[2] != '04' or line_data[3] != '02':
                    continue
                packagNums = int(line_data[84], 16)
                assert packagNums == 2
                packagIdx = int(line_data[87], 16)
                pointsNum = int(line_data[88], 16) * 256 + int(line_data[89], 16)
                if packagIdx != 0:
                    if packagIdx - oldpackagIdx != 1:
                        continue
                    lineData.append(line_data[90: 90 + pointsNum * 6])
                    if packagIdx == packagNums - 1:
                        oldpackagIdx = 0
                        if len(lineData) != packagNums:
                            lineData = []
                            continue
                        for i in range(packagNums):
                            lineData_ = lineData_ + lineData[i]
                        use_data.append(lineData_)
                        lineData = []
                        lineData_ = []
                    else:
                        oldpackagIdx = packagIdx
                else:
                    lineData.append(line_data[90: 90 + pointsNum * 6])

        return use_data

    # 用于读取广武傲视雷达点云数据，.dat格式, 仅根据是否有点判a断是否为车辆,傲视从上开始扫描
    def justreadDatAS(self):
        use_data = self.chooseDataAS()
        # 标定开始
        self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization_as(use_data[0], self.lidarAngleStep)
        # 标定结束
        for idx, data in enumerate(use_data):
            scan_data = []
            size = len(data)
            assert size % 6 == 0, 'the data is not a multiple of 6, please check it, size:%d!' % size
            for i in range(int(size / 6)):
                D1 = data[i * 6]
                D2 = data[i * 6 + 1]
                D3 = data[i * 6 + 2]
                D4 = data[i * 6 + 3]
                i1 = data[i * 6 + 4]
                i2 = data[i * 6 + 5]
                distance = int(D1, 16) * 256 * 256 * 256 + int(D2, 16) * 256 * 256 + int(D3, 16) * 256 + int(D4, 16)
                distance = int(distance / 10.0)
                itensity = int(i1, 16) * 256 + int(i2, 16)
                if distance < 100:
                    continue
                angle0 = i * self.lidarAngleStep
                # h = int(math.sin(math.radians(angle0)) * distance) + iHorizontalHeight
                # l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)

                if angle0 < self.iHorizontalAngle:
                    angle = self.iHorizontalAngle - angle0
                    h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > self.iHorizontalAngle:
                    angle = angle0 - self.iHorizontalAngle
                    h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = self.iHorizontalHeight
                    l = distance
                if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    if self.start_idx == 0:
                        self.start_idx = idx
                    self.end_idx = idx
                if l < 6000:
                    self.all_data.append(
                        [idx, l / 10.0, h / 10.0, 150])  # all_data.append([idx, h, l, 150, i, distance])

        print("read format: the file:%s, start_idx:%d, end_idx:%d" % (self.filePath, self.start_idx, self.end_idx))

        if self.savePath is not "":
            savedir = "/".join(self.savePath.split('/')[:-1])
            if not os.path.exists(savedir):  # 如果路径不存在
                os.makedirs(savedir)
            binpc = np.array(self.all_data)
            binpc = binpc.reshape(-1, 4).astype(np.float32)
            binpc.tofile(self.savePath)
        return self.all_data



    def justreadDatAS2(self):
        use_data = self.chooseDataAS()
        # 手动标定不需要下面的代码
        # iHorizontalAngle, iHorizontalHeight, min_l, max_l = standardization_as(use_data[0], lidarAngleStep)
        for idx, data in enumerate(use_data):
            scan_data = []
            size = len(data)
            assert size % 6 == 0, 'the data is not a multiple of 6, please check it, size:%d!' % size
            for i in range(int(size / 6)):
                D1 = data[i * 6]
                D2 = data[i * 6 + 1]
                D3 = data[i * 6 + 2]
                D4 = data[i * 6 + 3]
                i1 = data[i * 6 + 4]
                i2 = data[i * 6 + 5]
                distance = int(D1, 16) * 256 * 256 * 256 + int(D2, 16) * 256 * 256 + int(D3, 16) * 256 + int(D4, 16)
                distance = int(distance / 10.0)
                itensity = int(i1, 16) * 256 + int(i2, 16)
                if distance < 100:
                    continue
                angle0 = i * self.lidarAngleStep
                # h = int(math.sin(math.radians(angle0)) * distance) + iHorizontalHeight
                # l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)
                if angle0 < self.iHorizontalAngle:
                    angle = self.iHorizontalAngle - angle0
                    h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > self.iHorizontalAngle:
                    angle = angle0 - self.iHorizontalAngle
                    h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = self.iHorizontalHeight
                    l = distance
                if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    if self.start_idx == 0:
                        self.start_idx = idx
                    self.end_idx = idx
                if l < 6000:
                    self.all_data.append(
                        [idx, l / 10.0, h / 10.0, 150])  # all_data.append([idx, h, l, 150, i, distance])

        print("read format: the file:%s, start_idx:%d, end_idx:%d" % (self.filePath, self.start_idx, self.end_idx))
        if self.savePath is not "":
            savedir = "/".join(self.savePath.split('/')[:-1])
            if not os.path.exists(savedir):  # 如果路径不存在
                os.makedirs(savedir)
            binpc = np.array(self.all_data)
            binpc = binpc.reshape(-1, 4).astype(np.float32)
            binpc.tofile(self.savePath)
        return self.all_data


if __name__ == '__main__':
    a = Biaoding("/home/zhy/下载/code/zhy/data/my_data/dg1/20230414/20230414015053.dat",
                 "/home/zhy/下载/code/zhy/data/my_bin/dg1/20230414/20230414015053.bin")
