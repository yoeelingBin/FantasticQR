# FantasticQR
 应用软件设计个人小作业，生成好看的二维码

## 1. Introduction
本项目使用Python+Pyqt，实现个性化二维码的生成
可以生成普通二维码、带图片的艺术二维码（彩色and黑白）、动态二维码。

## 2. Usage
![image](https://user-images.githubusercontent.com/57822313/161936010-d0dabcff-3fc2-4210-97f5-aa38e7fc2771.png)

左侧为选择参数界面，可以进行参数选择
- 二维码的版本（即二维码的大小），范围为1-40
- 纠错级别（二维码纠正错误能力），范围为L M Q H，依次升高
- 背景颜色（控制二维码图片是黑白还是彩色的）
- 对比度（控制图像的对比度），大于1.0
- 亮度（调节图像的亮度），大于1.0

![image](https://user-images.githubusercontent.com/57822313/161938318-2b7f0a9b-fa18-446d-93d0-7b0b51faf8d3.png)

在文本输入框中输入文字或者网址（可用字符：数字、英文、标点符号），之后点击生成二维码即可在最右侧预览生成的个性化二维码

点击清除即可清空内容，保存就可按照指定的路径保存生成的二维码，方便将来的使用。

## 3. Tips
- 为了更好的显示效果，请最好使用正方形的图片
- 当图片尺寸较大时，最好选择更高的版本

## 4. Display
一些示例图片：

![1](https://user-images.githubusercontent.com/57822313/162349011-099fdfda-9898-493c-bb8a-c8f6b2d8a808.jpg)
![qingming](https://user-images.githubusercontent.com/57822313/162349070-4e29dae8-8358-46ef-9b02-d7d22f521436.jpg)
![my github](https://user-images.githubusercontent.com/57822313/162349024-becef375-c8f8-4988-9a3e-8c3d89737146.gif)
![test2](https://user-images.githubusercontent.com/57822313/162349043-c5e5c8f3-61c2-44a7-a864-600aa8a8dd22.jpg)

