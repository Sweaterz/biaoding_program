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

# 输入一帧数据以及雷达扫描步距角
# 输出角度、高度、最小l值、最大l值
def standardization_dg(use_data, lidarAngleStep, up2down=False):
    iHorizontalAngle = get_iHorizontalAngle_test(use_data, lidarAngleStep, up2down)
    iHorizontalHeight = get_iHorizontalHeight_test(use_data, lidarAngleStep, iHorizontalAngle, up2down)
    min_l = get_min_l_test(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, up2down)
    max_l = get_max_l_test(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l, up2down)
    return iHorizontalAngle, iHorizontalHeight, min_l, max_l


def standardization_dg_270mini(use_data, lidarAngleStep, up2down=False, startAngleDiff=105):
    iHorizontalAngle = get_iHorizontalAngle_test_270mini(use_data, lidarAngleStep, up2down, startAngleDiff)
    iHorizontalHeight = get_iHorizontalHeight_test_270mini(use_data, lidarAngleStep, iHorizontalAngle, up2down)
    min_l = get_min_l_test_270mini(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, up2down)
    max_l = get_max_l_test_270mini(use_data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l, up2down)
    return iHorizontalAngle, iHorizontalHeight, min_l, max_l


def get_iHorizontalAngle_dg(data, lidarAngleStep, up2down):
    size = len(data)
    my_data = []
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 2060 or distance > 3640:
            continue
        angle0 = i * lidarAngleStep
        h = int(math.sin(math.radians(angle0)) * distance)
        l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)

        my_data.append([l, h])
        if i == int(size / 2) - 100:
            break
    if up2down:
        my_data.reverse()
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
    # my_tans_area = [[],[],[],[]]
    my_tans_area = [[], [], []]
    for tan in my_tans:
        if 30 < tan < 50:
            my_tans_area[0].append(tan)
        elif 50 < tan < 70:
            my_tans_area[1].append(tan)
        elif 70 < tan < 90:
            my_tans_area[2].append(tan)
        # else:
        # my_tans_area[3].append(tan)
    # max_area = max(len(my_tans_area[0]), len(my_tans_area[1]), len(my_tans_area[2]), len(my_tans_area[3]))
    max_area = max(len(my_tans_area[0]), len(my_tans_area[1]), len(my_tans_area[2]))
    for i in range(3):
        if len(my_tans_area[i]) == max_area:
            my_tans = my_tans_area[i]
    # my_tans = [my_tan for my_tan in my_tans if math.fabs(my_tans[25] - my_tan) <= 10]
    if my_tans != []:
        average_tan = sum(my_tans) / len(my_tans)
        print("Final tan is %.2f" % average_tan)
        return average_tan


# 新算法
def get_iHorizontalAngle_test(data, lidarAngleStep, up2down = False):
    size = len(data)
    my_data = []
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 2060 or distance > 3640:
            continue
        angle0 = i * lidarAngleStep
        h = int(math.sin(math.radians(angle0)) * distance)
        l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)

        my_data.append([l, h])

    # 测量水平地面的角度
    my_tans = []
    countNum = len(my_data) // 2
    for i in range(countNum):
        l1 = my_data[i][0]
        l2 = my_data[i + countNum][0]
        h1 = my_data[i][1]
        h2 = my_data[i + countNum][1]
        if l1 != l2:
            theta = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
            my_tans.append(theta)
    if len(my_tans) != 0:
        average = sum(my_tans) / len(my_tans)
    # 最大值和最小值之差应该满足小于0.5度
    while max(my_tans) - min(my_tans) > 0.5:
        diff = [math.fabs(tan - average) for tan in my_tans]
        m = max(diff)
        index = diff.index(m)
        value = my_tans[index]
        my_tans.remove(value)
        average = sum(my_tans) / len(my_tans)
    print(f"Final angle is {average:.2f}゜")

    return average


# 270mini
def get_iHorizontalAngle_test_270mini(data, lidarAngleStep, up2down = False, startAngleDiff = 105):
    my_data = []
    loops = data.split("\n")
    if loops[-1] == "":
        loops = loops[:-1]

    for loop in loops:
        hex_data = loop.split(" ")
        firstStartAngle = (int(hex_data[3], 16) * 256 + int(hex_data[2], 16)) / 100
        if len(hex_data) != 1206 or hex_data[0] != "FF" or hex_data[1] != "EE":
            return
        for i in range(12):
            startIdx = i * 100
            if hex_data[startIdx] != "FF" or hex_data[startIdx + 1] != "EE":
                continue
            startAngle = (int(hex_data[startIdx + 3], 16) * 256 + int(hex_data[startIdx+2], 16) ) / 100
            for j in range(startIdx+4, startIdx+100, 6):
                distance = int(hex_data[j + 1], 16) * 256 + int(hex_data[j], 16)
                # if distance < 2060 or distance > 3640:
                #     continue
                if distance < 1050 or distance > 2050:
                    continue
                idx = (j - startIdx - 4 + 6) / 6
                pointIdx = startIdx * 16 + idx
                angle = startAngle + lidarAngleStep * idx - startAngleDiff
                h = int(math.sin(math.radians(angle)) * distance)
                l = int(math.cos(angle * math.pi / 180) * distance)
                my_data.append([l, h])

    # 测量水平地面的角度
    my_tans = []
    countNum = len(my_data) // 2
    for i in range(countNum):
        l1 = my_data[i][0]
        l2 = my_data[i + countNum][0]
        h1 = my_data[i][1]
        h2 = my_data[i + countNum][1]
        if l1 != l2:
            theta = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
            my_tans.append(theta)
    if len(my_tans) != 0:
        average = sum(my_tans) / len(my_tans)
        # print(my_tans)
    # 最大值和最小值之差应该满足小于0.5度
    else:
        return
    while max(my_tans) - min(my_tans) > 0.5:
        diff = [math.fabs(tan - average) for tan in my_tans]
        m = max(diff)
        index = diff.index(m)
        value = my_tans[index]
        my_tans.remove(value)
        average = sum(my_tans) / len(my_tans)
    print(f"Final angle is {average:.2f}゜")
    return average


def get_iHorizontalHeight_dg(data, lidarAngleStep, iHorizontalAngle, up2down):
    size = len(data)
    my_data = []
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    for i in range(int(size / 2)):
        angle0 = i * lidarAngleStep
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 100 or distance > 5000:
            continue
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = - int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = + int(math.sin(math.radians(angle)) * distance) * coefficient
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


def get_iHorizontalHeight_test(data, lidarAngleStep, iHorizontalAngle, up2down):
    size = len(data)
    usedData = []
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    for i in range(int(size / 2)):
        angle0 = i * lidarAngleStep
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 2060 or distance > 3640:
            continue
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = - int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = + int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = 0
            l = distance
        usedData.append(h)

    average = sum(usedData) / len(usedData)
    while max(usedData) - min(usedData) > 0.5:
        diff = [math.fabs(data - average) for data in usedData]
        m = max(diff)
        index = diff.index(m)
        value = usedData[index]
        usedData.remove(value)
        average = sum(usedData) / len(usedData)

    print("Final height is", -max(usedData) - 50)
    return -max(usedData) - 50


def get_iHorizontalHeight_test_270mini(data, lidarAngleStep, iHorizontalAngle, up2down, startAngleDiff = 105):
    size = len(data)
    usedData = []
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    loops = data.split("\n")
    if loops[-1] == "":
        loops = loops[:-1]

    for loop in loops:
        hex_data = loop.split(" ")
        if len(hex_data) != 1206 or hex_data[0] != "FF" or hex_data[1] != "EE":
            return
        firstStartAngle = (int(hex_data[3], 16) * 256 + int(hex_data[2], 16)) / 100

        for i in range(12):
            startIdx = i * 100
            if hex_data[startIdx] != "FF" or hex_data[startIdx + 1] != "EE":
                continue
            startAngle = (int(hex_data[startIdx + 3], 16) * 256 + int(hex_data[startIdx+2], 16) ) / 100
            for j in range(startIdx + 4, startIdx + 100, 6):
                distance = int(hex_data[j + 1], 16) * 256 + int(hex_data[j], 16)
                idx = (j - startIdx - 4 + 6) / 6
                pointIdx = startIdx * 16 + idx
                angle0 = startAngle + lidarAngleStep * idx - startAngleDiff
                if distance < 2060 or distance > 3640:
                    continue
                if angle0 < iHorizontalAngle:
                    angle = iHorizontalAngle - angle0
                    h = - int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(angle * math.pi / 180) * distance)
                elif angle0 > iHorizontalAngle:
                    angle = angle0 - iHorizontalAngle
                    h = + int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(angle * math.pi / 180) * distance)

                else:
                    h = 0
                    l = distance
                usedData.append(h)

    average = sum(usedData) / len(usedData)
    while max(usedData) - min(usedData) > 0.5:
        diff = [math.fabs(data - average) for data in usedData]
        m = max(diff)
        index = diff.index(m)
        value = usedData[index]
        usedData.remove(value)
        average = sum(usedData) / len(usedData)

    print("Final height is", -max(usedData) - 50)
    return -max(usedData) - 50


def get_min_l_dg(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, up2down):
    size = len(data)
    my_data = []
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 100 or distance > 5000:
            continue
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = iHorizontalHeight
            l = distance
        my_data.append([l, h])

    if up2down:
        my_data.reverse()
    for l, h in my_data:
        if h < 0 and 500 < l < 2000:
            break

    print("Final minl is", l)
    return l


def get_min_l_test(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, up2down):
    size = len(data)
    my_data = []
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 0 or distance > 2500:
            continue
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = iHorizontalHeight
            l = distance
        my_data.append([l, h])

    if up2down:
        my_data.reverse()
    for idx, one_my_data in enumerate(my_data):
        l = one_my_data[0]
        h = one_my_data[1]
        if h < -20 and 500 < l < 2000:
            for i in range(idx+1, idx+41):
                if my_data[i][1] > 0:
                    flag = False
                    break
                if i == idx+40:
                    flag = True
            if flag:
                break

    print("Final minl is", l)
    return l


def get_min_l_test_270mini(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, up2down, startAngleDiff = 105):
    size = len(data)
    my_data = []
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    loops = data.split("\n")
    if loops[-1] == "":
        loops = loops[:-1]

    for loop in loops:
        hex_data = loop.split(" ")

        if len(hex_data) != 1206 or hex_data[0] != "FF" or hex_data[1] != "EE":
            return
        firstStartAngle = (int(hex_data[3], 16) * 256 + int(hex_data[2], 16)) / 100

        for i in range(12):
            startIdx = i * 100
            if hex_data[startIdx] != "FF" or hex_data[startIdx + 1] != "EE":
                continue
            startAngle = (int(hex_data[startIdx + 3], 16) * 256 + int(hex_data[startIdx+2], 16) ) / 100
            for j in range(startIdx + 4, startIdx + 100, 6):
                distance = int(hex_data[j + 1], 16) * 256 + int(hex_data[j], 16)
                idx = (j - startIdx - 4 + 6) / 6
                pointIdx = startIdx * 16 + idx
                angle0 = startAngle + lidarAngleStep * idx - startAngleDiff
                if distance < 0 or distance > 2500:
                    continue
                if angle0 < iHorizontalAngle:
                    angle = iHorizontalAngle - angle0
                    h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > iHorizontalAngle:
                    angle = angle0 - iHorizontalAngle
                    h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = iHorizontalHeight
                    l = distance
                my_data.append([l, h])

    if up2down:
        my_data.reverse()
    for idx, one_my_data in enumerate(my_data):
        l = one_my_data[0]
        h = one_my_data[1]
        if h < -20 and 500 < l < 2000:
            for i in range(idx+1, idx+41):
                if my_data[i][1] > 0:
                    flag = False
                    break
                if i == idx+40:
                    flag = True
            if flag:
                break

    print("Final minl is", l)
    return l


def get_max_l_dg(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l, up2down):
    size = len(data)
    my_data = []
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    for i in range(int(size / 2)):
        MSB = data[i * 2 + 1]
        LSB = data[i * 2]
        distance = int(MSB, 16) * 256 + int(LSB, 16)
        if distance < 100 or distance > 7000:
            continue
        angle0 = i * lidarAngleStep
        if angle0 < iHorizontalAngle:
            angle = iHorizontalAngle - angle0
            h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        elif angle0 > iHorizontalAngle:
            angle = angle0 - iHorizontalAngle
            h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
            l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
        else:
            h = iHorizontalHeight
            l = distance
        my_data.append([l, h])

    if up2down:
        my_data.reverse()
    for l, h in my_data:
        if l > min_l and h > 100:
            break
    if l - 20 < min_l + 1500:
        return min_l + 1500
    print("Final maxl is", l)
    return l - 20


def get_max_l_test(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l, up2down):
    return min_l + 3000


def get_max_l_test_270mini(data, lidarAngleStep, iHorizontalAngle, iHorizontalHeight, min_l, up2down):
    return min_l + 3000


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
        if 2500 > distance > 1900:
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
            if l1 != l2:
                tan = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
                my_tans.append(tan)
    my_tans_area = [[], [], [], []]
    for tan in my_tans:
        if 0 <= tan < 30:
            my_tans_area[0].append(tan)
        elif 30 <= tan < 60:
            my_tans_area[1].append(tan)
        elif 60 <= tan < 90:
            my_tans_area[2].append(tan)
        else:
            my_tans_area[3].append(tan)
    max_area = max(len(my_tans_area[0]), len(my_tans_area[1]), len(my_tans_area[2]), len(my_tans_area[3]))
    for i in range(4):
        if len(my_tans_area[i]) == max_area:
            my_tans = my_tans_area[i]
    # my_tans = [my_tan for my_tan in my_tans if math.fabs(my_tans[25] - my_tan) <= 10]
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
    if not my_data:
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
