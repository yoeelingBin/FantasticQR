from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
import os
import imageio
from qrlib import qrmodule
from PIL import Image, ImageSequence
from qrlib.constant import alig_location
from PIL import ImageEnhance, ImageFilter
from utils import parameter
import cv2

ui: QWidget
scene: QGraphicsScene
showname: str


# 初始化
def modify(_ui: QWidget):
    global ui
    global scene
    global showname
    showname = ''
    ui = _ui
    scene = QGraphicsScene(ui)
    set_button()
    set_box()


# 设置按钮
def set_button():
    ui.genqr_button.clicked.connect(gen_qr)
    ui.clearqr_button.clicked.connect(clear_qr)
    ui.saveqr_button.clicked.connect(save_qr)
    ui.buttonGroup.buttonClicked.connect(handleButtonClicked)
    ui.radioButton.setChecked(True)


# 设置数字输入框
def set_box():
    ui.spinBox.setValue(1)
    ui.doubleSpinBox.setValue(1.00)
    ui.doubleSpinBox_2.setValue(1.00)


# 处理单选按钮响应
def handleButtonClicked():
    text = ui.buttonGroup.checkedButton().text()
    if text == "黑":
        return True
    else:
        return False


def combine(ver, qr_name, bg_name, colorized, contrast, brightness, save_dir, save_name=None):
    qr = Image.open(qr_name)
    qr = qr.convert('RGBA') if colorized else qr

    bg0 = Image.open(bg_name).convert('RGBA')
    bg0 = ImageEnhance.Contrast(bg0).enhance(contrast)
    bg0 = ImageEnhance.Brightness(bg0).enhance(brightness)

    if bg0.size[0] < bg0.size[1]:
        bg0 = bg0.resize((qr.size[0] - 24, (qr.size[0] - 24) * int(bg0.size[1] / bg0.size[0])))
    else:
        bg0 = bg0.resize(((qr.size[1] - 24) * int(bg0.size[0] / bg0.size[1]), qr.size[1] - 24))

    bg = bg0 if colorized else bg0.convert('1')

    aligs = []
    if ver > 1:
        aloc = alig_location[ver - 2]
        for a in range(len(aloc)):
            for b in range(len(aloc)):
                if not ((a == b == 0) or (a == len(aloc) - 1 and b == 0) or (a == 0 and b == len(aloc) - 1)):
                    for i in range(3 * (aloc[a] - 2), 3 * (aloc[a] + 3)):
                        for j in range(3 * (aloc[b] - 2), 3 * (aloc[b] + 3)):
                            aligs.append((i, j))

    for i in range(qr.size[0] - 24):
        for j in range(qr.size[1] - 24):
            if not ((i in (18, 19, 20)) or (j in (18, 19, 20)) or (i < 24 and j < 24) or (
                    i < 24 and j > qr.size[1] - 49) or (i > qr.size[0] - 49 and j < 24) or ((i, j) in aligs) or (
                            i % 3 == 1 and j % 3 == 1) or (bg0.getpixel((i, j))[3] == 0)):
                qr.putpixel((i + 12, j + 12), bg.getpixel((i, j)))

    qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(bg_name))[0] + '_qrcode.png') if not save_name \
        else os.path.join(save_dir, save_name)
    qr.resize((qr.size[0] * 3, qr.size[1] * 3)).save(qr_name)
    return qr_name


# 运行主程序
def run(words, version=1, level='H', picture=None, colorized=False, contrast=1.0, brightness=1.0, save_name=None,
        save_dir=os.getcwd()):
    """
    # Positional parameters
    :param words: str
    # Optional parameters
    :param version: int, from 1 to 40
    :param level:  str, just one of ('L','M','Q','H')
    :param picture: str, a filename of an image
    :param colorized: bool
    :param contrast: float
    :param brightness: float
    :param save_name: str, the output filename like 'example.png'
    :param save_dir: str, the output directory
    :return:
    """
    supported_chars = r"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ··,.:;+-*/\~!@#$%^&`'=<>[](" \
                      r")?_{}| "

    # check every parameter
    if not isinstance(words, str) or any(i not in supported_chars for i in words):
        raise ValueError('Wrong words! Make sure the characters are supported!')
    if not isinstance(version, int) or version not in range(1, 41):
        raise ValueError('Wrong version! Please choose a int-type value from 1 to 40!')
    if not isinstance(level, str) or len(level) > 1 or level not in 'LMQH':
        raise ValueError("Wrong level! Please choose a str-type level from {'L','M','Q','H'}!")
    if picture:
        if not isinstance(picture, str) or not os.path.isfile(picture) or picture[-4:] not in (
                '.jpg', '.png', '.bmp', '.gif'):
            raise ValueError(
                "Wrong picture! Input a filename that exists and be tailed with one of {'.jpg', '.png', '.bmp', "
                "'.gif'}!")
        if picture[-4:] == '.gif' and save_name and save_name[-4:] != '.gif':
            raise ValueError(
                'Wrong save_name! If the picuter is .gif format, the output filename should be .gif format, too!')
        if not isinstance(colorized, bool):
            raise ValueError('Wrong colorized! Input a bool-type value!')
        if not isinstance(contrast, float):
            raise ValueError('Wrong contrast! Input a float-type value!')
        if not isinstance(brightness, float):
            raise ValueError('Wrong brightness! Input a float-type value!')
    if save_name and (not isinstance(save_name, str) or save_name[-4:] not in ('.jpg', '.png', '.bmp', '.gif')):
        raise ValueError("Wrong save_name! Input a filename tailed with one of {'.jpg', '.png', '.bmp', '.gif'}!")
    if not os.path.isdir(save_dir):
        raise ValueError('Wrong save_dir! Input a existing-directory!')

    tempdir = os.path.join(os.path.expanduser('~'), '.myqr')

    try:
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

        ver, qr_name = qrmodule.get_qrcode(version, level, words, tempdir)

        if picture and picture[-4:] == '.gif':
            im = Image.open(picture)
            duration = im.info.get('duration', 0)
            im.save(os.path.join(tempdir, '0.png'))
            while True:
                try:
                    seq = im.tell()
                    im.seek(seq + 1)
                    im.save(os.path.join(tempdir, '%s.png' % (seq + 1)))
                except EOFError:
                    break

            imsname = []
            for s in range(seq + 1):
                bg_name = os.path.join(tempdir, '%s.png' % s)
                imsname.append(combine(ver, qr_name, bg_name, colorized, contrast, brightness, tempdir))

            ims = [imageio.imread(pic) for pic in imsname]
            qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(picture))[
                0] + '_qrcode.gif') if not save_name else os.path.join(save_dir, save_name)
            imageio.mimwrite(qr_name, ims, '.gif', **{'duration': duration / 1000})
        elif picture:
            qr_name = combine(ver, qr_name, picture, colorized, contrast, brightness, save_dir, save_name)
        elif qr_name:
            qr = Image.open(qr_name)
            qr_name = os.path.join(save_dir, os.path.basename(qr_name)) if not save_name else os.path.join(save_dir,
                                                                                                           save_name)
            qr.resize((qr.size[0] * 3, qr.size[1] * 3)).save(qr_name)

        return ver, level, qr_name

    except:
        raise
    finally:
        import shutil
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)


# 生成二维码
def gen_qr():
    text: QTextBrowser = ui.info_text
    param = get_parameter()
    if param.picture:
        if param.picture[-4:] == '.gif':
            gif_text = f'Generating qr gif, please waiting for some seconds...\n'
            text.setText(gif_text)
    version, level, qr_name = run(param.words, param.version, param.level, param.picture, param.colorized,
                                  param.contrast, param.brightness, param.name, param.save_dir)

    show_text = f'Succeed! \n Check out your {str(version)}-{str(level)} QR-code {qr_name}'
    text.append(show_text)
    show_img()


# 清除二维码
def clear_qr():
    reply = QMessageBox.question(ui, '温馨提示', '该操作会清除所有内容!', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        ui.textEdit.clear()
        ui.info_text.clear()
        scene.clear()


# 保存二维码
def save_qr():
    imagepath, _ = QFileDialog.getSaveFileName(
        ui,  # 父窗口对象
        "保存二维码",  # 标题
        "./img/",  # 起始目录
        "jpg, png, bmp, gif类型 (*.jpg *.png *.bmp *.gif);;All Files (*)"
    )
    if imagepath:
        if imagepath[-4:] == '.jpg':
            img = cv2.imread(showname)
            cv2.imwrite(imagepath, img)
        elif imagepath[-4:] == '.gif':
            im = Image.open(showname)
            duration = im.info.get('duration', 0)
            tmpdir = "E:\Codefield\Python\FantasticQR\tmp"
            im.save(os.path.join(tmpdir, 'frame0.png'))
            while True:
                try:
                    seq = im.tell()
                    im.seek(seq + 1)
                    im.save(os.path.join(tmpdir, 'frame%s.png' % (seq + 1)))
                except EOFError:
                    break
            imgname = []
            for s in range(seq + 1):
                imgname.append(showname)
            ims = [imageio.imread(pic) for pic in imgname]
            imageio.mimwrite(imagepath, ims, '.gif', **{'duration': duration / 1000})
        else:
            img = Image.open(showname)
            img.save(imagepath)
        QMessageBox.information(ui, '提示', '保存成功', QMessageBox.Yes)
    else:
        QMessageBox.warning(ui, '警告', '请选择文件路径', QMessageBox.Yes)


# 获取图片
def get_picture():
    global showname
    imagepath, _ = QFileDialog.getOpenFileName(
        ui,  # 父窗口对象
        "选择背景图片",  # 标题
        "./bg/",  # 起始目录
        "jpg, png, bmp, gif类型 (*.jpg *.png *.bmp *.gif);;All Files (*)"
    )
    try:
        if imagepath:
            QMessageBox.information(ui, '提示', '图片选取成功', QMessageBox.Yes)
            if imagepath[-4:] == '.jpg':
                showname = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(imagepath))[0] + '_qrcode.png')
            elif imagepath[-4:] == '.gif':
                showname = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(imagepath))[0] + '_qrcode.gif')
            return imagepath
        else:
            showname = os.path.join(os.getcwd(), 'qrcode.png')
            return None
    except Exception:
        QMessageBox.warning(ui, '警告', '图片读取异常', QMessageBox.Yes)


# 获取参数传递给生成函数
def get_parameter():
    words = ui.textEdit.toPlainText()
    version = ui.spinBox.value()
    level = ui.comboBox.currentText()
    picture = get_picture()
    colorized = handleButtonClicked()
    contrast = ui.doubleSpinBox.value()
    brightness = ui.doubleSpinBox_2.value()
    name = None
    save_dir = os.getcwd()
    return parameter.Parameter(words, version, level, picture, colorized, contrast, brightness, name, save_dir)


# 展示二维码预览
def show_img():
    pix = QPixmap(showname)
    item = QGraphicsPixmapItem(pix)
    scene.addItem(item)
    ui.graphicsView.setScene(scene)
