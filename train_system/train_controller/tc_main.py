import sys
from train_controller import TrainController, TrainModel
from tc_ui import *

def main():
    tm = TrainModel()
    
    tc = TrainController(tm)

    #test ui inputs
    #tc.engineer.set_ki(1)

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
    print("engine fault: " + str(tc.faults[0]))
    print("em brake: " + str(tc.brake.get_emergency_brake()))
    print("service brake: " + str(tc.brake.get_service_brake()))
    print("right door " + str(tc.doors.get_right()))
    print("lights: " + str(tc.lights.get_status()))




if __name__ == '__main__':
    main()