from ebooklib import epub

def extract_text_from_epub(epub_file):
    # 打开 EPUB 文件
    book = epub.read_epub(epub_file)

    # 初始化一个空字符串来保存提取的文本
    extracted_text = ''

    # 遍历 EPUB 中的每个项目
    for item in book.items:
        if isinstance(item, epub.EpubHtml):
            # 提取 HTML 内容
            content = item.content.decode('utf-8')
            extracted_text += content

    return extracted_text

# 替换为你的 EPUB 文件路径
epub_file_path = r"C:\Users\17403\Downloads\新概念英语第三册.epub"

# 提取文本
extracted_text = extract_text_from_epub(epub_file_path)

# 保存提取的文本到一个文件
with open('extracted_text.txt', 'w', encoding='utf-8') as file:
    file.write(extracted_text)
