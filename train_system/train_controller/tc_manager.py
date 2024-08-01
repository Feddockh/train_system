import paramiko

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from train_system.common.time_keeper import TimeKeeper
from train_system.train_controller.train_controller import TrainModelController
from train_system.train_controller.engineer import Engineer
from train_system.common.authority import Authority
from train_system.train_controller.tc_main import tc_main
from train_system.common.time_keeper import TimeKeeper

HOST= '192.168.0.77'
HOSTNAME = 'rp'
PORT = 22
USERNAME = 'danim'
PASSWORD = 'danim'

# Create the time keeper object


class TrainManager(QObject):

    test_signal = pyqtSignal(bool)
    train_dispatched = pyqtSignal(str, int, TrainModelController)    # line, train_id, train_system

    def __init__(self, time_keeper: TimeKeeper = None):
        super().__init__()

        self.time_keeper = time_keeper
        self.train_count = 40
        self.engineer_table: list[Engineer] = [Engineer()] * self.train_count
        self.train_list: list[TrainModelController] = []
        if HOST and PORT and USERNAME and PASSWORD:
            print("Host: ", HOST, "Port: ", PORT, "Username: ", USERNAME, "Password: ", PASSWORD)
            self.ssh_client = self.create_ssh_connection(HOSTNAME, PORT, USERNAME, PASSWORD)
        else:
            self.ssh_client = None

    # Example usage
    def create_ssh_connection(self, host, port=22, username='danim', password='danim'):
        """Establish an SSH connection to the Raspberry Pi and return the SSH client."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Connect to the Raspberry Pi
            ssh.connect(host, port, username, password)
            print("Connection established")
            return ssh
        except Exception as e:
            print(f"An error occurred while connecting: {e}")
            return None

    #### Might need to be engineer_table[id-1] ####
    @pyqtSlot(int, str)
    def handle_dispatch(self, train_id: int = 0, line: str = "green"):
        if train_id % 2 and self.ssh_client:
            # Add hardware train to the train list
            print("Hardware Train")
            self.train_list.append(TrainModelController(self.time_keeper, self.engineer_table[train_id], line, train_id, self.ssh_client))
        else:
            # Add software train to the train list
            print("Software Train")
            self.train_list.append(TrainModelController(self.time_keeper, self.engineer_table[train_id], line, train_id))
        self.train_dispatched.emit(line, train_id, self.train_list[-1])
            
        ##### ADD CONNECTIONS TO THE TRAIN SYSTEM #####
        self.train_list[-1].controller.delete_train.connect(self.handle_train_removed)
        print("DISPATCHED TRAIN")
        tc_main(self.time_keeper,TrainModelController(self.time_keeper, self.engineer_table[train_id], line, train_id, self.ssh_client))

    # When train reaches the yard, it removes itself from the train list
    #### NEED TO MANUALLY DELETE CONNECTIONS AS THE CONNECTIONS AREN'T DELETED WHEN TRAIN IS REMOVED ####
    @pyqtSlot(int)
    def handle_train_removed(self, train_id: int):
        for train in self.train_list:
            if train.id == train_id:
                print(f"Preparing to remove Train {train_id}")
                
                # Disconnect signals
                train.controller.delete_train.disconnect(self.handle_train_removed)
                self.test_signal.disconnect(train.controller.handle_fault_update)

                # Remove the train
                self.train_list.remove(train)
                print(f"Train {train_id} removed. Train List Length: {len(self.train_list)}")
                return
        raise ValueError(f"Train {train_id} not found in the train list")
    

    ##### TRACK MODEL HANDLERS #####

    @pyqtSlot(int, str, str)
    def handle_MBO_update(self, train_id: int, authority: str, commanded_speed: str):
        for train in self.train_list:
            if train.id == train_id:
                train.controller.train_model.decode_commanded_speed(commanded_speed)
                train.controller.train_model.decode_authority(authority)
                return
            
    ##### TRACK MODEL HANDLERS #####

    @pyqtSlot(int, float, Authority, float, int)
    def handle_CTC_update(self, train_id: int, commanded_speed: float, authority: Authority, grade: float, temp: int):
        for train in self.train_list:
            if train.id == train_id:
                train.controller.train_model.set_commanded_speed(commanded_speed)
                train.controller.train_model.grade = grade
                train.controller.train_model.outdoor_temp = temp
                train.controller.train_model.set_authority(authority)
                return
            
    @pyqtSlot(int, int)
    def handle_passenger_update(self, train_id: int, passengers: int):
        for train in self.train_list:
            if train.id == train_id:
                train.controller.train_model.set_passengers(passengers)
                return
    

    def self_deletion_run(self):
        print(f"Train List Length: {len(manager.train_list)}")
        self.train_list[0].to_yard_run()
        while len(manager.train_list) > 0:
            print(f"Current Block: {self.train_list[0].controller.track_block.number}, Destination: {self.train_list[0].controller.destination}")
            print(f"Position: {self.train_list[0].controller.position}, Loop Length: {self.train_list[0].controller.loop_length}")
            self.train_list[0].controller.update_train_controller()
        print(f"Train List Length should be 0 and position should not have reset")
        print(f"Train List Length: {len(manager.train_list)}")

    def multiple_window_run(self):
        print("!!!!!!!!!!!! FIRST TRAIN DISPATCHED !!!!!!!!!!!!")
        manager.handle_dispatch(1, "green")
        print("!!!!!!!!!!!! SECOND TRAIN DISPATCHED !!!!!!!!!!!!")
        manager.handle_dispatch(2, "green")
        print("!!!!!!!!!!!! THIRD TRAIN DISPATCHED !!!!!!!!!!!!")
        manager.handle_dispatch(3, "green")
        print("!!!!!!!!!!!! FOURTH TRAIN DISPATCHED !!!!!!!!!!!!")


    def multiple_windows_and_trains_run(self):
        manager.handle_dispatch(1, "green")
        manager.handle_dispatch(2, "green")
        manager.handle_dispatch(3, "green")

        for i in range(4):
            manager.train_list[i].controller.set_setpoint_speed(20)
        for i in range(4):
            manager.train_list[i].controller.update_authority(Authority(1000000000,65))
            print(f"Power Command: {manager.train_list[i].controller.engine.power_command}, Current Speed: {manager.train_list[i].controller.current_speed}, Position: {manager.train_list[i].controller.position}")

if __name__ == "__main__":
    # train_system = TrainModelController(HOST, PORT, USERNAME, PASSWORD)
    time_keeper = TimeKeeper()
    time_keeper.start_timer()
    manager = TrainManager(time_keeper)

    # manager.engineer_table[0].set_engineer(25, 0.5) # Software
    manager.engineer_table[1].set_engineer(30, 0.5) # Hardware
    manager.handle_dispatch(1, "green")

    # manager.multiple_window_run()
    # manager.multiple_windows_and_trains_run()

    # manager.train_list[0].small_run()
    # manager.train_list[0].long_run()
    # manager.train_list[0].past_yard_run()
    # manager.train_list[0].to_yard_run()
    # manager.train_list[0].destination_run()
    # manager.train_list[0].service_brake_run()
    # manager.train_list[0].emergency_brake_run()
    # manager.train_list[0].emergency_run()
    # manager.train_list[0].commanded_speed_run()
    # manager.train_list[0].switch_modes_run()
    # manager.train_list[0].fault_run()
    # manager.train_list[0].signal_fault_run()
    # manager.train_list[0].ac_run()

    # manager.self_deletion_run()
    