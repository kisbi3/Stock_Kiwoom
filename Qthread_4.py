from PyQt5.QtCore import *         # 쓰레드 함수를 불러온다.
from kiwoom import Kiwoom          # 메타클레스 기반 싱글턴
from urllib.request import urlopen # 크롤링 사이트 여는 함수
from bs4 import BeautifulSoup      # 크롤링 사이트의 값을 가져오는 함수


class Thread4(QThread):
    def __init__(self, parent):   # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)  # 부모의 윈도우 창을 초기화 한다.
        self.parent = parent      # 부모의 윈도우를 사용하기 위한 조건

        self.k = Kiwoom()

        response = urlopen("https://search.naver.com/search.naver?sm=mtb_drt&where=m&query=%EB%AF%B8%EA%B5%AD%ED%99%98%EC%9C%A8")  # 크롤링하고자하는 사이트
        # <div class="price_info"> <strong class="price">1,338.50</strong> <span class="u_hc">전일대비 상승</span> <span class="price_gap">1.50<span>(-0.11%)</span></span> </div>
        soup = BeautifulSoup(response, "html.parser")  # html에 대하여 접근할 수 있도록

        value = soup.find("div", {"class": "price_info"})
        value2 = value.text.split()

        del value2[1:3]

        a = value2[0].strip(',')  # 환율값
        dist = value2[1].split('(')
        c = dist[1].strip(')')      # 증가/하락 비율
        if c[0] == '+':
            b = '+' + dist[0]           # 증가/하락
        elif c[0] == '-':
            b = '-' + dist[0]           # 증가/하락
        else:
            # 변동이 없을 경우.
            b = dist[0]                 # 증가/하락

        print(a, b, c)

        self.parent.exchange_1.setPlainText(a)
        self.parent.exchange_2.setPlainText(b)
        self.parent.exchange_3.setPlainText(c)

        self.parent.exchange_1.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.parent.exchange_2.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.parent.exchange_3.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        print(float(c[1:4]))
        if "-" in c and float(c[1:5]) > 1:                   # 환율이 떨어지고, 떨어지는 폭이 1퍼센트 이상이면
            self.parent.exchange_4.setPlainText(str(0.15))
        if "-" in c and float(c[1:5]) < 1:                   # 환율이 떨어지고, 떨어지는 폭이 1퍼센트 이하이면
            self.parent.exchange_4.setPlainText(str(0.10))
        elif "-" not in c and float(c[1:5]) < 1:                   # 환율이 올라가고, 올라가는 폭이 1퍼센트 이하이면
            self.parent.exchange_4.setPlainText(str(0.05))
        elif "-" not in c and float(c[1:5]) > 1:                   # 환율이 올라가고, 올라가는 폭이 1퍼센트 이상이면
            self.parent.exchange_4.setPlainText(str(0.01))

        self.parent.exchange_4.setAlignment(Qt.AlignVCenter | Qt.AlignRight)