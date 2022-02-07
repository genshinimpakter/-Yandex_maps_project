import sys

import requests
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
import os
import geocoder


class MapShower(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_file = "map.png"
        uic.loadUi('app_des.ui', self)
        self.show_map.clicked.connect(self.show_map_func)

    def show_map_func(self):
        # Узнаём у пользователя координаты объекта
        lon = self.longtitude_input.text()
        lat = self.latitude_input.text()

        # Формируем и отсылаем запрос
        ll, span = geocoder.get_ll_span(f'{lon} {lat}')
        params = {'ll': ll, 'spn': span, 'l': 'map'}
        map_api_server = 'http://static-maps.yandex.ru/1.x/'
        response = requests.get(map_api_server, params)

        # Получаем ответ, закидываем его в картинку, отображаем её
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        map_pic = QPixmap(self.map_file)
        self.map.setPixmap(map_pic)

        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.longtitude_input.setText(f'{float(self.longtitude_input.text()) - 0.001}')
        elif event.key() == Qt.Key_Right:
            self.longtitude_input.setText(f'{float(self.longtitude_input.text()) + 0.001}')
        elif event.key() == Qt.Key_Up:
            self.latitude_input.setText(f'{float(self.latitude_input.text()) + 0.001}')
        elif event.key() == Qt.Key_Down:
            self.latitude_input.setText(f'{float(self.latitude_input.text()) - 0.001}')
        self.show_map_func()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapShower()
    ex.show()
    sys.exit(app.exec_())
