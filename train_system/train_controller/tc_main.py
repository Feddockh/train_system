import sys
from train_controller import TrainController, TrainModel
from tc_ui import *

def main():
    tm = TrainModel()
    
    tc = TrainController(tm)

    #test ui inputs
    #tc.faults[1] = True

    #tc.update_train_controller()

    #print("controller speed " + str(tc.authority))
    #print("train model authority " + str(tc.train_model.authority))

    #open ui
    app = QApplication(sys.argv)
    window = EngineerWindow(tc)
    window.show()

    app.exec()

    #test ui outputs
    #print("train model authority " + str(tc.train_model.authority))
    #print("controller authority " + str(tc.authority))
    




if __name__ == '__main__':
    main()