#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudabgsegm.hpp>
#include <opencv2/cudacodec.hpp>
#include <opencv2/cudafeatures2d.hpp>
#include <opencv2/cudafilters.hpp>
#include <opencv2/cudaimgproc.hpp>
#include <opencv2/cudalegacy.hpp>
#include <opencv2/cudaobjdetect.hpp>
#include <opencv2/cudastereo.hpp>
#include <opencv2/cudawarping.hpp>
#define CVUI_IMPLEMENTATION
#include <cvui.h>
extern "C"{
#include <uv.h>
}

using namespace std;
#define WINDOW_NAME	"CUDA createCLAHE"
cv::Mat src1,src2,dst,roi1,roi2,dst_roi,frame;
cv::Mat src1_rz;
int m_type = 1;
int setting_width = 200,setting_height=300;
int offset = 10;
cv::Mat dst_rz;

cv:: Ptr<cv::cuda::CLAHE> clahe;

void wait_for_a_while(uv_idle_t* handle){
    frame = cv::Scalar(49, 52, 49);
    cvui::window(frame, 10, 10, 200, 300, "Settings");
    src2.copyTo(roi2);
    src1_rz.copyTo(roi1);

    if (cvui::button(frame, 20, 230,180,30, "createCLAHE")) {
//        cv::Mat gray;
//        cv::cvtColor(src1,gray,cv::COLOR_BGR2GRAY);
        clahe = cv::cuda::createCLAHE();
//        cv::cuda::GpuMat dev_src(gray),dev_dst;
//        clahe->apply(dev_src,dev_dst);
//        dev_dst.download(dst);
//        cv::cvtColor(dst,dst,cv::COLOR_GRAY2BGR);
//        cv::resize(dst,dst_rz,cv::Size(dst.cols/2,dst.rows/2));
        std::vector<cv::Mat> channels;
        std::vector<cv::Mat> dst_channels;
        cv::split(src1,channels);
        for(int i = 0;i < channels.size();i++){
            cv::cuda::GpuMat dev_src(channels[i]),dev_dst;
            clahe->apply(dev_src,dev_dst);
            cv::Mat res;
            dev_dst.download(res);
            dst_channels.push_back(res);
        }
//        cv::Mat result;
        cv::merge(dst_channels,dst);
        cv::resize(dst,dst_rz,cv::Size(dst.cols/2,dst.rows/2));
    }

    if(!dst.empty()){
        dst_rz.copyTo(dst_roi);
    }

    cvui::update();

    // Show everything on the screen
    cv::imshow(WINDOW_NAME, frame);

    // Check if ESC was pressed
    if (cv::waitKey(30) == 27) {
        uv_idle_stop(handle);
    }

}

int main()
{
    cv::cuda::printShortCudaDeviceInfo(cv::cuda::getDevice());
    src1 = cv::imread("D:/Develop/DL/projects/digital-image-processing/datas/f1.jpg");
    src2 = cv::imread("D:/Develop/DL/projects/digital-image-processing/datas/f2.jpg");
//    std::cout << src1.size() << "," << src2.size() << std::endl;
    frame = cv::Mat(680,1024,CV_8UC3);
    roi1 = frame(cv::Rect(setting_width+offset*2,offset,src1.cols / 2,src1.rows / 2));
    roi2 = frame(cv::Rect(setting_width+offset*3+src1.cols/2,offset,src2.cols/2,src2.rows/2));

    cv::resize(src1,src1_rz,cv::Size(src1.cols/2,src1.rows/2));


    int dst_x = setting_width + offset*2;
    int dst_y = (offset * 2 + src1.rows / 2);
    dst_roi = frame(cv::Rect(dst_x,dst_y,src1.cols/2,src1.rows/2));
    cvui::init(WINDOW_NAME);
    uv_idle_t idler;
    uv_idle_init(uv_default_loop(), &idler);
    uv_idle_start(&idler, wait_for_a_while);

    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    cv::destroyAllWindows();
    return 0;

}
