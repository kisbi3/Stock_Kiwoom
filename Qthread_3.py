
import os
from PyQt5.QtCore import *              # 쓰레드 함수 불러오기
from kiwoom import Kiwoom               # 로그인을 위한 클래스
from kiwoomType import *                # 실시간 정보를 받아오기 위해 반드시 필요한 FID번호를 저장한 곳.

class Thread3(QThread):
    def __ini__(self, parent):          # 부모의 윈도우 창을 가져올 수 있게 하기
        super().___init___(parent)      # 부모의 윈도우 창을 초기화
        self.parent = parent            # 부모의 윈도우를 사용하기 위한 조건


        ############ 키움서버 함수를 사용하기 위해 kiwoom의 능력 상속받기
        self.k = Kiwoom()
        ############

        ############ 사용되는 변수
        account = self.parent.accComboBox.currentText()         # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        # 계좌번호 가져오는 부분은 Qthread_3 분리시 로그인 후 계좌번호를 가져오는 함수로 교체된다.
        # 각 Thread는 통신을 하지 못함 -> GUI에 입력된 계좌번호를 가져와야 함

        ############ 매수관련 변수
        self.Load_code()                # 매수 종목/금액/수량 가져오기
        self.orderitmelist_1 = []       # 중복 매수를 금지하기 위해 매수한 것들 모아두는 리스트

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
    

    def realdata_slot(self, sCode, sRealType, sRealData):       # 실시간으로 서버에서 데이터들이 날아옴

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']

            # 실시간 시세 데이터 수신 이벤트인 OnReceiveRealData() 가 발생될 때 실시간 데이터를 가져오는 함수
            value = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == '0':
                print("장 시작 전")
            
            elif value == '3':
                print("장 중")
            
            elif value == '2':
                print("장 종료, 동시호가")
            
            elif value == '4':
                print("장 마감")
        

        elif sRealType == "주식체결" and sCode in self.k.portfolio_stock_dict:

            fid1 = self.realType.REALTYPE[sRealType]['체결시간']        #체결시간은 string으로 나온다. HHMMSS
            a = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid1)

            fid2 = self.realType.REALTYPE[sRealType]['현재가']        # 현재가는 +/-으로 나온다.
            b = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid2)
            b = abs(int(b))

            fid3 = self.realType.REALTYPE[sRealType]['전일대비']        # 전일대비 오르거나 내린 가격
            c = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid3)
            c = abs(int(c))

            fid4 = self.realType.REALTYPE[sRealType]['등락율']        # 전일대비 오르거나 내린 비율
            d = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid4)
            d = float(d)

            fid5 = self.realType.REALTYPE[sRealType]['(최우선)매도호가']        # 제일 저렴한 매도호가
            e = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid5)
            e = abs(int(e))

            fid6 = self.realType.REALTYPE[sRealType]['(최우선)매수호가']  # 제일 비싼 매수호가
            f = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid6)
            f = abs(int(f))

            fid7 = self.realType.REALTYPE[sRealType]['거래량']  # 틱봉의 현재 거래량
            g = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid7)
            g = abs(int(g))

            fid8 = self.realType.REALTYPE[sRealType]['누적거래량']
            h = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid8)
            h = abs(int(h))

            fid9 = self.realType.REALTYPE[sRealType]['고가']
            i = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid9)
            i = abs(int(i))

            fid10 = self.realType.REALTYPE[sRealType]['시가']
            j = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid10)
            j = abs(int(j))

            fid11 = self.realType.REALTYPE[sRealType]['저가']
            k = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid11)
            k = abs(int(k))

            fid12 = self.realType.REALTYPE[sRealType]['거래회전율']  # 누적 거래회전율
            l = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid12)
            l = abs(float(l))

            if sCode not in self.k.portfolio_stock_dict:           # 만약 서버에 등록된 코드가 포트폴리오에 없다면 코드를 등록
                self.k.portfolio_stock_dict.update({sCode: {}})

            # 포트폴리오 종목코드마다 아래 실시간 데이터를 입력
            self.k.portfolio_stock_dict[sCode].update({"채결시간": a})       # 아래 내용을 업데이트
            self.k.portfolio_stock_dict[sCode].update({"현재가": b})
            self.k.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.k.portfolio_stock_dict[sCode].update({"등락율": d})
            self.k.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.k.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.k.portfolio_stock_dict[sCode].update({"거래량": g})
            self.k.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.k.portfolio_stock_dict[sCode].update({"고가": i})
            self.k.portfolio_stock_dict[sCode].update({"시가": j})
            self.k.portfolio_stock_dict[sCode].update({"저가": k})
            self.k.portfolio_stock_dict[sCode].update({"거래회전율": l})

            #1. 매수 알고리즘 가동

            #1차#############################################################################################
            # 현재 가격이 매수가격보다 같거나 낮은 구간에서 아래 조건문이 실행
            if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode]["매수가"]:
                # 중복매수 방지 코드 1
                # 중복매수를 막기 위해 self.orderitmelist_1 리스트에 종목이 있는지 확인하기
                if sCode not in self.orderitmelist_1:    
                    # 중복매수 방지 코드 2
                    # wa 리스트에 sCode를 넣어서, 만약 wa의 길이가 2 이상일 경우 종목 체결 금지
                    wa = []
                    wa.append(sCode)
                    if len(wa) > 1:
                        wa.clear()
                        pass
                    else:
                        print("매수 시작 %s" % sCode)

                        self.orderitmelist_1.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기 (중복매수 방지 코드 1)
                        ''' [SendOrder() 함수 설명]
                        SendOrder(
                        BSTR sRQName, // 사용자 구분명
                        BSTR sScreenNo, // 화면번호
                        BSTR sAccNo,  // 계좌번호 10자리
                        LONG nOrderType,  // 주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                        BSTR sCode, // 종목코드 (6자리)
                        LONG nQty,  // 주문수량
                        LONG nPrice, // 주문가격
                        BSTR sHogaGb,   // 거래구분(혹은 호가구분)은 아래 참고
                        BSTR sOrgOrderNo  // 원주문번호. 신규주문에는 공백 입력, 정정/취소시 입력합니다.
                        )
                        '''
                        order_success1 = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                                                   ["신규매수", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1, sCode,
                                                                    self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                                                                    self.realType.SENDTYPE['거래구분']['지정가'], ""])
                        # 시장가로 매수하길 원한다면... "현재가" --> "최우선 매도호가" 등

                        # 매수/매도 현황 데이터베이스화 : 종목명, 체결시간
                        wf2 = open("dist/mesu_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("1매수정보", self.k.portfolio_stock_dict[sCode]["종목명"], b, self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                        wf2.close()

                        # 주문 상태 확인
                        if order_success1 == 0:
                            print("최우선매수호가로 주문 전달 성공")
                        else:
                            print("최우선매수호가로 주문 전달 실패")


            #2. 매도 알고리즘 가동
            # 기본적으로 매수 알고리즘과 동일함.
            #1차 익절 #############################################################################################
            if self.k.portfolio_stock_dict[sCode]["현재가"] >= self.k.portfolio_stock_dict[sCode]["익절가"]:
                if sCode not in self.orderitmelist_2:

                    wa = []
                    wa.append(sCode)

                    if len(wa) > 1:
                        wa.clear()
                        pass
                    else:
                        print("익절 시작 %s" % sCode)

                        self.orderitmelist_2.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                        order_success2 = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                                                   ["신규익절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2, sCode,
                                                                    self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                                                                    self.realType.SENDTYPE['거래구분']['지정가'], ""])

                        wf2 = open("dist/mesu_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("1익절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b, self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                        wf2.close()

                        if order_success2 == 0:
                            print("익절가로 주문 전달 성공")
                        else:
                            print("익절가로 주문 전달 실패")

            #1차 손절 #############################################################################################
            if self.k.portfolio_stock_dict[sCode]["현재가"] <= self.k.portfolio_stock_dict[sCode]["손절가"]:
                if sCode not in self.orderitmelist_3:

                    wa = []
                    wa.append(sCode)

                    if len(wa) > 1:
                        wa.clear()
                        pass
                    else:
                        print("손절 시작 %s" % sCode)

                        self.orderitmelist_3.append(sCode)  # 이 기법을 더이상 사용하지 못하게 하기
                        order_success3 = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString ,int, QString, int, int, QString, QString)",
                                                                   ["신규손절", self.k.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2, sCode,
                                                                    self.k.portfolio_stock_dict[sCode]["매수수량"], self.k.portfolio_stock_dict[sCode]["현재가"],
                                                                    self.realType.SENDTYPE['거래구분']['지정가'], ""])

                        wf2 = open("dist/mesu_database.txt", "a", encoding="utf8")  # "a" 달아 쓴다. "w" 덮어 쓴다. files라느 파이썬 페키지 볼더를 만든다.
                        wf2.write("%s\t%s\t%s\t%s\n" % ("1손절정보", self.k.portfolio_stock_dict[sCode]["종목명"], b, self.k.portfolio_stock_dict[sCode]["채결시간"]))  # t는 tap을 의미한다.
                        wf2.close()

                        if order_success3 == 0:
                            print("손절가로 주문 전달 성공")
                        else:
                            print("손절가로 주문 전달 실패")


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


    def chejan_slot(self, sGubun, nItemCnt, sFIdList):   # 주문전송 후 주문접수, 체결통보, 잔고통보를 수신

        if sGubun == "0":
            print("매수/매도 중입니다. 미체결 잔고 업데이트")
        else:
            print("미체결잔고 해결로 실제 잔고 업데이트")

        if int(sGubun) == 0:   # 주문전송 후 미체결 되었을 때 아래와 같은 연산을 해 준다.
            account_num = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]  # [A203042]  -->  [1:] => [203042]
            stock_name = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()  # 혹시라도 공백이 있을 까봐
            origin_order_number = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])  # 원주문번호가 없으면 0000000이다
            order_number = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])
            order_status = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])  # 접수/확인/체결 정보
            order_quan = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])
            order_quan = int(order_quan)
            order_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])
            order_price = int(order_price)
            not_chegual_quan = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])
            not_chegual_quan = int(not_chegual_quan)
            order_gubun = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])  # 정정 등, 부호가 나오기 때문에 잡아줘야 된다.
            order_gubun = order_gubun.lstrip('+').lstrip('-')
            order_gubun = order_gubun.strip()
            chegual_time_str = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])  # '151028'
            chegual_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])       # 체결 X인 경우 -> 공백으로 넘어옴

            if chegual_price == '':
                chegual_price = 0  # 숫자로 할당
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])

            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])
            current_price = abs(int(current_price))
            first_sell_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))
            first_buy_price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))