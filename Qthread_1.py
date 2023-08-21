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

        def getItemList(self):
            marketList = ["0", "10"]    # 0 : 코스피  10 : 코스닥  3 : ELW  8 : ETF  50 : KONEX  4 :  뮤추얼펀드  5 : 신주인수권  6 : 리츠  9 : 하이얼펀드  30 : K-OTC

            for market in marketList:
                codeList = self.k.kiwoom.dynamicCall("GetCodeListByMarket(QString)", market).split(";")[:-1]    # 코스피, 코스닥 모든 종목들의 종목번호 불러오기

                for code in codeList:
                    name = self.k.kiwoom.dynamicCall("GetMasterCodeName(QString)", code)                        # 종목번호 -> 종목명
                    self.k.All_Stock_Code.update({code: {"종목명": name}})      # self.k에 All_Stock_Code라는 딕셔너리에 종목 코드와 이름 입력
                                                                                # 앞으로 종목 코드와 이름을 알고 싶으면 All_Stock_Code 딕셔너리에 접근하면 됨.