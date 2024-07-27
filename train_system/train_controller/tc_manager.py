from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from train_system.train_controller.train_controller import TrainController
from train_system.train_model.train_model import TrainModel
from train_system.train_controller.engineer import Engineer

HOST= '192.168.0.114'
PORT = 22
USERNAME = 'danim'
PASSWORD = 'danim'

def handle_train_dispatched(self, train_id, line):
    if train_id % 2:
        Train(train_id, line, HOST, PORT, USERNAME, PASSWORD)

class Train:
    def __init__(self, host=None, port=None, username=None, password=None):
        self.train_model = TrainModel()
        self.ssh_client = None
        if(host and port and username and password):
            self.ssh_client = self.create_ssh_connection(HOST, PORT, USERNAME, PASSWORD)
        # Hardware
        # self.controller = TrainController(25, 0.1, self.train_model, self.ssh_client)
        # Software
        self.controller = TrainController(25, 0.1, self.train_model)

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


    def run(self):
        self.controller.set_setpoint_speed(30)
        for _ in range(50):
            self.controller.update_train_controller()

        self.controller.set_position(65)

        self.controller.set_setpoint_speed(30)
        for _ in range(50):
            self.controller.update_train_controller()
        
        # self.controller.set_setpoint_speed(30)
        # for _ in range(50):
        #     self.controller.update_train_controller()
        
        # self.controller.set_setpoint_speed(10)
        # for _ in range(50):
        #     self.controller.update_train_controller()
            

if __name__ == "__main__":
    # train_system = TrainSystem(HOST, PORT, USERNAME, PASSWORD)
    train_system = TrainSystem()
    train_system.run()