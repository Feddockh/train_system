import sys
from train_controller import TrainController, TrainModel
from tc_ui import *

def main():
    tm = TrainModel()
    
    tc = TrainController(tm)

    tc.current_speed = 5

    app = QApplication(sys.argv)
    window = EngineerWindow(tc)
    window.show()

    app.exec()

    print("ki: " + str(int(tc.engineer.get_ki())))
    print("kp: " + str(int(tc.engineer.get_kp())))



if __name__ == '__main__':
    main()