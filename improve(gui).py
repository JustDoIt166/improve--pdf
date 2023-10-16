# -*- coding: utf-8 -*-

import os
import re
import time
from multiprocessing import Pool
import numpy as np
import cv2
import fitz


class ImprovePdf:
    def __init__(self, doc_path):
        self.doc_path = doc_path
        self.pdf_name = os.path.basename(self.doc_path).replace(".pdf", "(优化版).pdf")
        self.core = os.cpu_count()-4
        self.pagination = None
        # 创建相关目录
        self.final_pdf = os.path.dirname(doc_path)
        self.dir_name = os.path.basename(doc_path).replace(".pdf", "")
        self.final_pdf = os.path.join(self.final_pdf, self.dir_name)
        self.pdf_path = os.path.join(self.final_pdf, "pdf")
        self.img_path = os.path.join(self.final_pdf, "img")
        self.change_path = os.path.join(self.final_pdf, "change")
        self.erasure_path = os.path.join(self.final_pdf, "erasure")
        self.log=[]
        for path in [self.final_pdf, self.pdf_path, self.img_path, self.change_path, self.erasure_path]:
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception as e:
                    print(f"创建目录时出现错误: {e}")

    def cont_index(self):
        pdf = fitz.open(self.doc_path)
        index = []
        t = pdf.page_count // self.core
        for pg in range(0, pdf.page_count, t):
            x = min(pg + t, pdf.page_count)
            list1 = list(range(pg, x))
            index.append(list1)
            # print(list1)
        return index

    @staticmethod
    def numerical_sort(value):
        numbers = re.findall(r"\d+", value)
        return int(numbers[0]) if numbers else value

    def get_doc(self):
        pdf = fitz.open(self.doc_path)
        self.pagination = pdf.get_toc()

        if not self.pagination:
            try:
                with open("toc.txt", "r", encoding="utf-8") as f:
                    self.pagination = list(f)
            except Exception as e:
                pass
                print(f"读取目录时出现错误: {e}")
        else:
            print("目录读取成功")
            print(self.pagination)
        pdf.close()

    def get_image(self, zoom_x, zoom_y, rotation_angle, index):
        try:
            pdf = fitz.open(self.doc_path)
            # pdf转图片
            for pg in index:
                page = pdf[pg]
                # 设置缩放和旋转系数
                trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
                pm = page.get_pixmap(matrix=trans, alpha=False)
                # 开始写图像
                pm.save(os.path.join(self.img_path, str(pg) + ".png"))
                self.log.append(f"正在提取第{pg}张图片")
                print(f"正在提取第{pg}张图片")
            pdf.close()
        except Exception as e:
            self.log.append(f"提取图片时出现错误: {e}")
            print(f"提取图片时出现错误: {e}")

    def change_image(self, index):
        try:
            img_files = sorted(os.listdir(self.img_path), key=self.numerical_sort)
            for i in index:
                i = img_files[i]
                if i.endswith(".png"):
                    path = os.path.join(self.img_path, i)
                    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
                    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    binary2 = cv2.adaptiveThreshold(
                        GrayImage,
                        255,
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY,
                        55,
                        15,
                    )
                    # cv2.imwrite(os.path.join(self.change_path, i), binary2)
                    cv2.imencode('.png', binary2)[1].tofile(os.path.join(self.change_path, i))
                    self.log.append(f"正在二值化第{i}张图片")
                    print(f"正在二值化第{i}张图片")

        except Exception as e:
            self.log.append(f"二值化图片时出现错误: {e}")
            print(f"二值化图片时出现错误: {e}")

    def erasure_image(self, threshold, index):
        try:
            img_files = sorted(os.listdir(self.change_path), key=self.numerical_sort)
            for i in index:
                i = img_files[i]
                if i.endswith(".png"):
                    path= os.path.join(self.change_path, i)
                    # img = cv2.imread(
                    #     os.path.join(self.change_path, i), cv2.IMREAD_COLOR
                    # )
                    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
                    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    contours, hierarch = cv2.findContours(
                        GrayImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
                    )
                    for j in range(len(contours)):
                        area = cv2.contourArea(contours[j])
                        if area < threshold:
                            cv2.drawContours(
                                img, [contours[j]], -1, (255, 255, 255), thickness=-1
                            )
                            continue
                    # cv2.imwrite(
                    #     os.path.join(self.erasure_path, i),
                    #     img,
                    #     [cv2.IMWRITE_PNG_COMPRESSION, 9],
                    # )
                    # 设置PNG压缩参数，0表示无压缩，9表示最大压缩
                    compression_params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
                    cv2.imencode('.png', img,compression_params)[1].tofile(os.path.join(self.erasure_path, i))
                    self.log.append(f"正在去除第{i}张图片黑点")
                    print(f"正在去除第{i}张图片黑点")
        except Exception as e:
            self.log.append(f"去除黑点时出现错误: {e}")
            print(f"去除黑点时出现错误: {e}")

    def png_to_pdf(self, index):
        try:
            os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.UTF8"
            img_files = sorted(os.listdir(self.erasure_path), key=self.numerical_sort)

            for i in index:
                num = i
                i = img_files[i]
                with fitz.open() as doc:
                    img_doc = fitz.open(os.path.join(self.erasure_path, i))
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_pdf = fitz.open("pdf", pdf_bytes)
                    doc.insert_pdf(img_pdf)
                    doc.save(os.path.join(self.pdf_path, f"{num}.pdf"))
                    self.log.append(f"正在保存第{num}张pdf")
                    print(f"正在保存第{num}张pdf")
        except Exception as e:
            self.log.append(f"转换图片到PDF时出现错误: {e}")
            print(f"转换图片到PDF时出现错误: {e}")

    def merge_pdf(self):
        try:
            pdf_files = sorted(os.listdir(self.pdf_path), key=self.numerical_sort)
            PDFWriter = fitz.open()
            for pdf in pdf_files:
                pdf_path = os.path.join(self.pdf_path, pdf)
                pdf_doc = fitz.open(pdf_path)
                PDFWriter.insert_pdf(pdf_doc)
            PDFWriter.set_toc(self.pagination)
            PDFWriter.save(os.path.join(self.final_pdf, self.pdf_name))
        except Exception as e:
            self.log.append(f"合并PDF时出现错误: {e}")
            print(f"合并PDF时出现错误: {e}")

    def start(self):
        start_time = time.time()
        self.get_doc()
        index = self.cont_index()
        pool = Pool(self.core)  # 创建进程池，并发进程数
        self.log.append(f"你的CPU核心数为: {self.core+1}")
        print(f"你的CPU核心数为: {self.core}+1")
        # 多线程提取图片
        for i in index:
            pool.apply_async(self.get_image, args=(5.0, 5.0, 0, i))
            print(i)
        pool.close()
        pool.join()
        # 多线程二值化图片
        pool = Pool(self.core)  # 创建进程池，并发进程数
        for i in index:
            pool.apply_async(self.change_image, args=(i,))
            print(i)
        pool.close()
        pool.join()

        # 多线程去除图片黑点
        pool = Pool(self.core)  # 创建进程池，并发进程数
        for i in index:
            pool.apply_async(self.erasure_image, args=(30, i))
            print(i)
        pool.close()
        pool.join()
        # 多线程转换图片到PDF
        pool = Pool(self.core)  # 创建进程池，并发进程数
        for i in index:
            pool.apply_async(self.png_to_pdf, args=(i,))
            print(i)
        pool.close()
        pool.join()
        self.merge_pdf()
        end_time = time.time()
        # 计算程序运行时间
        run_time = end_time - start_time
        self.log.append(f"处理{self.pdf_name}时间为: {run_time} 秒")
        print(f"处理{self.pdf_name}时间为: {run_time} 秒")


# def main():
#     start_time = time.time()
#     doc_path = r"C:\Users\17403\Downloads\Documents\(1)复变函数论第4版.pdf"
#
#
#     optic_elec = ImprovePdf(doc_path)
#     optic_elec.get_doc()
#     index = optic_elec.cont_index()
#
#     pool = Pool(optic_elec.core)  # 创建进程池，并发进程数
#     print(f"你的CPU核心数为: {optic_elec.core}")
#     # 多线程提取图片
#     for i in index:
#         pool.apply_async(optic_elec.get_image, args=(5.0, 5.0, 0, i))
#         print(i)
#     pool.close()
#     pool.join()
#
#     # 多线程二值化图片
#     pool = Pool(optic_elec.core)  # 创建进程池，并发进程数
#     for i in index:
#         pool.apply_async(optic_elec.change_image, args=(i,))
#         print(i)
#     pool.close()
#     pool.join()
#
#     # 多线程去除图片黑点
#     pool = Pool(optic_elec.core)  # 创建进程池，并发进程数
#     for i in index:
#         pool.apply_async(optic_elec.erasure_image, args=(30, i))
#         print(i)
#     pool.close()
#     pool.join()
#     # 多线程转换图片到PDF
#     pool = Pool(optic_elec.core)  # 创建进程池，并发进程数
#     for i in index:
#         pool.apply_async(optic_elec.png_to_pdf, args=(i,))
#         print(i)
#     pool.close()
#     pool.join()
#     optic_elec.merge_pdf()
#     end_time = time.time()
#     # 计算程序运行时间
#     run_time = end_time - start_time
#
#     print(f"程序运行时间为: {run_time} 秒")
#
#
# if __name__ == "__main__":
#     main()

# def main():
#     doc_path = r"C:\Users\17403\Downloads\Documents\(1)复变函数论第4版.pdf"
#     t = ImprovePdf(doc_path)
#     t.start()
#
#
# if __name__ == "__main__":
#     main()