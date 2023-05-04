import functools
import multiprocessing
import time
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QMessageBox, QProgressBar, \
    QFileDialog
from PyQt6.QtCore import QSize, QThread, pyqtSignal
from PyQt6 import QtWidgets
import card
import logging


logger = logging.getLogger()
logger.setLevel('INFO')
file_handler = logging.FileHandler('log_file.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Worker(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(dict)

    def __init__(self, card, options):
        super().__init__()
        self.card = card
        self.options = options

    def run(self):
        """
            запуск многопоточного поиска номера карты
            check_card_number_with_options - частично примененная функция check_card_number с фиксированными options
            functools - библиотека для частичного применения функции
        :return:
        """
        result = {'card_number': None, 'pools': 0}
        check_card_number_with_options = functools.partial(self.card.check_card_number, options=self.options)
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as p:
            for status_value, card_result in enumerate(
                    p.imap_unordered(check_card_number_with_options, range(99999, 1000000))):
                if card_result:
                    self.update_prog_bar_finish()
                    p.terminate()
                    result = {'card_number': card_result, 'pools': p._processes}
                    break
                self.progress_signal.emit(status_value)
            else:
                self.progress_signal.emit(100)
        self.result_signal.emit(result)

    def update_prog_bar_finish(self):
        self.progress_signal.emit(100)


class GraphWorker(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(list)

    def __init__(self, card, cores, options):
        super().__init__()
        self.card = card
        self.cores = cores
        self.options = options

    def run(self):
        """
            запуск многопоточного поиска номера карты с разным количеством ядер
        :return:
        """
        d = {'pools': [], 'time': []}
        for i in range(self.cores):
            start_time = time.perf_counter()
            self.card.cores = i + 1
            check_card_number_with_options = functools.partial(self.card.check_card_number, options=self.options)
            with multiprocessing.Pool(processes=self.card.cores) as p:
                for status_value, card_result in enumerate(
                        p.imap_unordered(check_card_number_with_options, range(99999, 1000000))):
                    if card_result:
                        self.progress_signal.emit(100)
                        p.terminate()
                        result = {'card_number': card_result, 'pools': p._processes}
                    self.progress_signal.emit(status_value)
                else:
                    self.progress_signal.emit(100)
            self.result_signal.emit(result)
            end_time = time.perf_counter()
            delta = end_time - start_time
            d['pools'].append(i + 1)
            d['time'].append(float(delta))
        self.progress_signal.emit(100)
        self.result_signal.emit(d)


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
        while True:
            self.file_name = QFileDialog.getOpenFileName(self, 'Выбрать файл с характеристиками карты', '')[0]
            if self.file_name:
                try:
                    with open(self.file_name, 'r') as f:
                        self.options_card = eval(f.read())
                    logger.info(f'Файл {self.file_name} успешно загружен')
                    break
                except Exception as e:
                    logger.error(e)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 92, 450, 20)
        self.progress.setMaximum(100)
        self.progress.setMinimum(0)
        self.progress.setValue(0)
        self.progress.hide()
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

    def update_prog_bar(self, value) -> None:
        percentage = int((value / (1000000 - 99999)) * 100)
        self.progress.setValue(percentage)

    def prepare_prog_bar(self) -> None:
        """
            подготовка прогресс бара
        :return: None
        """
        self.progress.setValue(0)
        self.progress.show()

    def find_card(self) -> None:
        """
            Поиск номера карты
        :return:
        """
        self.prepare_prog_bar()
        self.worker = Worker(self.card, self.options_card)
        self.worker.progress_signal.connect(self.update_prog_bar)
        self.worker.result_signal.connect(self.show_result)
        self.worker.start()

    def show_result(self, result) -> None:
        card_number = result['card_number']
        pools = result['pools']
        if card_number:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Информационное окно")
            dlg.setText(f"Результат поиска номера карты: \nНомер карты: {card_number}\nБанк: ВТБ\nТип карты: Кредитная\nПлатежная система: VISA/MasterCard\nКоличество процессоров: {pools}\n")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")
            logger.info(f'Поиск номера карты завершен успешно! Номер карты: {card_number}')
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Информационное окно")
            dlg.setText("Номер карты не найден!")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")
            logger.info(f'Поиск номера карты завершен успешно! Карта не найдена!')
        self.worker.quit()
        self.worker.wait()

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
            logger.info(f'Номер карты прошел проверку по алгоритму Луна')
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Информационное окно")
            dlg.setText("Номер карты не прошел проверку по алгоритму Луна")
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Ok:
                print("OK!")
            logger.info(f'Номер карты не прошел проверку по алгоритму Луна')

    def set_pools_and_go_to_graph(self) -> None:
        """
            установка количества процессов и переход к графику
        :return: None
        """
        input_window = InputWindow(self)
        input_window.show()

    def graph(self, cores: int) -> None:
        """
            построение графика
        :param cores:
        :return:
        """
        self.prepare_prog_bar()
        self.graph_worker = GraphWorker(self.card, cores, self.options_card)
        self.graph_worker.progress_signal.connect(self.update_prog_bar)
        self.graph_worker.result_signal.connect(self.show_graph)
        self.graph_worker.start()

    def show_graph(self, data) -> None:
        """
            отображение графика
        :param data:
        :return: None
        """
        fig = plt.figure(figsize=(30, 5))
        plt.bar(data['pools'], data['time'], color='gold', width=0.05)
        plt.xlabel('Количество процессов')
        plt.ylabel('Время поиска')
        plt.title('График статистики (поиска коллизий)')
        plt.show()
        logger.info(f'Построение графика завершено успешно!')
        self.card.cores = multiprocessing.cpu_count()
        self.graph_worker.quit()
        self.graph_worker.wait()

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
        self.parent().card.cores = int(self.textbox.text())
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