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
        ############# 기관/외국인 매매동향 가져오기 사용되는 변수
        self.Find_down_Screen = "1200"      # 계좌평가잔고내역을 받기 위한 스크린(50개 까지 가능)
                                            # -> 50개가 넘어가면 스크린 번호를 1201로 바꿔야 함
        self.code_in_all = None             # 1600개 코드 중 1개 코드, 쌓이지 않고 계속 갱신

        ############# 역배열인지 확인하기
        self.Predic_Screen = "1400"         # 일봉차트를 가져오기 위한 스크린
        self.calcul_data   = []             # 받아온 종목의 다양한 값(현재가/고가/저기 등) 계산
        self.second_filter = []             # 역배열인지 확인
        self.Predic_start  = []             # 미래예측

        ###### slot
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot)     # 내가 알고 있는 Tr 슬롯에다가 특정 값을 던져준다.

        ###### EventLoop
        self.detail_account_info_event_loop = QEventLoop()          # 계좌 이벤트루프

        ###### 기관외국인 평균가 가져오기
        self.C_K_F_class()              # opt10045를 실행할 함수 실행

        ###### 역배열 평가
        self.Invers_arrangement()

        ###### 결과 붙이기(GUI)
        column_head = ["종목코드", "종목명", "위험도", "역배열"]
        colCount = len(column_head)
        rowCount = len(self.k.acc_portfolio)
        self.parent.Danger_wd.setColumnCount(colCount)                      # 행 갯수
        self.parent.Danger_wd.setRowCount(rowCount)                         # 행 갯수 (종목 수)
        self.parent.Danger_wd.setHorizontalHeaderLabels(column_head)        # 행의 이름 삽입
        index2 = 0
        for k in self.k.acc_portfolio.keys():
            self.parent.Danger_wd.setItem(index2, 0, QTableWidgetItem(str(k)))
            self.parent.Danger_wd.setItem(index2, 1, QTableWidgetItem(self.k.acc_portfolio[k]["종목명"]))
            self.parent.Danger_wd.setItem(index2, 2, QTableWidgetItem(self.k.acc_portfolio[k]["위험도"]))
            self.parent.Danger_wd.setItem(index2, 3, QTableWidgetItem(self.k.acc_portfolio[k]["역배열"]))
            index2 += 1


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

    # 계좌위험도 판단 함수
    def kigwan_meme_dong2(self, a, c):      # a : 기관일별순매수량, b : 종가/기관/외국인 평균가, c : 외국인일별순매수량, d : 등락률
        
        # 일단 4일치 데이터만 사용해서 위험도를 판단하자.
        a = a[0:4]
        c = c[0:4]
        print(a)
        # a = sum(a, [])
        # c = sum(c, [])

        if a[0] < 0 and a[1] < 0 and a[2] < 0 and a[3] < 0 and c[0] < 0 and c[1] < 0 and c[2] < 0 and c[3] < 0:
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "손절"})
        
        elif a[0] < 0 and a[1] < 0 and a[2] < 0 and c[0] < 0 and c[1] < 0 and c[2] < 0:
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "주의"})

        elif a[0] < 0 and a[1] < 0 and c[0] < 0 and c[1] < 0:
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "관심"})
        
        else:
            self.k.acc_portfolio[self.code_in_all].update({"위험도" : "낮음"})
    
    def Invers_arrangement(self):
        # "주식일봉차트조회"
        
        code_list = []
        for code in self.k.acc_portfolio.keys():
            code_list.append(code)
        
        print("계좌포함 종목 %s" % (code_list))

        for idx, code in enumerate(code_list):
            QTest.qWait(1000)
            
            self.code_in_all = code     # 종목코드 선언 (중간에 코드 정보 받아오기 위해서)
            print("%s 종목 검사 중 코드이름 : %s." % (idx + 1, self.code_in_all))

            self.k.kiwoom.dynamicCall("DisconnectRealData(QString)", self.Predic_Screen)               # 해당 스크린 끊고 다시 시작
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")           # 수정주가구분 0 : 액면분할 등이 포함되지 않음, 1 : 포함됨
            self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", "0", self.Predic_Screen)
            self.detail_account_info_event_loop.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

        if sRQName == "종목별기관매매추이요청2":

            cnt2 = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)        # 10일치 이상을 하려면 이 부분에 10일치 이상 데이터가 필요
            # ex) 5/1~5/10일 일 경우 -> "GetRepeatCnt(QString, QString)" 함수는 10을 반환함

            self.calcul2_data = []
            self.calcul2_data2 = []         # 기관일별수매매수량
            self.calcul2_data3 = []         # 외국인일별순매수수량
            self.calcul2_data4 = []

            for i in range(cnt2):
                # 싱글데이터로 특정기간 내의 기관추정평균가/외인추정평균가를 받아옴
                # 멀티데이터로 기관일별순매매수량/외인일별순매매수량/등락률/종가 데이터를 가져옴
                Kigwan_meme = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "기관일별순매매수량"))
                Kigwan_meme_ave = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "기관추정평균가"))
                Forgin_meme = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "외인일별순매매수량"))
                Forgin_meme_ave = (self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "외인추정평균가"))
                percentage = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "등락율"))
                Jongga = (self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "종가"))

                self.calcul2_data.append(int(Kigwan_meme.strip()))
                self.calcul2_data2.append(abs(int(Jongga.strip())))
                self.calcul2_data2.append(abs(int(Kigwan_meme_ave.strip())))
                self.calcul2_data2.append(abs(int(Forgin_meme_ave.strip())))
                self.calcul2_data3.append(int(Forgin_meme.strip()))
                self.calcul2_data4.append(float(percentage.strip()))

                # 여기까지 code의 기관일별순매수수량, 외국인일별순매수량, 기관/외국인 평균가, 등락률 정보가 나온다.
                # self.kigwan_meme_dong2(self.calcul2_data, self.calcul2_data2[0:3], self.calcul2_data3, self.calcul2_data4)
            
            self.kigwan_meme_dong2(self.calcul2_data, self.calcul2_data3)

            self.detail_account_info_event_loop.exit()

        if sRQName == "주식일봉차트조회":
            # GetCommData -> 데이터를 받아오는 함수
            code = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()     # 여백 발생 방지
            cnt = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            #print("데이터 일수 %s" % cnt)
            # 600일치 데이터를 한번에 받아오는 함수 : GetCommDataEx, 리스트로 변환
            # data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)
            # [[''], '현재가', '거래량', '거래대금', '날짜', '시가', '고가', '저가', ''], [...], [...], ..... ]

            for i in range(cnt):        # [0] ~ [599]
                data = []
                current_price = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")     # GetCommDataEx함수의 반환값과 동일하게 하기 위해서!
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.Predic_start.append(int(current_price.strip()))            # 미래를 예측하기 위한 코드인데 강의에서 다루지 않을 예정.
                self.calcul_data.append(data.copy())            # 리스트로 데이터가 들어간다. -> 레지스터 주소가 중복되지 않게 복사
                # self.Predic_start -> 600일치의 현재가 포함
                # self.calcul_data -> 600일치의 고가/저가/현재가 등등이 포함

            if self.calcul_data == None or len(self.calcul_data) < 210:
                self.k.acc_portfolio[self.code_in_all].update({"역배열" : "데이터 없음"})
            
            else:           # 만약 120개의 데이터가 존재한다면
                total_five_price = []       # 초기화
                total_twenty_price = []     # 초기화
                
                # 5일선, 20일선 데이터 10개씩 계산
                for k in range(10):
                    total_five_price.append(sum(self.Predic_start[k: 5 + k]) / 5)
                
                for k in range(10):
                    total_twenty_price.append(sum(self.Predic_start[k: 20 + k]) / 20)
                
                add_item = 0

                for k in range(10):
                    if float(total_five_price[k]) < float(total_twenty_price[k]) and float(self.calcul_data[k][1]) < float(total_twenty_price[k]):
                        # 5일선 < 20일선 and 현재가 < 20일선 인 경우 add_time에 1씩 더한다.
                        add_item += 1
                    else:
                        pass
                
                if add_item >= 8:
                    self.k.acc_portfolio[self.code_in_all].update({"역배열" : "맞음"})
                else:
                    self.k.acc_portfolio[self.code_in_all].update({"역배열" : "아님"})
                
            self.calcul_data.clear()        # 코드에 들어있는 일봉 데이터 삭제
            self.Predic_start.clear()

            self.detail_account_info_event_loop.exit()
                    


