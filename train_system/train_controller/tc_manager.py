import paramiko

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from train_system.train_controller.train_controller import TrainSystem
from train_system.train_controller.engineer import Engineer

HOST= '192.168.0.114'
PORT = 22
USERNAME = 'danim'
PASSWORD = 'danim'

class TrainManager:
    def __init__(self):
        self.ssh_client = None
        self.engineer_table: list[Engineer] = [Engineer()] * 100
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
    def handle_dispatch(self, train_id: int = "1", line: str = "green"):
        if train_id % 2:
            # Add hardware train to the train list
            self.train_list.append(TrainSystem(self.engineer_table[train_id], line, train_id, self.ssh_client))
            ##### ADD CONNECTIONS TO THE TRAIN SYSTEM #####
        else:
            # Add software train to the train list
            self.train_list.append(TrainSystem(self.engineer_table[train_id], line, train_id))
            ##### ADD CONNECTIONS TO THE TRAIN SYSTEM #####

    def handle_train_removed(self, train_id: int):
        for train in self.train_list:
            if train.id == train_id:
                #### DO WHATEVER NECESSARY BEFORE REMOVING TRAIN ####
                self.train_list.remove(train)
                return
        print("No Train found with ID: " + str(train_id))

if __name__ == "__main__":
    # train_system = TrainSystem(HOST, PORT, USERNAME, PASSWORD)
    manager = TrainManager()
    manager.engineer_table[0].set_engineer(5000, 1)
    manager.handle_dispatch(0, "green")
    manager.train_list[0].small_run()