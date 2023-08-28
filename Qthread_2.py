from PyQt5.QtCore import *              # eventloop/쓰레드 함수 불러오기
from kiwoom import Kiwoom               # 로그인을 위한 클래스
from PyQt5.QtWidgets import *           # PyQt import
from PyQt5.QtTest import *              # 시간관련 함수
from datetime import datetime, timedelta    # 특정 일자 조회


class Thread2(QThread):
    def __init__(self, parent):         # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)        # 부모의 윈도우 창 초기화
        self.parent = parent            # 부모의 윈도우를 사용하기 위한 조건

        self.k = Kiwoom()               # kiwoom 함수 상속