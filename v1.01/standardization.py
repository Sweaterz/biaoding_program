import math

# 标定数据

# 以下内容是标定工作
# scanning_direction_is_UP = True   #激光扫描方向是否向上 默认从下向上扫
# iHorizontalAngle = 0.0            #标定角度 单位度
# iHorizontalHeight = 0.0           #标定高度 单位mm
# min_l = 0.0                       #标定路面最近处 单位mm
# max_l = 5000.0                    #标定路面最远处 单位mm
# min_h = 0.0                       #扫描范围最低处 单位mm   理想状态下为0
# max_h = 4000                      #扫描范围最高处 单位mm   默认最大高度为4m

#输入一帧数据以及雷达扫描步距角
#输出角度、高度、最小l值、最大l值
def standardization_dg(use_data, lidarAngleStep):
    iHorizontalAngle = get_iHorizontalAngle_dg(use_data, lidarAngleStep)
    iHorizontalHeight = get_iHorizontalHeight_dg(use_data, lidarAngleStep, iHorizontalAngle)
    min_l = get_min_l_dg(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight)
    max_l = get_max_l_dg(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l)
    return iHorizontalAngle, iHorizontalHeight, min_l, max_l

def get_iHorizontalAngle_dg(data, lidarAngleStep):
    size = len(data)
    my_data = []
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 100:
            continue
        angle0 = i * lidarAngleStep
        h = int(math.sin(math.radians(angle0)) * distance)
        l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)
        if l > 5000:
            break
        my_data.append([l, h])
        if i == int(size / 2) - 100:
            break
    # 测量水平地面的角度
    my_tans = []
    for i, coordinate in enumerate(my_data):
        l = coordinate[0]
        h = coordinate[1]
        if i > 25:
            l1 = my_data[i - 25][0]
            h1 = my_data[i - 25][1]
            l2 = l
            h2 = h
            if l1 != l2:
                tan = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
                my_tans.append(tan)
    my_tans = [my_tan for my_tan in my_tans if math.fabs(my_tans[25] - my_tan) <= 10]
    if my_tans != []:
        average_tan = sum(my_tans) / len(my_tans)
        print("Final tan is %.2f" % average_tan)
        return average_tan

def get_iHorizontalHeight_dg(data, lidarAngleStep, iHorizontalAngle):
    size = len(data)
    my_data = []
    for i in range(int(size / 2)):
        angle0 = i * lidarAngleStep
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 100:
            continue
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = - int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = + int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = 0
            l = distance
        if l < 2000:
            my_data.append(h)
        else:
            continue
    min_h = min(my_data)
    min_h = -min_h
    print("Final height is", min_h - 38)
    return min_h - 38

def get_min_l_dg(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight):
    size = len(data)
    my_data = []
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 100:
            continue
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = iHorizontalHeight
            l = distance
        if h < 0 and 500 < l < 2000:
            break
    print("Final minl is", l)
    return l

def get_max_l_dg(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l):
    size = len(data)
    my_data = []
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 100:
            continue
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = iHorizontalHeight
            l = distance
        if l > min_l and h > 100:
            break
    print("Final maxl is", l)
    return l - 20

def standardization_as(use_data, lidarAngleStep):
    iHorizontalAngle = get_iHorizontalAngle_as(use_data, lidarAngleStep)
    iHorizontalHeight = get_iHorizontalHeight_as(use_data, lidarAngleStep, iHorizontalAngle)
    min_l = get_min_l_as(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight)
    max_l = get_max_l_as(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l)
    return iHorizontalAngle, iHorizontalHeight, min_l, max_l

def get_iHorizontalAngle_as(data, lidarAngleStep):
    size = len(data)
    my_data = []
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
        angle0 = i * lidarAngleStep
        h = int(math.sin(math.radians(angle0)) * distance)
        l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)
        if 2500 > distance > 1800:
            my_data.append([l, h])
    # 测量水平地面的角度
    my_tans = []
    for i, coordinate in enumerate(my_data):
        l = coordinate[0]
        h = coordinate[1]
        if i > 25:
            l1 = my_data[i - 25][0]
            h1 = my_data[i - 25][1]
            l2 = l
            h2 = h
            if l1 != l2 and l < 5000:
                tan = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
                my_tans.append(tan)
    if my_data[0][0] > my_data[-1][0]:
        my_tans = [my_tan for my_tan in my_tans if math.fabs(my_tans[-25] - my_tan) <= 10]
    else:
        my_tans = [my_tan for my_tan in my_tans if math.fabs(my_tans[25] - my_tan) <= 10]
    if my_tans != []:
        average_tan = sum(my_tans) / len(my_tans)
        print("Final tan is %.2f" % average_tan)
        return average_tan

def get_iHorizontalHeight_as(data, lidarAngleStep, iHorizontalAngle):
    size = len(data)
    my_data = []
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
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = + int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = - int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = 0
            l = distance
        if 0 < l < 2000:
            my_data.append(h)
        else:
            continue
    if my_data == []:
        print("Height is error, please replace the data file to retry.")
        return 0
    min_h = -min(my_data)
    print("Final height is", min_h - 30)
    return min_h - 30

def get_min_l_as(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight):
    size = len(data)
    my_data = []
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
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = iHorizontalHeight
            l = distance
        if 500 < l < 1500:
            my_data.append([l, h])
    min_l = 0
    if my_data == []:
        print("please choose other data file.")
        return
    if my_data[0][0] > my_data[-1][0]:
        for l, h in my_data:
            if h > 0:
                min_l = l + 100
                break
    else:
        for l, h in my_data:
            if h < 0:
                min_l = l + 100
                break
    print("Final minl is", min_l)
    return min_l

def get_max_l_as(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l):
    size = len(data)
    my_data = []
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
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = iHorizontalHeight
            l = distance
        if 2000 < l < 5000:
            my_data.append([l, h])
    if my_data == []:
        print("Maxl error, please replace other file", min_l)
        return min_l
    max_l = min_l
    if my_data[0][0] > my_data[-1][0]:
        for l, h in my_data:
            if h < 50:
                max_l = l - 10
                break
    else:
        for l, h in my_data:
            if h > 50:
                max_l = l - 10
                break
    print("Final maxl is", max_l)
    return max_l