import fitz
import cv2
import os
import re
from multiprocessing import Pool

import time
class ImprovePdf:
    def __init__(self, doc_path, pdf_name):
        self.doc_path = doc_path
        self.pdf_name = pdf_name

        # 创建相关目录
        self.final_pdf = os.path.dirname(doc_path)
        self.pdf_path = os.path.join(self.final_pdf, "pdf")
        self.img_path = os.path.join(self.final_pdf, "img")
        self.change_path = os.path.join(self.final_pdf, "change")
        self.erasure_path = os.path.join(self.final_pdf, "erasure")

        for path in [self.pdf_path, self.img_path, self.change_path, self.erasure_path]:
            if not os.path.exists(path):
                os.makedirs(path)

    def cont_index(self):
        pdf = fitz.open(self.doc_path)
        index = []
        for pg in range(0, pdf.page_count, 10):
            x = min(pg + 10, pdf.page_count)
            list1 = list(range(pg, x))
            index.append(list1)
            # print(list1)
        return index
    @staticmethod
    def numerical_sort(value):
        numbers = re.findall(r'\d+', value)
        return int(numbers[0]) if numbers else value

    def get_image(self, zoom_x, zoom_y, rotation_angle):
        try:
            pdf = fitz.open(self.doc_path)
            for pg in range(len(pdf)):
                page = pdf[pg]
                trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
                pm = page.get_pixmap(matrix=trans, alpha=False)
                pm.save(os.path.join(self.img_path, f"{pg}.png"))
                print(f"正在提取第{pg}张图片")
            pdf.close()
        except Exception as e:
            print(f"提取图片时出现错误: {e}")


    def change_image(self,index):
        try:
            img_files = sorted(os.listdir(self.img_path),key=self.numerical_sort)
            for i in index:
                i=img_files[i]
                if i.endswith('.png'):
                    img = cv2.imread(os.path.join(self.img_path, i), cv2.IMREAD_COLOR)
                    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    binary2 = cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY, 55, 15)
                    cv2.imwrite(os.path.join(self.change_path, i), binary2)
                    print(f"正在二值化第{i}张图片")
        except Exception as e:
            print(f"二值化图片时出现错误: {e}")


    def erasure_image(self, threshold,index):
        try:
            img_files = sorted(os.listdir(self.change_path),key=self.numerical_sort)
            for i in index:
                i=img_files[i]
                if i.endswith('.png'):
                    img = cv2.imread(os.path.join(self.change_path, i), cv2.IMREAD_COLOR)
                    GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    contours, hierarch = cv2.findContours(GrayImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    for j in range(len(contours)):
                        area = cv2.contourArea(contours[j])
                        if area < threshold:
                            cv2.drawContours(img, [contours[j]], -1, (255, 255, 255), thickness=-1)
                            continue
                    cv2.imwrite(os.path.join(self.erasure_path, i), img)
                    print(f"正在去除第{i}张图片黑点")
        except Exception as e:
            print(f"去除黑点时出现错误: {e}")

    def png_to_pdf(self,index):
        try:
            os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
            img_files = sorted(os.listdir(self.erasure_path),key=self.numerical_sort)

            for i in index:
                num=i
                i=img_files[i]
                with fitz.open() as doc:
                    img_doc = fitz.open(os.path.join(self.erasure_path, i))
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_pdf = fitz.open("pdf", pdf_bytes)
                    doc.insert_pdf(img_pdf)
                    doc.save(os.path.join(self.pdf_path, f'{num}.pdf'))
                    print(f"正在保存第{num}张pdf")
        except Exception as e:
            print(f"转换图片到PDF时出现错误: {e}")

    def merge_pdf(self):
        try:
            pdf_files = natsorted(os.listdir(self.pdf_path))
            PDFWriter = fitz.open()
            for pdf in pdf_files:
                pdf_path = os.path.join(self.pdf_path, pdf)
                pdf_doc = fitz.open(pdf_path)
                PDFWriter.insert_pdf(pdf_doc)
            PDFWriter.save(os.path.join(self.final_pdf, self.pdf_name))
        except Exception as e:
            print(f"合并PDF时出现错误: {e}")



def main():
    start_time = time.time()
    doc_path = r"C:\Users\17403\Desktop\liser\激光原理与应用（第四版）-1.pdf"
    pdf_name = os.path.basename(doc_path).replace(".pdf", "(优化版).pdf")

    optic_elec = ImprovePdf(doc_path, pdf_name)

    index=optic_elec.cont_index()
    optic_elec.get_image(zoom_x=5.0, zoom_y=5.0, rotation_angle=0)

    p=Pool(3)#创建进程池，并发进程数

    try:
        for i in range(0,len(index),3):
            tasks = []
            for j in range(i,i+3):
                if j < len(index):
                    i = index[j]
                    print(i)
                    p.apply_async(optic_elec.change_image,(i,))

                else:
                    pass

    except Exception as e:
            print(f"二值化出现错误: {e}")


    try:
        for i in range(0,len(index),10):
            tasks = []
            for j in range(i,i+10):
                if j < len(index):
                    j=index[j]
                    p.apply_async(optic_elec.erasure_image, (30,j,))
                else:
                    pass

    except Exception as e:
            print(f"去除出现错误: {e}")


    try:
        for i in range(0,len(index),10):
            tasks = []
            for j in range(i,i+10):
                if j < len(index):
                    j=index[j]
                    p.apply_async(optic_elec.png_to_pdf, (j,))
                else:
                    pass
    except Exception as e:
            print(f"转pdf出现错误: {e}")

    p.close()
    p.join()

    end_time = time.time()
    # 计算程序运行时间
    run_time = end_time - start_time

    print(f"程序运行时间为: {run_time} 秒")


if __name__ == '__main__':
    main()
