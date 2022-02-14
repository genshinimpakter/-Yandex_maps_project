import os
import sys

import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

import geocoder


class MapShower(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_file = "map.png"
        uic.loadUi('app_des.ui', self)


        self.mode = 'map'
        self.map_mode.setEnabled(False)

        self.lat, self.lon = 0, 0

        self.lon_save = ''
        self.lat_save = ''
        self.span_save = ''

        self.clear_mode = False

        self.show_map.clicked.connect(self.run)
        self.map_mode.clicked.connect(self.change_map_mode)
        self.sat_mode.clicked.connect(self.change_map_mode)
        self.skl_mode.clicked.connect(self.change_map_mode)
        self.map_delete.clicked.connect(self.delete_map)

    def run(self):
        self.latitude_input.setEnabled(False)
        self.longtitude_input.setEnabled(False)
        self.object_address.setEnabled(False)
        self.show_map.setEnabled(False)
        self.show_map_func()

    def show_map_func(self):
        flag_address = False
        if self.object_address.text():
            self.lat, self.lon = list(map(float, self.object_address.text().replace(' ', '').split(',')))
            flag_address = True
        elif self.latitude_input.text() and self.longtitude_input.text():
            self.lat, self.lon = float(self.latitude_input.text().strip()), float(self.longtitude_input.text().strip())
        else:
            return

        # Объявляем переменные, чтобы программа не рухнула
        ll, span = geocoder.get_ll_span(f'{self.lon} {self.lat}')
        # Формируем параметры
        params = {'ll': ll, 'spn': span, 'l': self.mode}
        if flag_address:
            # Добавляем метку
            params["pt"] = "{0},pm2dgl".format(ll)
        if self.clear_mode:
            params['ll'] = f'{self.lon_save},{self.lat_save}'
            params['spn'] = self.span_save

        self.map_response_collect(params)

        map_pic = QPixmap(self.map_file)
        self.map.setPixmap(map_pic)

        os.remove(self.map_file)

    def map_response_collect(self, params):
        map_api_server = 'http://static-maps.yandex.ru/1.x/'
        response = requests.get(map_api_server, params)

        # Получаем ответ, закидываем его в картинку
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def change_map_mode(self):
        # Узнаём, что написано на кнопке, отправившей сигнал
        name_of_mode = self.sender().text()
        if name_of_mode == 'Схема':
            self.mode = 'map'
            self.map_mode.setEnabled(False)
            self.skl_mode.setEnabled(True)
            self.sat_mode.setEnabled(True)
            self.show_map_func()
        if name_of_mode == 'Спутник':
            self.mode = 'sat'
            self.sat_mode.setEnabled(False)
            self.map_mode.setEnabled(True)
            self.skl_mode.setEnabled(True)
            self.show_map_func()
        if name_of_mode == 'Гибрид':
            self.mode = 'skl'
            self.skl_mode.setEnabled(False)
            self.map_mode.setEnabled(True)
            self.sat_mode.setEnabled(True)
            self.show_map_func()

    def delete_map(self):
        self.latitude_input.setEnabled(True)
        self.longtitude_input.setEnabled(True)
        self.object_address.setEnabled(True)
        self.show_map.setEnabled(True)

        self.map.clear()
        self.object_address.clear()
        self.latitude_input.clear()
        self.longtitude_input.clear()
        self.show_map_func()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown]:
            if event.key() == Qt.Key_Left:
                self.lon -= 0.0002
            if event.key() == Qt.Key_Right:
                self.lon += 0.0002
            if event.key() == Qt.Key_Up:
                self.lat += 0.0002
            if event.key() == Qt.Key_Down:
                self.lat -= 0.0002
            if event.key() == Qt.Key_PageUp:
                geocoder.span = \
                    f"{float(geocoder.span.split(',')[0]) / 2},{float(geocoder.span.split(',')[1]) / 2}"
            if event.key() == Qt.Key_PageDown:
                geocoder.span = \
                    f"{float(geocoder.span.split(',')[0]) * 2},{float(geocoder.span.split(',')[1]) * 2}"
            self.show_map_func()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapShower()
    ex.show()
    sys.exit(app.exec_())
