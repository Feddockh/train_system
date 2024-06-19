import sys
from train_controller import TrainController, TrainModel
from tc_ui import *

def main():
    tm = TrainModel()
    
    tc = TrainController(tm)

    #test ui inputs
    tc.current_speed = 5
    tc.commanded_speed = 7
    tc.faults[0] = True

    #open ui
    app = QApplication(sys.argv)
    window = EngineerWindow(tc)
    window.show()

    app.exec()

    #test ui outputs
    print("ki: " + str(int(tc.engineer.get_ki())))
    print("kp: " + str(int(tc.engineer.get_kp())))
    print("setpoint speed: " + str(tc.setpoint_speed))
    print("comm temp: " + str(tc.ac.get_commanded_temp()))



if __name__ == '__main__':
    main()