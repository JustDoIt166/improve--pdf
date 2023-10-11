import re

# 正则表达式模式
tittle_pattern = r"第[一二三四五六七八九十百千万零]+章"
section_pattern = r"\d+\.\d+"
pagination_pattern = r"\d+"

with open("目录.txt", "r", encoding="utf-8") as f:
    text = f.read()
    lines = text.split("\n")
list1 = []
page_list = []
for line in lines:
    if re.search(tittle_pattern, line):
        list1.append(line)
        print(f"章节信息: {line}")
    elif re.search(section_pattern, line):
        list1.append(line)
        print(f"小节信息: {line}")
    elif re.search(pagination_pattern, line):
        page_list.append(line)
        print(f"页码信息: {line}")
    else:
        list1.append(line)
        print("未匹配到任何信息。")
print(list1, page_list, sep="\n")
if len(list1) == len(page_list):
    with open("目录.txt", "w", encoding="utf-8") as f:
        for i in range(len(list1)):
            f.write(list1[i] + " " + page_list[i] + "\n")
    print("章节信息和页码信息数量相同。")
else:
    print("章节信息和页码信息数量不同,请检查目录文件。")
