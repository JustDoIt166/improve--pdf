# improve-pdf
## 原理：
pdf转成png图片
再使用opencv对图片局部阈值二值化处理
并去除孤立噪点，优化图片观感
最后转回pdf并合并，最终达到优化提高pdf清晰度的目的
（可选）使用potrace处理png转成svg矢量图，使文字线条平滑，观感大幅度提高，接近ocr pdf 。
