import multiprocessing
import hashlib
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кредитная карта")
        self.setFixedSize(QSize(550, 400))

        # заголовок программы
        self.label_title = QLabel(self)
        self.label_title.setText("Кредитная карта")
        self.label_title.move(50, 50)
        self.label_title.setStyleSheet("font-size: 30px;")
        self.label_title.adjustSize()
        self.pools = 0
        self.type = 1

        # кнопки
        self.btn_find_card = self.add_button("💳Подбор номера карты", 450, 50, 50, 120)
        self.btn_graph = self.add_button("📊График статистики (поиска коллизий)", 450, 50, 50, 180)
        self.btn_luna = self.add_button("✅Проверка номера карты по алгоритму Луна", 450, 50, 50, 240)
        self.btn_exit = self.add_button("📛Выход", 450, 50, 50, 300)

        # события кнопок
        self.btn_find_card.clicked.connect(self.find_card)
        self.btn_graph.clicked.connect(self.graph)
        self.btn_luna.clicked.connect(self.luna)
        self.btn_exit.clicked.connect(self.close)

        self.show()

    def add_button(self, name: str, size_x: int, size_y: int, pos_x: int, pos_y: int) -> QPushButton:
        """
            добавление кнопки на форму с заданными параметрами и возврат кнопки
            :name: - название кнопки
            :size_x: - размер по x
            :size_y: - размер по y
            :pos_x: - положение по x
            :pos_y: - положение по y
        """
        button = QPushButton(name, self)
        button.setFixedSize(QSize(size_x, size_y))
        button.move(pos_x, pos_y)
        return button


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.setStyle('Fusion')
    app.setStyleSheet('''
        QMainWindow {
            background-color: #06db4d;
        }

        QPushButton {
            background-color: #575757;
            color: #fff;
            border: 1px solid #575757;
            border-radius: 15px;
            padding: 5px 10px;
        }

        QPushButton:hover {
            background-color: #fff;
            color: #575757;   
        }
        ''')

    app.exec()