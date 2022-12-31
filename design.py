# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data\untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import glob

from PyQt5.QtCore import Qt, QRect
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox
from qtpy import QtGui
from decoder import lazyDecoder
import json

from canvas import Canvas
from centralLabel import Label
from model import build_model


class Ui_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.images_list = []

        self.setObjectName("MainWindow")
        self.resize(1920, 1080)

        self.central_widget = centralWidget()
        self.central_widget.setObjectName("centralwidget")

        self.setCentralWidget(self.central_widget)


class centralWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.dict = None
        self.elements_list = QListWidget()
        self.label_list_widget = QListWidget()
        self.ranks = None
        self.create_list()

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(10, 0, 121, 30))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText('push')

        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 40, 121, 30))
        self.pushButton_2.setObjectName("pushButton2")

        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(10, 80, 121, 30))
        self.pushButton_3.setObjectName("pushButton3")

        self.pushButton_4 = QtWidgets.QPushButton(self)
        self.pushButton_4.setGeometry(QtCore.QRect(10, 120, 101, 30))
        self.pushButton_4.setObjectName("pushButton4")

        self.info_line = QLabel('Hellow!', parent=self)
        self.info_line.setGeometry(QtCore.QRect(0, 933, 1920, 30))
        self.info_line.setAlignment(QtCore.Qt.AlignCenter)

        self.pushButton.clicked.connect(self.on_clicked_2)
        self.pushButton_2.clicked.connect(self.load_project)
        # self.pushButton_3.clicked.connect(self.on_clicked_3)
        self.pushButton_4.clicked.connect(self.rewrite)

        self.elements_list.clicked.connect(self.elements_list_clicked)
        self.label_list_widget.clicked.connect(self.label_list_clicked)

    def load_project(self):

        dirlist = QtWidgets.QFileDialog.getExistingDirectory(None, "Выбрать папку", ".")

        if dirlist:
            try:
                with open(dirlist + r'/Контрольные точки/Points', 'r') as ff:
                    self.dict = json.loads(ff.read(), strict=False)
            except Exception as ex:
                self.info_line.setText(f'Error {ex}')
                message = QMessageBox()
                message.setText('Файл Points не найден,\n найти вручную?')
                message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                answer = message.exec_()
                if answer == QMessageBox.Yes:
                    dirlist_points, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Выбрать папку",
                                                                              dirlist + '/Контрольные точки/')
                    if dirlist_points:
                        with open(dirlist_points, 'r') as ff:
                            self.dict = json.loads(ff.read(), strict=False)
                elif answer in (QMessageBox.No, QMessageBox.Close):
                    return

            if self.dict:
                self.elements_list.clear()
                for el in self.dict['Elements'].keys():
                    self.elements_list.addItem(QListWidgetItem(el))
                self.elements_list.setCurrentRow(0)

            self.label_list_widget.clear()
            for file in glob.glob(dirlist + r'\Виды\*'):
                self.label_list_widget.addItem(QListWidgetItem(file.split('\\')[-1]))
                self.create_label(file)
            self.label_list_widget.setCurrentRow(0)
            self.label_list_clicked()

            projects = glob.glob(dirlist + r'\*.prj')
            if len(projects) != 1:
                dirlist_project, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Выбрать проект", dirlist + "/")
                with open(dirlist_project, 'r') as ff:
                    f = ff.read()
                    indexes_dict = json.loads(f.replace('\\', '\\\\'), strict=False)
                    self.ranks = {name: item['Rank'] for name, item in indexes_dict['Items']['0']['Items'].items()}
            else:
                with open(projects[0], 'r') as ff:
                    f = ff.read()
                    indexes_dict = json.loads(f.replace('\\', '\\\\'), strict=False)
                    self.ranks = {name: item['Rank'] for name, item in indexes_dict['Items']['0']['Items'].items()}

            self.info_line.setText(f'Elements & images loaded from {dirlist}')
        else:
            self.info_line.setText('Project are not loaded')

    def next_item(self):
        self.elements_list.setCurrentRow(self.elements_list.currentRow() + 1)

    def elements_list_clicked(self):
        print(f'item clicked {self.elements_list.currentItem().text()}')

    def label_list_clicked(self):
        item = self.label_list_widget.currentItem().text()
        self.findChild(Label, item).show()
        for element in self.findChildren(Label):
            if element.objectName() != item:
                element.hide()
            else:
                element.show()

    def to_points_elements(self, points: list):
        element = self.elements_list.currentItem().text()
        self.dict['Elements'][element]['Views'][self.ranks[self.label_list_widget.currentItem().text()]] = \
            [{'L': int(min(points[0], points[2])) * 5,
              'T': int(min(points[1], points[3])) * 5,
              'R': int(max(points[0], points[2])) * 5,
              'B': int(max(points[1], points[3])) * 5,
              'Section': self.elements_list.currentItem().text()}]
        self.info_line.setText(f'Element position {self.elements_list.currentItem().text()} added into Points')

    def to_points_dots(self, dots: list):
        for num, dot in enumerate(dots):
            key = f'{self.elements_list.currentItem().text()}_{num + 1}'
            if key in self.dict['Dots']:
                self.dict['Dots'][key]['Views'][self.ranks[self.label_list_widget.currentItem().text()]] = \
                    {'L': int(dot[0] * 1.25),
                     'T': int(dot[1] * 1.25),
                     'R': int(dot[0] * 1.25 + 30),
                     'B': int(dot[1] * 1.25 + 30),
                     'Section': ''}
                self.info_line.setText(
                    f'Dot position {self.elements_list.currentItem().text()}_{num + 1} added into Points')
            else:
                self.info_line.setText(
                    f'Dot position {self.elements_list.currentItem().text()}_{num + 1} not added into Points')

    def rewrite(self):
        dirlist = QtWidgets.QFileDialog.getExistingDirectory(None, "Выбрать папку", ".")
        with open(dirlist + r'/Контрольные точки/Points', 'w') as ff:
            json.dump(self.dict, ff, indent=1)
        self.info_line.setText(f'File {dirlist}/Контрольные точки/Points rewrite')

    def create_list(self):
        list_area = QWidget(self)
        list_area.setObjectName('ListElements')
        list_area.setGeometry(QRect(1400, 100, 400, 800))
        list_area.setStyleSheet(
            '#ListElements {border: 3px solid black};')
        vbox = QVBoxLayout()
        vbox.addWidget(self.elements_list)
        vbox.addWidget(self.label_list_widget)
        list_area.setLayout(vbox)

    # def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
    #
    #     if event.key() == Qt.Key_Delete:
    #         print(self.cen_label.objects)
    #         self.cen_label.objects[self.cen_label.current_object].deleteLater()
    #         del (self.cen_label.objects[self.cen_label.current_object])

    def on_clicked_2(self):
        self.info_line.setText(f'button pressed')
        self.cen_label.hide()

    def create_label(self, path):
        image = Canvas(path, model=model)
        label = Label(image=image, parent=self)
        label.setObjectName(path.split('\\')[-1])
        label.setGeometry(140, 100, 1200, 800)
        label.setStyleSheet(
            "#{cen_label} /{{background-color: rgb(100,120,100);/}}".format(cen_label=path.split('\\')[-1])
        )
        return label


if __name__ == "__main__":
    import sys

    model = build_model()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.load_weights('data/U-net/weights.hdf5')

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())
