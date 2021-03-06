import os

import cv2
import imageio
import shutil
from PIL import Image, ImageSequence
from PIL import ImageEnhance
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import *

from qrlib import qrmodule
from qrlib.constant import alig_location
from utils import parameter

ui: QWidget
showname: str


class WorkThread(QThread):
    trigger = pyqtSignal(str)

    def __init__(self, words, version, level, picture, colorized, contrast, brightness, save_name, save_dir):
        self.qr_name = ''
        self.words = words
        self.version = version
        self.level = level
        self.picture = picture
        self.colorized = colorized
        self.contrast = contrast
        self.brightness = brightness
        self.name = save_name
        self.save_dir = save_dir
        super(WorkThread, self).__init__()

    def __del__(self):
        self.quit()
        self.wait()

    def run(self):
        self.version, self.level, self.qr_name = run(self.words, self.version, self.level, self.picture, self.colorized,
                                                     self.contrast, self.brightness, self.name, self.save_dir)


# 初始化
def modify(_ui: QWidget):
    global ui
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
    if text == "彩色":
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
    finally:
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)


# 检查输入参数
def check(words, version, picture, save_name, save_dir):
    supported_chars = r"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ··,.:;+-*/\~!@#$%^&`'=<>[](" \
                      r")?_{}| "

    # check every parameter
    if not isinstance(words, str) or any(i not in supported_chars for i in words):
        QMessageBox.critical(ui, '错误', '错误字符！', QMessageBox.Yes)
        raise ValueError('Wrong words! Make sure the characters are supported!')
    if not isinstance(version, int) or version not in range(1, 41):
        QMessageBox.critical(ui, '错误', '错误版本！请输入正确的版本号！（1-40）', QMessageBox.Yes)
        raise ValueError('Wrong version! Please choose a int-type value from 1 to 40!')
    if picture:
        if not isinstance(picture, str) or not os.path.isfile(picture) or picture[-4:] not in (
                '.jpg', '.png', '.bmp', '.gif'):
            QMessageBox.critical(ui, '错误', '错误图片！请输入正确的图片格式！', QMessageBox.Yes)
            raise ValueError(
                "Wrong picture! Input a filename that exists and be tailed with one of {'.jpg', '.png', '.bmp', "
                "'.gif'}!")
        if picture[-4:] == '.gif' and save_name and save_name[-4:] != '.gif':
            QMessageBox.critical(ui, '错误', '错误保存路径！后缀应为.gif！', QMessageBox.Yes)
            raise ValueError(
                'Wrong save_name! If the picture is .gif format, the output filename should be .gif format, too!')
    if save_name and (not isinstance(save_name, str) or save_name[-4:] not in ('.jpg', '.png', '.bmp', '.gif')):
        QMessageBox.critical(ui, '错误', '错误保存名字！请选择为图片格式！', QMessageBox.Yes)
        raise ValueError("Wrong save_name! Input a filename tailed with one of {'.jpg', '.png', '.bmp', '.gif'}!")
    if not os.path.isdir(save_dir):
        QMessageBox.critical(ui, '错误', '错误保存目录！请选择已存在的目录！', QMessageBox.Yes)
        raise ValueError('Wrong save_dir! Input a existing-directory!')


def del_files(path_file):
    ls = os.listdir(path_file)
    for i in ls:
        f_path = os.path.join(path_file, i)
        if os.path.isdir(f_path):
            del_files(f_path)
        else:
            os.remove(f_path)


# 生成二维码
def gen_qr():
    text: QTextBrowser = ui.info_text
    param = get_parameter()
    try:
        check(param.words, param.version, param.picture, param.name, param.save_dir)
    except ValueError:
        ui.textEdit.clear()
        ui.info_text.clear()
        ui.movie_screen.clear()
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
        ui.movie_screen.clear()


# 保存二维码
def save_qr():
    imagepath, _ = QFileDialog.getSaveFileName(
        ui,  # 父窗口对象
        "保存二维码",  # 标题
        "./img/",  # 起始目录
        "jpg, png, bmp类型 (*.jpg *.png *.bmp);;gif (*.gif);;All Files (*)"
    )
    if imagepath:
        if imagepath[-4:] == '.jpg':
            img = cv2.imread(showname)
            cv2.imwrite(imagepath, img)
        elif imagepath[-4:] == '.gif':
            im = Image.open(showname)
            iter = ImageSequence.Iterator(im)
            index = 1
            for frame in iter:
                frame.save("./tmp/frame%d.png" % index)
                index += 1
            imgs = [frame.copy() for frame in ImageSequence.Iterator(im)]
            imgs[0].save(imagepath, save_all=True, append_images=imgs[1:])
            del_files("./tmp")
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
    if showname[-4:] == '.png':
        pix = QPixmap(showname)
        ui.movie_screen.setPixmap(pix)
        ui.movie_screen.setScaledContents(True)
    elif showname[-4:] == '.gif':
        movie = QMovie(showname)
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(100)
        ui.movie_screen.setMovie(movie)
        movie.start()
