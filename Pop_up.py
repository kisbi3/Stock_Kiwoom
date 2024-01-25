import sys                        # system specific parameters and functions : 파이썬 스크립트 관리
from PyQt5.QtWidgets import *     # GUI의 그래픽적 요소를 제어       하단의 terminal 선택, activate py37_32,  pip install pyqt5,   전부다 y
from PyQt5 import uic             # ui 파일을 가져오기위한 함수
from PyQt5 import QtGui, QtWidgets
from kiwoom import Kiwoom          # 메타클레스 기반 싱글턴
from Qthread_5 import Thread5      # Qthread_4 에 크롤링을 위한 스레드

class myFirstWindow(QtWidgets.QWidget):
    def __init__(self):
        super(myFirstWindow, self).__init__()

        self.k = Kiwoom()
        self.check_ADR()


        self.resize(500, 50)    # 창 크기
        self.setWindowTitle('투자 가이드 라인')

        if self.k.kospi > 120:
            self.label1 = basicLabel(self, "매수하지 마세요. 제발(%s, %s)" % (self.k.kospi, self.k.kosdac))
            self.label1.setStyleSheet("Color : red")
            self.label1.setFont(QtGui.QFont("맑은고딕", 14, QtGui.QFont.Bold))

        elif self.k.kospi < 120 and self.k.kospi > 100:
            self.label1 = basicLabel(self, "매수는 신중하세요. 비중 30퍼센트(%s, %s)" % (self.k.kospi, self.k.kosdac))
            self.label1.setStyleSheet("Color : purple")
            self.label1.setFont(QtGui.QFont("맑은고딕", 14, QtGui.QFont.Bold))

        elif self.k.kospi > 80 and self.k.kospi < 100:
            self.label1 = basicLabel(self, "투자하기 좋은날. 비중 100퍼센트(%s, %s)" % (self.k.kospi, self.k.kosdac))
            self.label1.setStyleSheet("Color : blue")
            self.label1.setFont(QtGui.QFont("맑은고딕", 14, QtGui.QFont.Bold))

        elif self.k.kospi < 80:
            self.label1 = basicLabel(self, "공격적 투자 가능. 비중 200퍼센트(%s, %s)" % (self.k.kospi, self.k.kosdac))
            self.label1.setStyleSheet("Color : green")
            self.label1.setFont(QtGui.QFont("맑은고딕", 14, QtGui.QFont.Bold))

        self.center()           # Center() 함수를 통해 창이 화면의 가운데 위치
        self.show()


    def check_ADR(self):
        print("ADR 정보 가져오기")
        h5 = Thread5(self)
        h5.start


    def center(self):
        qr = self.frameGeometry()                          # 현재 메인 화면의 크기와 위치 정보를 qr에 저장, 창의 위치와 크기 정보를 가져옴
                                                           # 가상 프레임
        cp = QDesktopWidget().availableGeometry().center() # 사용하는 모니터 화면의 크기와 가운데 위치 파악
        qr.moveCenter(cp)                                  # 창의 직사각형 위치를 화면의 중심의 위치로 이동
        self.move(qr.topLeft())                  # 현재 창을 화면의 중심으로 이동했던 직사각형 (qr)의 위치로 이동
                                                 # 결과적으로 현재 창의 중심이 화면의 중심과 일치하게 되어 창의 가운데 정렬 됩니다.

class basicLabel(QtWidgets.QLabel):
    def __init__(self, frame, text):
        QtWidgets.QLabel.__init__(self, frame)
        self.setText(text)
        self.move(20, 20)