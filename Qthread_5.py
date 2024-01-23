from PyQt5.QtCore import *      # 쓰레드 함수 불러오기
from kiwoom import Kiwoom       # 로그인을 위한 클래스
from urllib.request import urlopen
from bs4 import BeautifulSoup




class Thread5(QThread):
    def __init__(self, parent):         # 부모의 윈도우 창 가져오기
        super().__init__(parent)        # 부모의 윈도우 창 초기화
        self.parent = parent            # 부모의 윈도우를 사용하기 위한 조건

        self.k = Kiwoom()

        response = urlopen("http://adrinfo.kr/")            # 크롤링 하고자 하는 사이트
        soup = BeautifulSoup(response, "html.parser")       # html에 저버근할 수 있도록

        i = 0
        k = [0, 0]
        for link in soup.select("h2.card-title"):
            a = link.text.strip()
            k[i] = a[0:5].strip()
            i = i+1

        self.k.kospi = float(k[0])
        self.k.kosdac = float(k[1])
