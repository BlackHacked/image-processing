#include <iostream>
#include <opencv2/opencv.hpp>

using namespace std;

int main()
{
    cv::Mat src = cv::imread("../../../../../../datas/face3.jpg");
    if(src.empty()){
        std::cerr << "cannot open image" << std::endl;
        return -1;
    }
    cv::Mat dst;
    cv::bilateralFilter(src,dst,7,2.4,2.4);

    cv::imshow("src",src);
    cv::imshow("dst",dst);

    cv::waitKey();
    cv::destroyAllWindows();
    return 0;
}
