# created at 2018-05-11

# updated at 2018-08-23
# support multi-faces now

# By        coneypo
# Blog:     http://www.cnblogs.com/AdaminXie
# GitHub:   https://github.com/coneypo/Dlib_face_recognition_from_camera

import dlib  # 人脸识别的库dlib
import numpy as np  # 数据处理的库numpy
import cv2  # 图像处理的库OpenCv
import pandas as pd  # 数据处理的库Pandas

# face recognition model, the object maps human faces into 128D vectors
facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")


# 计算两个向量间的欧式距离
def return_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    print("e_distance: ", dist)

    if dist > 0.4:
        return "diff"
    else:
        return "same"


# 处理存放所有人脸特征的csv
path_features_known_csv = "F:/code/python/P_dlib_face_reco/data/features_all.csv"

# path_features_known_csv= "/media/con/data/code/python/P_dlib_face_reco/data/csvs/features_all.csv"
csv_rd = pd.read_csv(path_features_known_csv, header=None)

# 存储的特征人脸个数
# print(csv_rd.shape[0])

# 用来存放所有录入人脸特征的数组
features_known_arr = []

for i in range(csv_rd.shape[0]):
    features_someone_arr = []
    for j in range(0, len(csv_rd.ix[i, :])):
        features_someone_arr.append(csv_rd.ix[i, :][j])
    #    print(features_someone_arr)
    features_known_arr.append(features_someone_arr)
print("Faces in Database：", len(features_known_arr))

# Dlib 预测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('../resources/models/dlib/shape_predictor_68_face_landmarks.dat')

# 创建 cv2 摄像头对象
cap = cv2.VideoCapture(0)

# cap.set(propId, value)
# 设置视频参数，propId设置的视频参数，value设置的参数值
cap.set(3, 480)


# 返回一张图像多张人脸的128D特征
def get_128d_features(img_gray):
    dets = detector(img_gray, 1)
    if len(dets) != 0:
        face_des = []
        for i in range(len(dets)):
            shape = predictor(img_gray, dets[i])
            face_des.append(facerec.compute_face_descriptor(img_gray, shape))
    else:
        face_des = []
    return face_des


# cap.isOpened（） 返回true/false 检查初始化是否成功
while cap.isOpened():

    # cap.read()
    # 返回两个值：
    #    一个布尔值true/false，用来判断读取视频是否成功/是否到视频末尾
    #    图像对象，图像的三维矩阵
    flag, im_rd = cap.read()

    # 每帧数据延时1ms，延时为0读取的是静态帧
    kk = cv2.waitKey(1)

    # 取灰度
    img_gray = cv2.cvtColor(im_rd, cv2.COLOR_RGB2GRAY)

    # 人脸数 dets
    dets = detector(img_gray, 0)

    # 待会要写的字体
    font = cv2.FONT_HERSHEY_SIMPLEX

    cv2.putText(im_rd, "q: quit", (20, 400), font, 0.8, (84, 255, 159), 1, cv2.LINE_AA)

    # 存储人脸名字和位置的两个 list
    # list 1 (dets): store the name of faces                Jack    unknown unknown Mary
    # list 2 (pos_namelist): store the positions of faces   12,1    1,21    1,13    31,1

    # 存储所有人脸的名字
    pos_namelist = []
    name_namelist = []

    if len(dets) != 0:
        # 检测到人脸

        # 获取当前捕获到的图像的所有人脸的特征，存储到 features_cap_arr
        features_cap_arr = []
        for i in range(len(dets)):
            shape = predictor(im_rd, dets[i])
            features_cap_arr.append(facerec.compute_face_descriptor(im_rd, shape))

        # 遍历捕获到的图像中所有的人脸
        for k in range(len(dets)):
            # 让人名跟随在矩形框的下方
            # 确定人名的位置坐标
            # 先默认所有人不认识，是 unknown
            name_namelist.append("unknown")

            # 每个捕获人脸的名字坐标
            pos_namelist.append(tuple([dets[k].left(), int(dets[k].bottom() + (dets[k].bottom() - dets[k].top()) / 4)]))

            # 对于某张人脸，遍历所有存储的人脸特征
            for i in range(len(features_known_arr)):
                # 将某张人脸与存储的所有人脸数据进行比对
                compare = return_euclidean_distance(features_cap_arr[k], features_known_arr[i])
                if compare == "same":  # 找到了相似脸
                    name_namelist[k] = "person_" + str(i)

            # 矩形框
            for kk, d in enumerate(dets):
                # 绘制矩形框
                cv2.rectangle(im_rd, tuple([d.left(), d.top()]), tuple([d.right(), d.bottom()]), (0, 255, 255), 2)

        # 写人脸名字
        for i in range(len(dets)):
            cv2.putText(im_rd, name_namelist[i], pos_namelist[i], font, 0.8, (0, 255, 255), 1, cv2.LINE_AA)

    print("Name list:", name_namelist, "\n")

    cv2.putText(im_rd, "faces: " + str(len(dets)), (20, 50), font, 1, (0, 0, 255), 1, cv2.LINE_AA)

    # 按下q键退出
    if kk == ord('q'):
        break

    # 窗口显示
    cv2.imshow("camera", im_rd)

# 释放摄像头
cap.release()

# 删除建立的窗口
cv2.destroyAllWindows()