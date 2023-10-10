import cv2


class Compress:
    def __init__(self, path):
        self.path = path

    def compress(self):
        img = cv2.imread(self.path)

        # 保存路径

        # opencv png格式压缩

        cv2.imwrite(
            r"C:\Users\17403\Desktop\li\erasure\c1.png",
            img,
            [cv2.IMWRITE_PNG_COMPRESSION, 9],
        )
        print("Compressed Image Saved Successfully!")


t = Compress(r"C:\Users\17403\Desktop\li\erasure\1.png")
t.compress()
