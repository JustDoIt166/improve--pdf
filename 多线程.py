import fitz
import cv2
import os
import re
import threading
import time

# 记录程序开始时间
start_time = time.time()
class ImprovePdf:
    def __init__(self,doc_path,pdf_path, img_path, change_path, erasure_path, pdf_name, final_pdf,core):
        self.doc_path = doc_path
        self.pdf_path = pdf_path
        self.img_path = img_path
        self.change_path = change_path
        self.erasure_path = erasure_path
        self.pdf_name = pdf_name
        self.final_pdf = final_pdf
        self.core = core
    @staticmethod
    def numerical_sort(value):
        numbers = re.findall(r'\d+', value)  # 返回的numbers是一个列表
        return int(numbers[0]) if numbers else -1
    def cont_index(self):
        pdf = fitz.open(self.doc_path)
        index = []
        for pg in range(0,pdf.page_count , 10):
            x = min(pg + 10, pdf.page_count)
            list1 = list(range(pg, x))
            index.append(list1)
            print(list1)
        return index


    def get_image(self, zoom_x, zoom_y, rotation_angle,index):
        # 创建一个信号量，设置最大允许的线程数量为5
        semaphore = threading.Semaphore(self.core)
        with semaphore:
            print(f"Thread {index} 获得了信号量")
            pdf = fitz.open(self.doc_path)
            # pdf转图片
            for pg in index:
                page = pdf[pg]
                # 设置缩放和旋转系数
                trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
                pm = page.get_pixmap(matrix=trans, alpha=False)
                # 开始写图像
                pm.save(os.path.join(self.img_path, str(pg) + ".png"))
                print(f"正在提取第{pg}张图片")
            pdf.close()
            print(f"Thread {index} 释放了信号量")

    def change_image(self,index):
        # 创建一个信号量，设置最大允许的线程数量为5
        semaphore = threading.Semaphore(self.core)
        with semaphore:
            print(f"Thread {index} 获得了信号量")
            # 图片二值化
            img_path1 = os.listdir(self.img_path)
            img_path1 = sorted(img_path1, key=self.numerical_sort)
            for i in index:
                i=img_path1[i]
                if i.endswith('.png'):
                    img = cv2.imread(os.path.join(self.img_path, i), cv2.IMREAD_COLOR)
                    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # 局部阈值
                    binary2 = cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 15) # 推荐25 10 越小越细节 越小更浅变深
                    # 保存图片
                    cv2.imwrite(os.path.join(self.change_path, i), binary2)
                    print(f"正在二值化第{i}张图片")
            print(f"Thread {index} 释放了信号量")
    def erasure_image(self, threshold,index):
        # 创建一个信号量，设置最大允许的线程数量为5
        semaphore = threading.Semaphore(self.core)
        with semaphore:
            print(f"Thread {index} 获得了信号量")
            # threshold为设置清除黑点面积阈值
            img_path1 = os.listdir(self.change_path)
            img_path1 = sorted(img_path1, key=self.numerical_sort)
            for i in index:
                i=img_path1[i]
                if i.endswith('.png'):
                    img = cv2.imread(os.path.join(self.change_path, i), cv2.IMREAD_COLOR)
                    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    contours, hierarch = cv2.findContours(GrayImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    for j in range(len(contours)):
                        area = cv2.contourArea(contours[j])  # 计算轮廓所占面积
                        if area < threshold:
                            cv2.drawContours(img, [contours[j]], -1, (255, 255, 255), thickness=-1)
                            continue
                    cv2.imwrite(os.path.join(self.erasure_path, i), img)  # 保存图片
                    print(f"正在去除第{i}张图片黑点")
            print(f"Thread {index} 释放了信号量")

    def png_to_pdf(self):
        # 创建一个信号量，设置最大允许的线程数量为5
        semaphore = threading.Semaphore(self.core)
        with semaphore:
            print(f"Thread {index} 获得了信号量")
            # 防止字符串乱码
            os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
            # 排序图片地址
            img_path1 = os.listdir(self.erasure_path)
            files = sorted(img_path1, key=self.numerical_sort)
            # 读取图片地址
            for num, img in enumerate(files):
                # 打开空文档
                doc = fitz.open()
                # 打开指定图片
                img_doc = fitz.open(os.path.join(self.erasure_path, img))
                # 使用图片创建单页的PDF
                pdf_bytes = img_doc.convert_to_pdf()
                img_pdf = fitz.open("pdf", pdf_bytes)
                # 将当前页写入文档
                doc.insert_pdf(img_pdf)
                # 一直在保存为指定名称的PDF文件
                doc.save(os.path.join(self.pdf_path, '{}.pdf'.format(num)))
                print(f"正在保存第{num}张pdf")
                # 关闭
                doc.close()
            print(f"Thread {index} 释放了信号量")
    def merge_pdf(self):
        pdf_path1 = os.listdir(self.pdf_path)
        pdf_path2 = sorted(pdf_path1, key=self.numerical_sort)
        pdf_list = pdf_path2
        print(pdf_list)
        PDFWriter = fitz.open()
        for pdf in pdf_list:
            pdf_path = os.path.join(self.pdf_path, pdf)
            pdf_doc = fitz.open(pdf_path)
            PDFWriter.insert_pdf(pdf_doc)

        PDFWriter.save(os.path.join(self.final_pdf, self.pdf_name))


def main():
    doc_path = r"C:\Users\17403\Desktop\elec-power\电动力学导论.pdf"
    final_pdf = os.path.dirname(doc_path)
    pdf_path  = os.path.join(os.path.dirname(doc_path), "pdf")
    img_path = os.path.join(os.path.dirname(doc_path), "img")
    change_path = os.path.join(os.path.dirname(doc_path), "change")
    erasure_path = os.path.join(os.path.dirname(doc_path), "erasure")
    pdf_name = os.path.basename(doc_path).replace(".pdf", "")
    # 检查路径是否存在并创建目录
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)

    if not os.path.exists(img_path):
        os.makedirs(img_path)

    if not os.path.exists(change_path):
        os.makedirs(change_path)

    if not os.path.exists(erasure_path):
        os.makedirs(erasure_path)

    optic_elec = ImprovePdf(
        doc_path=doc_path,
        pdf_path=pdf_path,
        img_path=img_path,
        change_path=change_path,
        erasure_path=erasure_path,
        pdf_name=pdf_name+('(优化版).pdf'),
        final_pdf= final_pdf,
        core=10
    )

    index=optic_elec.cont_index()

      # 多线程
    threads = []

    for i in range(len(index)):  # 这里创建了4个线程，可以根据需要调整
        thread = threading.Thread(target=optic_elec.get_image, args=(5.0, 5.0, 0,index[i]))
        threads.append(thread)
        thread.start()# 开始线程

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # optic_elec.get_image(zoom_x=5.0, zoom_y=5.0, rotation_angle=0)#放大倍数 旋转角度，推荐5倍，倍数过小体积小但效果差
    # optic_elec.change_image()
    # optic_elec.erasure_image(threshold=30)
    # optic_elec.png_to_pdf()
    # optic_elec.merge_pdf()

    threads = []

    for i in range(len(index)):  # 这里创建了4个线程，可以根据需要调整
        thread = threading.Thread(target=optic_elec.change_image,args=(index[i],))
        threads.append(thread)
        thread.start()# 开始线程

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    threads = []
    for i in range(len(index)):
        thread = threading.Thread(target=optic_elec.erasure_image, args=(30,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    optic_elec.png_to_pdf()

    optic_elec.merge_pdf()


if __name__ == '__main__':
    main()
# 记录程序结束时间
end_time = time.time()
# 计算程序运行时间
run_time = end_time - start_time

print(f"程序运行时间为: {run_time} 秒")
