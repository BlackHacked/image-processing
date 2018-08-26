
#include "cuda_runtime.h"
#include "device_launch_parameters.h"

#include<opencv2/opencv.hpp>
#include <stdio.h>
#include <iostream>

using namespace std;
using namespace cv;

//��������
#define CHECK_ERROR(call){\
    const cudaError_t err = call;\
    if (err != cudaSuccess)\
    {\
        printf("Error:%s,%d,",__FILE__,__LINE__);\
        printf("code:%d,reason:%s\n",err,cudaGetErrorString(err));\
        exit(1);\
    }\
}

//�ں˺�����ʵ�����·�ת
__global__ void swap_image_kernel(cuda::PtrStepSz<uchar3> cu_src, cuda::PtrStepSz<uchar3> cu_dst, int h, int w)
{
	//����ķ������ο�ǰ������
	unsigned int x = blockDim.x * blockIdx.x + threadIdx.x;
	unsigned int y = blockDim.y * blockIdx.y + threadIdx.y;
	//ΪɶҪ�������ƣ��ο�ǰ������
	if (x < cu_src.cols && y < cu_src.rows)
	{
		//Ϊ�β���h-y-1,������h-y���Լ�˼��Ŷ
		cu_dst(y, x) = cu_src(h - y - 1, x);
	}
}
//���ú�������Ҫ����block��grid�Ĺ�ϵ
void swap_image(cuda::GpuMat src, cuda::GpuMat dst, int h, int w)
{
	assert(src.cols == w && src.rows == h);
	int uint = 32;
	//�ο�ǰ�����ĵ�block��grid�ļ��㷽����ע�ⲻҪ����GPU����
	dim3 block(uint, uint);
	dim3 grid((w + block.x - 1) / block.x, (h + block.y - 1) / block.y);
	printf("grid = %4d %4d %4d\n", grid.x, grid.y, grid.z);
	printf("block= %4d %4d %4d\n", block.x, block.y, block.z);
	swap_image_kernel << <grid, block >> > (src, dst, h, w);
	//ͬ��һ�£���Ϊ���������ܴܺ�
	CHECK_ERROR(cudaDeviceSynchronize());
}
int main(int argc, char **argv)
{
	Mat src, dst;
	cuda::GpuMat cu_src, cu_dst;
	int h, w;
	//����argv[1]����ͼƬ���ݣ�BGR��ʽ������
	src = imread(argv[1]);
	//����Ƿ���ȷ����
	if (src.data == NULL)
	{
		cout << "Read image error" << endl;
		return -1;
	}
	h = src.rows; w = src.cols;
	cout << "ͼƬ�ߣ�" << h << ",ͼƬ��" << w << endl;
	//�ϴ�CPUͼ�����ݵ�GPU����cudaMalloc��cudaMemcpy����Ŷ����ʵupload���������ôд��
	cu_src.upload(src);
	//����GPU�ռ䣬Ҳ���Ե����������룬����������Ҫ���룬Ҫ��Ȼ�ں˺����ᱬ��Ŷ
	cu_dst = cuda::GpuMat(h, w, CV_8UC3, Scalar(0, 0, 0));
	//����CPU�ռ�
	dst = Mat(h, w, CV_8UC3, Scalar(0, 0, 0));
	//���ú���swap_image,�ɸú��������ں˺�����������η����������׳���
	//��Ȼ��Ҳ����ֱ������������ں˺���������̫�����������
	swap_image(cu_src, cu_dst, h, w);
	//����GPU���ݵ�CPU����upload()��Ӧ
	cu_dst.download(dst);
	//��ʾcpuͼ�������װ��openCV������openGL,�ǿ���ֱ����ʾGpuMat
	imshow("dst", dst);
	//�ȴ�����
	waitKey();
	//дͼƬ���ļ�
	if (argc == 3)
		imwrite(argv[2], dst);
	return 0;
}
