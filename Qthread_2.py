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
        ############# 사용되는 변수
        self.Find_down_Screen = "1200"      # 계좌평가잔고내역을 받기 위한 스크린(50개 까지 가능)
                                            # -> 50개가 넘어가면 스크린 번호를 1201로 바꿔야 함
        self.code_in_all = None             # 1600개 코드 중 1개 코드, 쌓이지 않고 계속 갱신

        ###### slot
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)     # 내가 알고 있는 Tr 슬롯에다가 특정 값을 던져준다.

        ###### EventLoop
        self.detail_account_info_event_loop = QEventLoop()          # 계좌 이벤트루프

        ###### 기관외국인 평균가 가져오기
        self.C_K_F_class()              # opt10045를 실행할 함수 실행
    

    def C_K_F_class(self):
        code_list = []                      # 계좌에 있는 종목을 불러와 저장하기 위한 장소
        
        # QThread_1.py에서 acc_portfolio에 계좌의 종목 정보를 넣어두었음. -> key()를 이용해 코드 번호만 가져오기
        for code in self.k.acc_portfolio.keys():
            code_list.append(code)
        
        print("계좌 종목 개수 %s" % (code_list))