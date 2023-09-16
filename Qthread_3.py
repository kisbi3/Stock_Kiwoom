
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


