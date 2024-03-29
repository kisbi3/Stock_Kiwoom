import sys                        # system specific parameters and functions : 파이썬 스크립트 관리
from PyQt5.QtWidgets import *     # GUI의 그래픽적 요소를 제어       하단의 terminal 선택, activate py37_32,  pip install pyqt5,   전부다 y
from PyQt5 import uic             # ui 파일을 가져오기위한 함수

###################################################
from Qthread_4 import Thread4      # Qthread_4 에 크롤링을 위한 스레드
###################################################

form_secondwindow = uic.loadUiType("NewsWindows.ui")[0]

class secondwindow(QMainWindow, QWidget, form_secondwindow):
    def __init__(self):
        super(secondwindow, self).__init__()
        self.initUi()
        self.show()

        self.check_exchange_rate()

        self.pushButton.clicked.connect(self.btn_second_to_main)

    def initUi(self):
        self.setupUi(self)

    def btn_second_to_main(self):
        self.close()  # 클릭시 종료됨.

    def check_exchange_rate(self):
        print("환율 가져오기")
        h4 = Thread4(self)
        h4.start()
