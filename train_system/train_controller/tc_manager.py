import paramiko

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from train_system.train_controller.train_controller import TrainSystem
from train_system.train_controller.engineer import Engineer

HOST= None  #'192.168.0.114'
PORT = 22
USERNAME = 'danim'
PASSWORD = 'danim'

class TrainManager(QObject):

    test_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.ssh_client = None
        self.engineer_table: list[Engineer] = [Engineer()] * 40
        self.train_list: list[TrainSystem] = []
        if(HOST and PORT and USERNAME and PASSWORD):
            self.ssh_client = self.create_ssh_connection(HOST, PORT, USERNAME, PASSWORD)

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
    def handle_dispatch(self, train_id: int = 1, line: str = "green"):
        if train_id % 2:
            # Add hardware train to the train list
            print("Hardware Train")
            self.train_list.append(TrainSystem(self.engineer_table[train_id], line, train_id, self.ssh_client))
        else:
            # Add software train to the train list
            print("Software Train")
            self.train_list.append(TrainSystem(self.engineer_table[train_id], line, train_id))
            
        ##### ADD CONNECTIONS TO THE TRAIN SYSTEM #####
        self.train_list[-1].controller.delete_train.connect(self.handle_train_removed)
        self.test_signal.connect(self.train_list[-1].controller.handle_fault_update)

    # When train reaches the yard, it removes itself from the train list
    #### NEED TO MANUALLY DELETE CONNECTIONS AS THE CONNECTIONS AREN'T DELETED WHEN TRAIN IS REMOVED ####
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

    def self_deletion_run(self):
        print(f"Train List Length: {len(manager.train_list)}")
        self.train_list[0].to_yard_run()
        while len(manager.train_list) > 0:
            print(f"Current Block: {self.train_list[0].controller.track_block.number}, Destination: {self.train_list[0].controller.destination}")
            print(f"Position: {self.train_list[0].controller.position}, Loop Length: {self.train_list[0].controller.loop_length}")
            self.train_list[0].controller.update_train_controller()
        print(f"Train List Length should be 0 and position should not have reset")
        print(f"Train List Length: {len(manager.train_list)}")

if __name__ == "__main__":
    # train_system = TrainSystem(HOST, PORT, USERNAME, PASSWORD)
    manager = TrainManager()
    manager.engineer_table[0].set_engineer(5000, 1)
    manager.handle_dispatch(0, "green")

    manager.self_deletion_run()

    # manager.train_list[0].small_run()
    # manager.train_list[0].long_run()
    # manager.train_list[0].full_loop_run()
    # manager.train_list[0].destination_run()
    # manager.train_list[0].service_run()
    # manager.train_list[0].emergency_run()
    # manager.train_list[0].commanded_speed_run()
    # manager.train_list[0].switch_modes_run()
    # manager.train_list[0].fault_run()
    # manager.train_list[0].ac_run()

    # manager.handle_train_removed(0)
    # print(f"Train List Length: {len(manager.train_list)}")
    