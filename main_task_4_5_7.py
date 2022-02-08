import os
import sys

import requests
from PyQt5 import uic  # Импортируем uic
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

        self.show_map.clicked.connect(self.show_map_func)
        self.map_mode.clicked.connect(self.change_map_mode)
        self.sat_mode.clicked.connect(self.change_map_mode)
        self.skl_mode.clicked.connect(self.change_map_mode)
        self.map_delete.clicked.connect(self.delete_map)

    def show_map_func(self):
        # Узнаём у пользователя координаты объекта
        lon = self.longtitude_input.text()
        lat = self.latitude_input.text()
        address = self.object_address.text()
        flag_right_inp = True
        flag_address = False # Заполнено ли поле адреса

        # Проверяем заполненность строк, нам не нужно, чтобы сразу
        # были заполненны и координаты и адрес
        if lon and lat and not address:
            ll, span = geocoder.get_ll_span(f'{lon} {lat}')
        if address and not lon and not lat:
            flag_address = True
            ll, span = geocoder.get_ll_span(f'{address}')
        else:
            flag_right_inp = False

        if flag_right_inp:
            # Формируем и отсылаем запрос
            params = {'ll': ll, 'spn': span, 'l': self.mode}
            if flag_address: # Добавляем метку
                params["pt"] = "{0},pm2dgl".format(ll)
            map_api_server = 'http://static-maps.yandex.ru/1.x/'
            response = requests.get(map_api_server, params)

            # Получаем ответ, закидываем его в картинку, отображаем её
            with open(self.map_file, "wb") as file:
                file.write(response.content)
            map_pic = QPixmap(self.map_file)
            self.map.setPixmap(map_pic)

            os.remove(self.map_file)

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
        self.map.clear()
        self.object_address.clear()
        self.longtitude_input.clear()
        self.latitude_input.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.longtitude_input.setText(
                f'{float(self.longtitude_input.text()) - 0.001}')
        elif event.key() == Qt.Key_Right:
            self.longtitude_input.setText(
                f'{float(self.longtitude_input.text()) + 0.001}')
        elif event.key() == Qt.Key_Up:
            self.latitude_input.setText(
                f'{float(self.latitude_input.text()) + 0.001}')
        elif event.key() == Qt.Key_Down:
            self.latitude_input.setText(
                f'{float(self.latitude_input.text()) - 0.001}')
        self.show_map_func()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapShower()
    ex.show()
    sys.exit(app.exec_())
