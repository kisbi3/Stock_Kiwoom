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

        # self.parent.progressBar5.setMaximum(len(code_list) - 1 )      # 나중에 설명

        for idx, code in enumerate(code_list):                          # code_list에 있는 종목번호들에 'index'부여해서 index는 idx, 종목번호는 code
            # self.parent.progressBar5.setValue(idx)                    # 나중에 설명
            
            QTest.qWait(1000)       # 1000ms(1s)씩 지연 발생 -> 키움 서버에 짧은 시간 안에 너무 많은 명령을 전송하면 계좌가 일시 정지하게 됨.
                                    # 보통 3.6s(3600ms)마다 1번씩 명령을 전송하는 것이 안전함.

            self.k.kiwoom.dynamicCall("DisconnectRealData(QString)", self.Find_down_Screen)     # 해당 스크린을 끊고 다시 시작
            # 몇개의 주문마다 스크린 번호를 바꿔 주거나 끊어줄지는 선택하자!

            self.code_in_all = code                         # 종목코드 선언( 중간에 코드 정보 받아오기 위해서 ) -> 위험도 판단 시 사용될 예정
            print("%s / %s  : 종목 검사 중 코드이름 : %s." % (idx + 1, len(code_list), self.code_in_all))

            # 기관 평균가를 받아오는 날짜를 정의하는 곳
            date_today = datetime.today().strftime("%Y%m%d")
            date_prev = datetime.today() - timedelta(10)        # 넉넉히 1일 전의 데이터를 바당온다. 또는 20일 이상 데이터도 필요
            date_prev = date_prev.strftime("%Y%m%d")

            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시작일자", date_prev)      # 모의투자 0000
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종료일자", date_today)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기관추정단가구분", "1")
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "외인추정단가구분", "1")
            self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "종목별기관매매추이요청2", "opt10045", "0", self.Find_down_Screen)
            self.detail_account_info_event_loop.exec_()


    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sRQName == "종목별기관매매추이요청2":

            cnt2 = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)        # 10일치 이상을 하려면 이 부분에 10일치 이상 데이터가 필요
            # ex) 5/1~5/10일 일 경우 -> "GetRepeatCnt(QString, QString)" 함수는 10을 반환함

            self.calcul2_data = []
            self.calcul2_data2 = []
            self.calcul2_data3 = []
            self.calcul2_data4 = []

            for i in range(cnt2):
                # 싱글데이터로 특정기간 내의 기관추정평균가/외인추정평균가를 받아옴
                # 멀티데이터로 기관일별순매매수량/외인일별순매매수량/등락률/종가 데이터를 가져옴
                Kigwan_meme = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "기관일별순매매수량"))
                Kigwan_meme_ave = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "기관추정평균가"))
                Forgin_meme = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "외인일별순매매수량"))
                Forgin_meme_ave = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "외인추정평균가"))
                percentage = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "등락률"))
                Jongga = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "종가"))

                self.calcul2_data.append(int(Kigwan_meme.strip()))
                self.calcul2_data2.append(abs(int(Jongga.strip())))
                self.calcul2_data2.append(abs(int(Kigwan_meme_ave.strip())))
                self.calcul2_data2.append(abs(int(Forgin_meme_ave.strip())))
                self.calcul2_data3.append(int(Forgin_meme.strip()))
                self.calcul2_data4.append(float(percentage.strip()))

                # 여기까지 code의 기관일별순매수수량, 외국인일별순매수량, 기관/외국인 평균가, 등락률 정보가 나온다.