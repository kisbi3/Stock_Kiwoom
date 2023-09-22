
import os
from PyQt5.QtCore import *              # 쓰레드 함수 불러오기
from kiwoom import Kiwoom               # 로그인을 위한 클래스
from kiwoomType import *                # 실시간 정보를 받아오기 위해 반드시 필요한 FID번호를 저장한 곳.

class Thread3(QThread):
    def __ini__(self, parent):          # 부모의 윈도우 창을 가져올 수 있게 하기
        super().___init___(parent)      # 부모의 윈도우 창을 초기화
        self.parent = parent            # 부모의 윈도우를 사용하기 위한 조건


        ############ 키뭉서버 함수를 사용하기 위해 kiwoom의 능력 상속받기
        self.k = Kiwoom()
        ############

        ############ 사용되는 변수
        account = self.parent.accComboBox.currentText()         # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        # 계좌번호 가져오는 부분은 Qthread_3 분리시 로그인 후 계좌번호를 가져오는 함수로 교체된다.
        # 각 Thread는 통신을 하지 못함 -> GUI에 입력된 계좌번호를 가져와야 함

        ############ 매수관련 변수
        self.Load_code()

        ############ 주문 전송 시 필요한 FID 번호
        self.realType = RealType()      # 실시간 FID 번호 모아두는 곳

        ############################################################
        ###### 등록된 계좌 체 해제하기(작동 정지 되었을 때 등록 정보를 끊어야 함.)
        self.k.kiwoom.dynamicCall("SetRealRemove(QString, QString)", ["ALL", "ALL"])
        ############################################################

        self.screen_num = 5000
        for code in self.k.portfolio_stock_dict.keys():
            fids = self.realType.REALTYPE['주식체결']['체결시간']
            self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_num, code, fids, "1")
            # 하나만 요청해도 기타 정보인 "현재가", "거래량" 등의 20가지가 넘은 다양한 데이터를 넘겨줌.
            self.screen_num += 1

        # print("실시간 등록  : %s, 스크린번호 : %s, FID 번호 : %s" %(code, screen_num, fids))
        print("종목등록 완료")
        print(self.k.portfolio_stock_dict.keys())

        ######################################################################
        ###### 현재 장 상태 알아보기 (장 시작 / 장 마감 등)
        self.screen_start_stop_real = "300"       # 장시 시작 전/후 상태 확인용 스크린 번호
        self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")  # 장의 시작인지, 장 외인지등에 대한 정보 수신, 연속 조회가 필요 없음 : 0

        ###### 실시간 슬롯 (데이터를 받아오는 슬롯을 설정한다)
        self.k.kiwoom.OnReceiveRealData.connect(self.realdata_slot)   # 실시간 데이터를 받아오는 곳
    
    def Load_code(self):

        if os.path.exists("dist/Selected_code.txt"):
            f = open("dist/Selected_code.txt", "r", encoding = "utf8")
            lines = f.readlines()                       # 여러 종목이 저장되어 있다면 모든 항목을 가져온다.
            screen = 4000
            
            for line in lines:
                if line != "":
                    ls = line.split("\t")
                    t_code = ls[0]
                    t_name = ls[1]
                    curren_price = ls[2]
                    dept = ls[3]
                    mesu = ls[4]
                    n_o_stock = ls[5]
                    profit =ls[6]
                    loss = ls[7].split("\n")[0]

                    self.k.portfolio_stock_dict.update({t_code: {"종목명": t_name}})        # dictionary에 종목 추가
                    self.k.portfolio_stock_dict[t_code].update({"현재가": int(curren_price)})
                    self.k.portfolio_stock_dict[t_code].update({"신용비율": dept})
                    self.k.portfolio_stock_dict[t_code].update({"매수가": int(mesu)})
                    self.k.portfolio_stock_dict[t_code].update({"매수수량": int(n_o_stock)})
                    self.k.portfolio_stock_dict[t_code].update({"익절가": int(profit)})
                    self.k.portfolio_stock_dict[t_code].update({"손절가": int(loss)})
                    self.k.portfolio_stock_dict[t_code].update({"주문용스크린번호": screen})  # 아래 내용을 업데이트
                    screen += 1                                                             # 종목마다 스크린 번호를 다르게 하기
            
            f.close()


