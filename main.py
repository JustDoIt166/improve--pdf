import fitz
import cv2
import os
import re

class ImprovePdf:
    def __init__(self, pdf_path, img_path, change_path, erasure_path, pdf_name):
        self.pdf_path = pdf_path
        self.img_path = img_path
        self.change_path = change_path
        self.erasure_path = erasure_path
        self.pdf_name = pdf_name

    def get_image(self, zoom_x, zoom_y, rotation_angle):
        pdf = fitz.open(self.pdf_path)
        # pdf转图片
        for pg in range(0, pdf.page_count):
            page = pdf[pg]
            # 设置缩放和旋转系数
            trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
            pm = page.get_pixmap(matrix=trans, alpha=False)
            # 开始写图像
            pm.save(os.path.join(self.img_path, str(pg) + ".png"))
        pdf.close()

    def change_image(self):
        # 图片二值化
        img_path1 = os.listdir(self.img_path)
        for i in img_path1:
            if i.endswith('.png'):
                img = cv2.imread(os.path.join(self.img_path, i), cv2.IMREAD_COLOR)
                GrayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # 局部阈值
                binary2 = cv2.adaptiveThreshold(GrayImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 10)
                # 保存图片
                cv2.imwrite(os.path.join(self.change_path, i), binary2)

    def erasure_image(self, threshold):
        # threshold为设置清除黑点面积阈值
        img_path1 = os.listdir(self.change_path)
        for i in img_path1:
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

    @staticmethod
    def numerical_sort(value):
        numbers = re.findall(r'\d+', value)  # 返回的numbers是一个列表
        return int(numbers[0]) if numbers else -1

    def png_to_pdf(self):
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
            # 关闭
            doc.close()

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
        PDFWriter.save(os.path.join(self.pdf_path, self.pdf_name))


def main():

    optic_elec = ImprovePdf(
        pdf_path=r"C:\Users\17403\Desktop\optic-elec\pdf",
        img_path=r"C:\Users\17403\Desktop\optic-elec\img",
        change_path=r"C:\Users\17403\Desktop\optic-elec\change",
        erasure_path=r"C:\Users\17403\Desktop\optic-elec\erasure",
        pdf_name="example.pdf"
    )
    optic_elec.get_image(zoom_x=2.0, zoom_y=2.0, rotation_angle=0)
    optic_elec.change_image()
    optic_elec.erasure_image(threshold=30)
    optic_elec.png_to_pdf()
    optic_elec.merge_pdf()

if __name__ == '__main__':
    main()
