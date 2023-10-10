import concurrent.futures as cf
import os
import time

import fitz


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

    def get_image(self, zoom_x, zoom_y, rotation_angle):
        tp = cf.ThreadPoolExecutor(8)
        start = time.time()
        pdf = fitz.open(self.doc_path)
        futures = []
        # pdf转图片
        for pg in range(pdf.page_count):
            page = pdf[pg]
            # 设置缩放和旋转系数
            trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
            pm = page.get_pixmap(matrix=trans, alpha=False)
            # 开始写图像
            t = pm.save(os.path.join(self.img_path, str(pg) + ".png"))
            future = tp.submit(t)
            futures.append(future)
            print(f"正在提取第{pg}张图片")
        tp.shutdown()

        pdf.close()
        end = time.time()
        print(f"提取图片耗时: {end - start}秒")


def main():
    doc_path = r"C:\Users\17403\Desktop\xd\程序员的数学3线性代数.pdf"
    pdf_name = os.path.basename(doc_path).replace(".pdf", "(优化版).pdf")
    optic_elec = ImprovePdf(doc_path, pdf_name)
    optic_elec.get_image(zoom_x=5.0, zoom_y=5.0, rotation_angle=0)


if __name__ == "__main__":
    main()
