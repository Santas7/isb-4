import time
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets
import card
import logging


logger = logging.getLogger()
logger.setLevel('INFO')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кредитная карта")
        self.setFixedSize(QSize(550, 400))
        self.label_title = QLabel(self)
        self.label_title.setText("Кредитная карта")
        self.label_title.move(50, 50)
        self.label_title.setStyleSheet("font-size: 30px;")
        self.label_title.adjustSize()
        self.card = card.Card()
        self.card_number = None

        """self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 92, 450, 20)
        self.progress.setMaximum(100)
        self.progress.setMinimum(0)
        self.progress.setValue(0)
        self.progress.show()"""

        self.btn_find_card = self.add_button("💳Подбор номера карты", 450, 50, 50, 120)
        self.btn_graph = self.add_button("📊График статистики (поиска коллизий)", 450, 50, 50, 180)
        self.btn_luna = self.add_button("✅Проверка номера карты по алгоритму Луна", 450, 50, 50, 240)
        self.btn_exit = self.add_button("📛Выход", 450, 50, 50, 300)
        self.btn_find_card.clicked.connect(self.find_card)
        self.btn_graph.clicked.connect(self.set_pools_and_go_to_graph)
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
        start_time = time.perf_counter()
        dict = self.card.enum_card_number()
        end_time = time.perf_counter()
        delta = end_time - start_time
        self.card_number = dict['card_number']
        if self.card_number:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Информационное окно")
            dlg.setText(f"Результат поиска номера карты: \nНомер карты: {self.card_number}\nБанк: ВТБ\nТип карты: Кредитная\nПлатежная система: VISA/MasterCard\nВремя поиска: {delta}s \nКоличество процессоров: {dict['pools']}\n")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Информационное окно")
            dlg.setText("Номер карты не найден!")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")

    def luna(self) -> None:
        """
            проверка номера карты по алгоритму Луна
        :return: None
        """
        if self.card.luna(self.card_number):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Информационное окно")
            dlg.setText("Номер карты прошел проверку по алгоритму Луна")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Информационное окно")
            dlg.setText("Номер карты не прошел проверку по алгоритму Луна")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")

    def set_pools_and_go_to_graph(self):
        """
            установка количества процессов и переход к графику
        :return: None
        """
        input_window = InputWindow(self)
        input_window.show()

    def graph(self, cores: int) -> None:
        """
            построение графика статистики поиска номера карты
        :return: None
        """
        d = {
            'pools': [],
            'time': []
        }
        for i in range(cores):
            start_time = time.perf_counter()
            self.card.cores = i + 1
            dict = self.card.enum_card_number()
            end_time = time.perf_counter()
            delta = end_time - start_time
            card_number = dict['card_number']
            if card_number:
                d['pools'].append(i + 1)
                d['time'].append(float(delta))
        fig = plt.figure(figsize=(30, 5))
        plt.bar(d['pools'], d['time'], color='gold', width=0.05)
        plt.xlabel('Количество процессов')
        plt.ylabel('Время поиска')
        plt.title('График статистики (поиска коллизий)')
        plt.show()

    def exit(self) -> None:
        """
            закрытие программы
        :return: None
        """
        self.close()


class InputWindow(QtWidgets.QDialog):
    """
        класс окна ввода количества процессов
    """
    def __init__(self, parent=None):
        super(InputWindow, self).__init__(parent)
        self.setFixedSize(QSize(400, 300))
        self.setWindowTitle("Ввод кол-ва процессов")
        self.label = QLabel(self)
        self.label.setText("Введите количество процессов:")
        self.label.move(50, 50)
        self.label.adjustSize()
        self.textbox = QLineEdit(self)
        self.textbox.move(50, 100)
        self.textbox.resize(280, 40)
        self.button = QPushButton('Ввод', self)
        self.button.move(50, 200)
        self.button.clicked.connect(self.on_click)
        self.show()

    def on_click(self) -> None:
        """
            обработка нажатия кнопки
        :return: None
        """
        self.parent().card.set_cores(int(self.textbox.text()))
        self.parent().graph(int(self.textbox.text()))
        self.close()

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
        
        QProgressBar {
            border: 1px solid #575757;
            border-radius: 5px;
            background-color: #fff;
            color: #575757;
            text-align: center;
        }
        ''')
    app.exec()