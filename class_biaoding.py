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
            self.lidarAngleStep = 0.25
        elif brand == "as":
            self.lidarAngleStep = 0.25
        self.iHorizontalHeight = 0  # 1275
        self.start_idx = 0
        self.end_idx = 0
        self.min_l = 0
        self.max_l = 5000
        self.min_h = 0
        self.max_h = 4000
        self.isle_l = 0
        self.isle_h = 0
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
                if line_data[4]=='9D' and line_data[5]=='03':
                    if len(line_data) < 925:
                        print('this scan data is not enough, discard it!')
                        continue
                elif line_data[4] == '0D' and line_data[5] == '07':
                    if len(line_data) < 1813:
                        print('this scan data is not enough, discard it!')
                        continue
                self.lidarAngleStep = (int(line_data[24], 16) + int(line_data[25], 16) * 256) / 10000
                num_points = int(line_data[19], 16) * 256 + int(line_data[18], 16)
                # assert num_points * 2 + 49 - 1 == 1810
                use_data.append(line_data[49: 2 * num_points + 49])
        return use_data

    # 用于读取广武杜格雷达点云数据，.dat格式, 仅根据是否有点判断是否为车辆,杜格从下开始扫描
    def readDatDG(self, up2down):
        use_data = self.chooseDataDG()

        if len(use_data) < 30:
            print("this data is not right! please check it! filePath is %s" % self.filePath)
            return self.all_data
        # 标定开始
        self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization_dg(use_data[50],
                                                                             self.lidarAngleStep, up2down)
        if up2down:
            coefficient = -1
        else:
            coefficient = 1
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
                    h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > self.iHorizontalAngle:
                    angle = angle0 - self.iHorizontalAngle
                    h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = self.iHorizontalHeight
                    l = distance
                # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                #     if self.start_idx == 0:
                #         self.start_idx = idx
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

    def readDatDG2(self, up2down = False):
        use_data = self.chooseDataDG()
        if len(use_data) < 30:
            print("this data is not right! please check it! filePath is %s" % self.filePath)
            return self.all_data
        if up2down:
            coefficient = -1
        else:
            coefficient = 1
        # 手动标定不需要这一步
        # self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization(use_data[0],
        # self.lidarAngleStep)

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
                    h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > self.iHorizontalAngle:
                    angle = angle0 - self.iHorizontalAngle
                    h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = self.iHorizontalHeight
                    l = distance
                # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                #     if self.start_idx == 0:
                #         self.start_idx = idx
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

    def final_show(self, format="bin", up2down = False):
        final_data = []
        if self.brand == "dg" or self.brand == "杜格":
            use_data = self.chooseDataDG()
            if len(use_data) < 30:
                print("this data is not right! please check it! filePath is %s" % self.filePath)
                return self.all_data
            # 手动标定不需要这一步
            # self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization(use_data[0],                                                                                self.lidarAngleStep)
            # 标定结束

            if up2down:
                coefficient = -1
            else:
                coefficient = 1
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
                        h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    elif angle0 > self.iHorizontalAngle:
                        angle = angle0 - self.iHorizontalAngle
                        h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    else:
                        h = self.iHorizontalHeight
                        l = distance
                    # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    #     if self.start_idx == 0:
                    #         self.start_idx = idx
                    self.end_idx = idx
                    # if idx > 150:
                    #     all_data.append([idx, l / 20.0, h / 20.0, 150])  # all_data.append([idx, h, l, 150, i])
                    if self.isle_l > l and self.isle_h > h:
                        continue
                    if self.min_l < l < self.max_l and self.min_h < h < self.max_h:
                        final_data.append([idx, l / 20, h / 20, 150])
                    else:
                        continue
            if self.savePath is not "":
                binpc = np.array(final_data)
                binpc = binpc.reshape(-1, 4).astype(np.float32)
                binpc.tofile(self.savePath)
        elif self.brand == "as" or self.brand == "傲视":
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
                    # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    #     if self.start_idx == 0:
                    #         self.start_idx = idx
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

    def plot_wheel_area(self):
        # max_l轴
        if self.brand == "dg":
            div_num = 20
        elif self.brand == "as":
            div_num = 10
        else:
            div_num = 1

        parameter = [[40, 82, 1300, 1050], [166, 210, 1300, 1050], [220, 262, 1300, 1050], [500, 544, 1200, 1050], [552, 590, 1190, 1050], [595, 635, 1190, 1050]]

        for i in range(6):
            mlab.plot3d(
                [parameter[i][0], parameter[i][1]],
                [parameter[i][2] / div_num, parameter[i][2] / div_num],
                [0 / div_num, 0 / div_num],
                color=(1, 1, 0),
                tube_radius=None,
            )

            mlab.plot3d(
                [parameter[i][0], parameter[i][1]],
                [parameter[i][2] / div_num, parameter[i][2] / div_num],
                [parameter[i][3] / div_num, parameter[i][3] / div_num],
                color=(1, 1, 0),
                tube_radius=None,
            )
            mlab.plot3d(
                [parameter[i][0], parameter[i][0]],
                [parameter[i][2] / div_num, parameter[i][2] / div_num],
                [0 / div_num, parameter[i][3] / div_num],
                color=(1, 1, 0),
                tube_radius=None,

            )
            mlab.plot3d(
                [parameter[i][1], parameter[i][1]],
                [parameter[i][2] / div_num, parameter[i][2] / div_num],
                [0 / div_num, parameter[i][3] / div_num],
                color=(1, 1, 0),
                tube_radius=None,

            )


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
                          colormap='spectral',  # 'bone', 'copper', 'gnuplot', 'spectral'
                          # color=(0, 1, 0),   # Used a fixed (r,g,b) instead
                          figure=fig,
                          )
        # 绘制原点
        mlab.points3d(0, 0, 0, color=(1, 1, 1), mode="sphere", scale_factor=0.2)
        # 绘制坐标
        axes = np.array(
            [[1000.0, 0.0, 0.0, 0.0], [0.0, 500, 0.0, 0.0], [0.0, 0.0, 300, 0.0]],
            dtype=np.float64,
        )
        self.plot_biaoding_area()
        # self.plot_wheel_area()
        if self.brand == "dg" or self.brand == "杜格":
            div_num = 20
        elif self.brand == "as" or self.brand == "傲视":
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
        l.mlab_source.reset(x=x, y=y, z=z, col=col)
        mlab.show(func=None, stop=False)

    def integrate_show(self, fig, format="bin"):
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
        if str(type(x)) != "<class 'list'>":
            ll = mlab.points3d(x, y, z,
                              col,  # Values used for Color
                              mode="point",
                              # 灰度图的伪彩映射
                              colormap='spectral',  # 'bone', 'copper', 'gnuplot', 'spectral'
                              # color=(0, 1, 0),   # Used a fixed (r,g,b) instead
                              figure=fig,
                              )
        else:
            ll = mlab.plot3d([5000], [5000], [5000])
        # 绘制原点
        mlab.points3d(0, 0, 0, color=(1, 1, 1), mode="sphere", scale_factor=0.2, figure=fig)
        # 绘制坐标
        axes = np.array(
            [[1000.0, 0.0, 0.0, 0.0], [0.0, 500, 0.0, 0.0], [0.0, 0.0, 300, 0.0]],
            dtype=np.float64,
        )
        # 绘制黄色辅助线
        self.plot_biaoding_area()
        # self.plot_wheel_area()
        if self.brand == "dg" or self.brand == "杜格":
            div_num = 20
        elif self.brand == "as" or self.brand == "傲视":
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
        ll.mlab_source.reset(x=x, y=y, z=z, col=col)
        # mlab.show(func=None, stop=False)

    def final_integrate_show(self, format="bin", up2down = False, fig = None):
        final_data = []
        if self.brand == "dg" or self.brand == "杜格":
            use_data = self.chooseDataDG()
            if len(use_data) < 30:
                print("this data is not right! please check it! filePath is %s" % self.filePath)
                return self.all_data
            # 手动标定不需要这一步
            # self.iHorizontalAngle, self.iHorizontalHeight, self.min_l, self.max_l = standardization(use_data[0],                                                                                self.lidarAngleStep)
            # 标定结束

            if up2down:
                coefficient = -1
            else:
                coefficient = 1
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
                        h = self.iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    elif angle0 > self.iHorizontalAngle:
                        angle = angle0 - self.iHorizontalAngle
                        h = self.iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
                        l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                    else:
                        h = self.iHorizontalHeight
                        l = distance
                    # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    #     if self.start_idx == 0:
                    #         self.start_idx = idx
                    self.end_idx = idx
                    # if idx > 150:
                    #     all_data.append([idx, l / 20.0, h / 20.0, 150])  # all_data.append([idx, h, l, 150, i])
                    if self.isle_l > l and self.isle_h > h:
                        continue
                    if self.min_l < l < self.max_l and self.min_h < h < self.max_h:
                        final_data.append([idx, l / 20, h / 20, 150])
                    else:
                        continue
            if self.savePath is not "":
                binpc = np.array(final_data)
                binpc = binpc.reshape(-1, 4).astype(np.float32)
                binpc.tofile(self.savePath)
        elif self.brand == "as" or self.brand == "傲视":
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
                    # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                    #     if self.start_idx == 0:
                    #         self.start_idx = idx
                    self.end_idx = idx
                    if self.min_l < l < self.max_l and self.min_h < h < self.max_h:
                        final_data.append([idx, l / 10, h / 10, 150])
                    else:
                        continue
            if self.savePath is not "":
                binpc = np.array(final_data)
                binpc = binpc.reshape(-1, 4).astype(np.float32)
                binpc.tofile(self.savePath)
        self.integrate_show(fig)
        return final_data

    def plot_biaoding_area(self):
        # max_l轴
        if self.brand == "dg" or self.brand == "杜格":
            div_num = 20
        elif self.brand == "as" or self.brand == "傲视":
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
        if use_data == []:
            print('data error')
            return
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
                # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                #     if self.start_idx == 0:
                #         self.start_idx = idx
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


    # 这个函数用来最终效果展示
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
                # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
                #     if self.start_idx == 0:
                #         self.start_idx = idx
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
    a = Biaoding("/home/zhy/biaoding_program/data/data_file/dg2/20230414/20230414055451.dat",
                 "/home/zhy/biaoding_program/data/bin_file/dg2/20230414/20230414055451.bin")
    a.iHorizontalAngle = 85.24
    a.iHorizontalHeight = 2057
    a.min_l = 1000
    a.max_l = 4240
    a.final_show()



