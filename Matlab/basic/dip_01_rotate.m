clc;
clear;
img = imread('../../datas/f4.jpg');
%��ת90��
dst = imrotate(img,90);
imshow(dst);