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

    def find_card(self) -> None:
        """
            поиск номера карты с помощью многопроцессорной обработки данных и вывод номера карты на экран
        :return: None
        """
        start_time = time.time()
        dict = self.enum_card_number()
        card_number = dict['card_number']
        if card_number:
            self.info_window = InfoWindow(self, card_number, "ВТБ", "Кредитная карта", "Mastercard",
                                          time.time() - start_time, dict['pools'])
            self.info_window.show()
        else:
            print('Карта не найдена!')

    def enum_card_number(self) -> dict:
        """
            перебор номера карты с помощью многопроцессорной обработки данных и возврат номера карты
        :return: dict
        """
        if self.type == 1:
            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as p:
                for result in p.map(self.check_card_number, tqdm(range(0, 1000000), ncols=120)):
                    if result:
                        p.terminate()
                        return {'card_number': result, 'pools': p._processes}
            return {'card_number': None, 'pools': p._processes}
        else:
            self.pools += 1
            with multiprocessing.Pool(processes=self.pools) as p:
                for result in p.map(self.check_card_number, tqdm(range(0, 1000000), ncols=120)):
                    if result:
                        p.terminate()
                        return {'card_number': result, 'pools': p._processes}
            return {'card_number': None, 'pools': p._processes}

    @staticmethod
    def check_card_number(card_number_) -> str:
        """
            проверка номера карты на соответствие хешу и бину карты
        :param card_number_:
        :return: str
        """
        for card_bin in (
        519998, 529025, 516451, 522327, 522329, 523760, 527652, 528528, 529158, 529460, 529856, 530176, 530429, 531452, \
        531456, 531855, 531866, 531963, 532465, 534133, 534135, 534299, 510144, 518591, 518640, 540989, 526589, 528154):
            card_number = f'{card_bin}{card_number_:06d}{"0758"}'
            if hashlib.sha1(card_number.encode()).hexdigest() == "754a917a9c82f5247412006a5abe1c0eb76e1007":
                return card_number
        return None


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