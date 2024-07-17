import sys
from train_system.train_controller.train_controller import TrainController, TrainModel
from train_system.train_controller.tc_ui import *

def main():
    tm = TrainModel()
    
    tc = TrainController(tm)

    driver = DriverWindow()
    

    #open ui
    app = QApplication(sys.argv)
    window = EngineerWindow(tc)
    window.show()

    app.exec()

    #test ui outputs
    print("train model temp " + str(tc.train_model.get_train_temp()))
    print("controller temp " + str(tc.ac.get_commanded_temp()))
    




if __name__ == '__main__':
    main()