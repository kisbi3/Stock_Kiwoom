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

        ##### 계좌정보 가져오기
        self.getItemList()                      # 종목 이름 받아오기
        self.detail_account_mystock()           # 계좌평가잔고내역 가져오기


        def getItemList(self):
            marketList = ["0", "10"]    # 0 : 코스피  10 : 코스닥  3 : ELW  8 : ETF  50 : KONEX  4 :  뮤추얼펀드  5 : 신주인수권  6 : 리츠  9 : 하이얼펀드  30 : K-OTC

            for market in marketList:
                codeList = self.k.kiwoom.dynamicCall("GetCodeListByMarket(QString)", market).split(";")[:-1]    # 코스피, 코스닥 모든 종목들의 종목번호 불러오기

                for code in codeList:
                    name = self.k.kiwoom.dynamicCall("GetMasterCodeName(QString)", code)                        # 종목번호 -> 종목명
                    self.k.All_Stock_Code.update({code: {"종목명": name}})      # self.k에 All_Stock_Code라는 딕셔너리에 종목 코드와 이름 입력
                                                                                # 앞으로 종목 코드와 이름을 알고 싶으면 All_Stock_Code 딕셔너리에 접근하면 됨.

        def detail_account_mystock(self, sPrevNext="0"):        # 키움서버에서 조회할 데이터가 30개 이상이면 2, 그 이하면 0을 반환

            print("계좌평가잔고내역 조회")
            account = self.parent.accComboBox.currentText() # 콤보박스의 계좌번호를 가져오는 부분
                                                            # parent를 이용하여 부모 GUI에 접근할 수 있는 권한을 할당받음
            self.account_num = account                      # 파일 Qthread_1 어디에서도 계좌번호를 사용할 수 있도록 self 를 이용해 저장
            print("최종 선택 계좌는 %s" % self.account_num)

            # dynamicCall 함수를 이용해 키움에 명령 전송
            self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", account)
            self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")      # 모의투자 0000
            self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
            self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
            self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.Acc_Screen)
            self.detail_account_info_event_loop.exec()              # 계좌평가잔고내역요청을 키움 서버로 전송한 후 모든 처리가 완성될 때 까지 다음 코드가 진행되지 않도록 막아주는 이벤트 루프

        # BSTR sScrNo : 화면번호, BSTR sRQName : 사용자 구분명, BSTR sTrCode : TR이름(종목번호), BSTR sPrevNext : 이전/다음 페이지
        def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

            if sRQName == "계좌평가잔고내역요청":

                column_head = ["종목번호", "종목명", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"]
                colCount = len(column_head)
                rowCount = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
                self.parent.stocklistTableWidget_2.setColumnCount(colCount)                 # 행 갯수
                self.parent.stocklistTableWidget_2.setRowCount(rowCount)                    # 열 갯수 (종목 수)
                self.parent.stocklistTableWidget_2.setHorizontalHeaderLabels(column_head)   # 행의 이름 삽입

                self.rowCount = rowCount

                print("계좌에 들어있는 종목 수 %s" % rowCount)

                totalBuyingPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액"))
                currentTotalPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
                balanceAsset = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "추정예탁자산"))
                totalEstimateProfit = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
                total_profit_loss_rate = float(self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)"))