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

        self.lon_save = ''
        self.lat_save = ''
        self.span_save = ''

        self.clear_mode = False

        self.show_map.clicked.connect(self.show_map_func)
        self.map_mode.clicked.connect(self.change_map_mode)
        self.sat_mode.clicked.connect(self.change_map_mode)
        self.skl_mode.clicked.connect(self.change_map_mode)
        self.map_delete.clicked.connect(self.delete_map)

    def collect_coords_from_user(self):
        # Узнаём у пользователя координаты объекта
        lon = self.longtitude_input.text()
        lat = self.latitude_input.text()
        flag_coords = False
        if lon and lat:
            flag_coords = True
        return lon, lat, flag_coords

    def collect_address_from_user(self):
        # Узнаём у пользователя адрес объекта
        address = self.object_address.text()
        flag_address = True if address else False
        return address, flag_address

    def show_map_func(self):
        lon, lat, flag_coords = self.collect_coords_from_user()
        address, flag_address = self.collect_address_from_user()
        flag_right_inp = True

        # Объявляем переменные, чтобы программа не рухнула
        ll = ''
        span = ''

        # Проверяем заполненность строк, нам не нужно, чтобы сразу
        # были заполненны и координаты и адрес
        if flag_coords and not flag_address:
            ll, span = geocoder.get_ll_span(f'{lon} {lat}')
            self.clear_mode = False
        if flag_address and not flag_coords:
            ll, span = geocoder.get_ll_span(f'{address}')
            self.lon_save = ll.split(',')[0]
            self.lat_save = ll.split(',')[1]
            self.span_save = span
            self.clear_mode = False
        if not flag_coords and not flag_address:
            flag_right_inp = False

        if flag_right_inp or self.clear_mode:
            # Формируем параметры
            params = {'ll': ll, 'spn': span, 'l': self.mode}
            if flag_address and not self.clear_mode:
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
        self.object_address.clear()
        self.clear_mode = True
        self.show_map_func()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.longtitude_input.setText(
                f'{float(self.longtitude_input.text()) - 0.01}')
        if event.key() == Qt.Key_Right:
            self.longtitude_input.setText(
                f'{float(self.longtitude_input.text()) + 0.01}')
        if event.key() == Qt.Key_Up:
            self.latitude_input.setText(
                f'{float(self.latitude_input.text()) + 0.01}')
        if event.key() == Qt.Key_Down:
            self.latitude_input.setText(
                f'{float(self.latitude_input.text()) - 0.01}')
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
