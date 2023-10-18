import re


class Catalog:
    def __init__(self, path):
        self.tittle_pattern = r"第(?:[一二三四五六七八九十百千万零]+|\d+)章"
        self.section_pattern = r"\d+(?:\.\d+)+"
        self.pagination_pattern = r"\d+"
        self.other_pattern = r"[\u4e00-\u9fa5a-zA-Z]+"
        self.path = path
        self.tittle_list = []
        self.section_list = []
        self.pagination_list = []
        self.other_list = []
        self.bool = None
        self.final_list = []

    def codify(self):
        with open(self.path, "r", encoding="utf-8") as f:
            text = f.read()
            lines = text.split("\n")
        with open("目录(yema).txt", "w", encoding="utf-8") as f:
            # 分类
            for line in lines:
                line = re.sub(r"\.\.+", "", line)
                line = re.sub(r"…", "", line)
                line = (
                    line.replace("(", "")
                    .replace(")", "")
                    .replace("（", "")
                    .replace("）", "")
                )
                # 使用单独的if语句，而不是elif，以匹配多个模式
                if re.search(self.tittle_pattern, line):
                    self.tittle_list.extend(re.findall(self.tittle_pattern, line))
                    line = re.sub(self.tittle_pattern, "", line)
                if re.search(self.section_pattern, line):
                    self.section_list.extend(re.findall(self.section_pattern, line))
                    line = re.sub(self.section_pattern, "", line)
                line.replace("(", "").replace(")", "").replace("（", "").replace("）", "")
                if re.search(self.pagination_pattern, line):
                    line = line.replace(".", "")
                    self.pagination_list.extend(
                        re.findall(self.pagination_pattern, line)
                    )
                f.write(line + "\n")

    def get_toc(self):
        with open("目录(yema).txt", "r", encoding="utf-8") as f:
            f = f.read()
            f = re.sub(r"\n", "", f)
            f = re.sub(r"[,， ]", "", f)
            f = re.split(r"\d+", f)
            del f[-1]
            print(f)
            self.other_list = f
        print(
            "章节数:" + str(len(self.tittle_list)),
            "小节数:" + str(len(self.section_list)),
            "页码数:" + str(len(self.pagination_list)),
            "标题数:" + str(len(self.other_list)),
            sep="\n",
        )
        if len(self.tittle_list) + len(self.section_list) == len(self.pagination_list):
            print("目录提取成功")
            self.bool = True
        else:
            print("目录提取失败,请检查目录是否正确")
            self.bool = False
        list1 = []
        for i in range(len(self.tittle_list)):
            list1.append(["1", f"{self.tittle_list[i]}"])
            for j in self.section_list:
                t = int(j.split(".")[0])
                # print(t)
                if i + 1 == t:
                    list1.append(["2", f"{j}"])
        self.final_list = []
        for i in range(len(list1)):
            l = list1[i]
            l.append(f"{self.other_list[i]}")
            l.append(f"{self.pagination_list[i]}")
            self.final_list.append(l)
        with open("目录(toc).txt", "w", encoding="utf-8") as f:
            f.write(str(self.final_list))
        with open("目录(final).txt", "w", encoding="utf-8") as f:
            for i in self.final_list:
                f.write(f"{i[1]} {i[2]}…{i[3]}\n")


def main():
    path = "目录.txt"
    catalog = Catalog(path)
    catalog.codify()
    catalog.get_toc()


if __name__ == "__main__":
    main()
