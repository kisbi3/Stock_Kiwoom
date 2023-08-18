import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

'''
    8강부터!!
'''

form_class = uic.loadUiType("main_windows.ui")[0]             # 만들어 놓은 ui 불러오기

class Login_Machnine(QMainWindow, QWidget, form_class):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, *args, **kwargs):                      # Main class의 self를 초기화 한다.

        print("Login Machine 실행합니다.")
        super(Login_Machnine, self).__init__(*args, **kwargs)
        form_class.__init__(self)                            # 상속 받은 from_class를 실행하기 위한 초기값(초기화)
        self.setUI()                                         # UI 초기값 셋업 반드시 필요

    def setUI(self):
        self.setupUi(self)                # UI 초기값 셋업

if __name__=='__main__':             # import된 것들을 실행시키지 않고 __main__에서 실행하는 것만 실행 시킨다.
                                     # 즉 import된 다른 함수의 코드를 이 화면에서 실행시키지 않겠다는 의미이다.

    app = QApplication(sys.argv)     # PyQt5로 실행할 파일명을 자동으로 설정, PyQt5에서 자동으로 프로그램 실행
    CH = Login_Machnine()            # Main 클래스 myApp으로 인스턴스화
    CH.show()                        # myApp에 있는 ui를 실행한다.
    app.exec_()                      # 이벤트 루프