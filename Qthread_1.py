from PyQt5.QtCore import *              # 쓰레드 함수 불러오기
from kiwoom import Kiwoom               # 로그인을 위한 클래스
from PyQt5.QtWidgets import *

class Thread1(QThread):
    def __init__(self, parent):   # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)  # 부모의 윈도우 창을 초기화 한다.
        self.parent = parent      # 부모의 윈도우를 사용하기 위한 조건


        ################## 키움서버 함수를 사용하기 위해서 kiwoom의 능력을 상속 받는다.
        self.k = Kiwoom()
        ##################

        ################## 사용되는 변수
        self.Acc_Screen = "1000"         # 계좌평가잔고내역을 받기위한 스크린을 '1000'으로 할당

        ###### 슬롯
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)  # 내가 알고 있는 Tr 슬롯에다 특정 값을 던져 준다.
        
        ###### EventLoop
        self.detail_account_info_event_loop = QEventLoop()  # 계좌 이벤트루프