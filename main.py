import multiprocessing
import hashlib
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets


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