from PyQt5.QtWidgets import *                 # GUI의 그래픽적 요소를 제어       하단의 terminal 선택, activate py37_32,  pip install pyqt5,   전부다 y
from PyQt5.QAxContainer import *              # 키움증권의 클레스를 사용할 수 있게 한다.(QAxWidget)
from PyQt5Singleton import Singleton

# Kiwoom 클래스는 metaclass에 의해 생성되었으므로 인스턴스화 되었음
class Kiwoom(QWidget, metaclass=Singleton):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, parent=None, **kwargs):                    # Main class의 self를 초기화 한다.

        print("로그인 프로그램을 실행합니다.")

        super().__init__(parent, **kwargs)

        ################ 로그인 관련 정보

        self.kiwoom = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')       # CLSID
        # -> 키움에서 제공하는 함수를 사용하기 위해서는 반드시 self.kiwoom을 사용해야 함!

        ################ 전체 공유 데이터
        self.All_Stock_Code = {}            # {종목코드 : 종목명} 으로 되어있는 All_Stock_Code라는 딕셔너리 생성
        self.acc_portfolio = {}             # 계좌에 들어있는 종목의 코드, 수익률 등등 입력
        self.portfolio_stock_dict = {}      # 매매에 관한 모든 종목(현재계좌 종목/금일 등록 종목)이 모두 들어간다.

        self.today_meme = []                # 금일 매매하는 종목이 들어감
        self.not_account_stock_dist ={}     # 미체결 잔고

        ################ 오늘 산 잔고

        self.jango_dict = {}
        self.buy_jogon = {}                 # 미체결 잔고

        