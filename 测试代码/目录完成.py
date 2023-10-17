import re

tittle_pattern = r"第(?:[一二三四五六七八九十百千万零]+|\d+)章"

section_pattern = r"\d+(?:\.\d+)+"

pagination_pattern = r"\d+"  # 纯数字，考虑数字两边的边界
other_pattern = r"[\u4e00-\u9fa5a-zA-Z]+"

with open("目录.txt", "r", encoding="utf-8") as f:
    text = f.read()
    lines = text.split("\n")
    tittle_list = []
    section_list = []
    pagination_list = []
    other_list = []
with open("目录(yema).txt", "w", encoding="utf-8") as f:
    # 分类
    for line in lines:
        line = re.sub(r"\.\.+", "", line)
        line = re.sub(r"…", "", line)
        print(line)
        # 使用单独的if语句，而不是elif，以匹配多个模式
        if re.search(tittle_pattern, line):
            tittle_list.extend(re.findall(tittle_pattern, line))
            line = re.sub(tittle_pattern, "", line)
            # print("tittle", line)
        if re.search(section_pattern, line):
            section_list.extend(re.findall(section_pattern, line))
            line = re.sub(section_pattern, "", line)
            # print("section", line)
        if re.search(pagination_pattern, line):
            line = re.sub(r"\.", "", line)
            # line = re.sub(r"\.", "", line)
            print("page" + line)
            pagination_list.extend(re.findall(pagination_pattern, line))
            # line = re.sub(pagination_pattern, "", line)

        f.write(line + "\n")

        # if re.search(pagination_pattern, line):
        #     pagination_list.extend(re.findall(pagination_pattern, line))
        # if re.search(other_pattern, line):
        #     other_list.extend(re.findall(other_pattern, line))
        #
        #
    #
    print(tittle_list)
    print(section_list)
    print(pagination_list)
    print(other_list)
    print(
        len(tittle_list),
        len(section_list),
        len(pagination_list),
        len(other_list),
        sep="\n",
    )
with open("目录(yema).txt", "r", encoding="utf-8") as f:
    f = f.read()
    f = re.sub(r"\n", "", f)
    f = re.sub(r"[,,， ]", "", f)
    f = re.split(r"\d+", f)
    del f[-1]
    other_list = f
    print(f)
    print(other_list)
    print(
        len(tittle_list),
        len(section_list),
        len(pagination_list),
        len(other_list),
        sep="\n",
    )
list1 = []
for i in range(len(tittle_list)):
    list1.append(["0", f"{tittle_list[i]}"])
    for j in section_list:
        t = int(j.split(".")[0])
        print(t)
        if i + 1 == t:
            list1.append(["1", f"{j}"])
print(list1)
fina = []
for i in range(len(list1)):
    l = list1[i]
    l.append(f"{other_list[i]}")
    l.append(f"{pagination_list[i]}")
    fina.append(l)
print(fina)
