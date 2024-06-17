class TrainController:
    def __init__(self, train_model):
        self.engineer = self.Engineer()
        self.brake = self.Brake()
        self.engine = self.Engine()
        self.doors = self.Doors(train_model)
        self.lights = self.Lights(train_model)
        self.ac = self.AC(train_model)

        self.driver_mode = "manual"
        self.setpoint_speed = 0

        self.current_speed = None
        self.commanded_speed = None
        self.authority = None
        self.position = None
        self.train_temp = None
        self.faults = None

        self.update_train_model(train_model)

    def update_train_model(self, train_model):
        self.current_speed = train_model.get_current_speed()
        self.commanded_speed = train_model.get_commanded_speed()
        self.authority = train_model.get_authority()
        self.position = train_model.get_position()
        self.train_temp = train_model.get_train_temp()
        self.faults = train_model.get_fault_statuses()
        self.doors.update_status(train_model)
        self.lights.update_status(train_model)
        self.ac.update_current_temp(train_model)

    def set_driver_mode(self, mode: str):
        if mode not in ["automatic", "manual"]:
            raise ValueError("Invalid mode. Mode must be 'automatic' or 'manual'.")
        self.driver_mode = mode

    def get_driver_mode(self):
        return self.driver_mode

    def toggle_driver_mode(self):
        self.driver_mode = "automatic" if self.driver_mode == "manual" else "manual"

    def set_setpoint_speed(self, speed: float):
        self.setpoint_speed = speed

    def get_setpoint_speed(self):
        return self.setpoint_speed

    def get_commanded_speed(self):
        return self.commanded_speed

    def update_commanded_speed(self, train_model):
        self.commanded_speed = train_model.get_commanded_speed()

    def get_desired_speed(self):
        return self.setpoint_speed if self.driver_mode == "manual" else self.commanded_speed

    def get_power_command(self):
        return self.engine.compute_power_command(self.get_desired_speed(), self.current_speed, self.engineer)

    # Simulate the train's response to desired speeds
    ## Purely for debugging purposes
    def simulate_speed(self, speed: float):
        for _ in range(10):
            power_command = self.engine.compute_power_command(speed, self.current_speed, self.engineer)
            self.current_speed = self.engine.calculate_current_speed(power_command, self.current_speed)
            print(f"Power Command: {power_command}, Current Speed: {self.current_speed}")

    class Engineer:
        def __init__(self, kp=25, ki=0.5):
            self.kp = kp
            self.ki = ki

        def set_kp(self, kp: float):
            if kp > 0:
                self.kp = kp
            else:
                raise ValueError("kp must be positive")

        def set_ki(self, ki: float):
            if ki > 0:
                self.ki = ki
            else:
                raise ValueError("ki must be positive")

        def set_engineer(self, kp: float, ki: float):
            self.set_kp(kp)
            self.set_ki(ki)

        def get_kp(self):
            return self.kp

        def get_ki(self):
            return self.ki

        def get_engineer(self):
            return self.get_kp(), self.get_ki()

    class Brake:
        def __init__(self):
            self.service_brake = False
            self.emergency_brake = False

        def set_service_brake(self, status: bool):
            self.service_brake = status

        def set_emergency_brake(self, status: bool):
            self.emergency_brake = status

        def toggle_service_brake(self):
            self.service_brake = not self.service_brake

        def toggle_emergency_brake(self):
            self.emergency_brake = not self.emergency_brake

        def get_service_brake(self):
            return self.service_brake

        def get_emergency_brake(self):
            return self.emergency_brake

        def get_status(self):
            return self.service_brake or self.emergency_brake

    class Engine:
        def __init__(self):
            self.T = 0.05
            self.P_MAX = 120
            self.u_k = 0
            self.e_k_integral = 0
            self.u_k_integral = 0

        def compute_power_command(self, desired_speed: float, current_speed: float, engineer):
            kp, ki = engineer.get_engineer()
            e_k = desired_speed - current_speed
            p_cmd = kp * e_k + ki * self.u_k

            if p_cmd < self.P_MAX:
                self.u_k = self.u_k_integral + (self.T / 2) * (e_k + self.e_k_integral)
            else:
                self.u_k = self.u_k_integral

            self.e_k_integral = e_k
            self.u_k_integral = self.u_k

            return p_cmd

        def calculate_current_speed(self, power_command, current_speed):
            if power_command > self.P_MAX:
                power_command = self.P_MAX
            elif power_command < -self.P_MAX:
                power_command = -self.P_MAX

            current_speed += power_command * self.T
            return current_speed

    class Doors:
        def __init__(self, train_model):
            self.left = None
            self.right = None
            self.update_status(train_model)

        def set_left(self, status: bool):
            self.left = status

        def set_right(self, status: bool):
            self.right = status

        def toggle_left(self):
            self.left = not self.left

        def toggle_right(self):
            self.right = not self.right

        def get_left(self):
            return self.left

        def get_right(self):
            return self.right

        def get_status(self):
            return self.get_left(), self.get_right()

        def update_status(self, train_model):
            self.left = train_model.get_left_door()
            self.right = train_model.get_right_door()

    class Lights:
        def __init__(self, train_model):
            self.lights = None
            self.update_status(train_model)

        def set_lights(self, status: bool):
            self.lights = status

        def turn_on(self):
            self.lights = True

        def turn_off(self):
            self.lights = False

        def toggle_lights(self):
            self.lights = not self.lights

        def get_status(self):
            return self.lights

        def update_status(self, train_model):
            self.lights = train_model.get_lights()

        def update_lights(self, train_model):
            self.lights = not train_model.get_underground_status()

    class AC:
        def __init__(self, train_model):
            self.commanded_temp = 69
            self.current_temp = None
            self.update_current_temp(train_model)

        def set_commanded_temp(self, temp: int):
            self.commanded_temp = temp

        def update_current_temp(self, train_model):
            self.current_temp = train_model.get_train_temp()

        def get_commanded_temp(self):
            return self.commanded_temp

        def get_current_temp(self):
            return self.current_temp

class TrainModel:
    def get_current_speed(self):
        return 0  # Replace with actual logic

    def get_position(self):
        return 0  # Replace with actual logic

    def get_authority(self):
        return 0  # Replace with actual logic

    def get_commanded_speed(self):
        return 0  # Replace with actual logic

    def get_train_temp(self):
        return 0  # Replace with actual logic

    def get_station_name(self):
        return "Station"  # Replace with actual logic

    def get_underground_status(self):
        return False  # Replace with actual logic

    def get_exit_door(self):
        return False  # Replace with actual logic

    def get_fault_statuses(self):
        return [False] * 5  # Replace with actual logic

    def get_speed_limit(self):
        return 0  # Replace with actual logic

    def get_left_door(self):
        return False  # Replace with actual logic

    def get_right_door(self):
        return False  # Replace with actual logic

    def get_lights(self):
        return False  # Replace with actual logic

    def get_distance_traveled(self):
        return 0  # Replace with actual logic

class TrainSystem:
    def __init__(self):
        self.train_model = TrainModel()
        self.controller = TrainController(self.train_model)

    def run(self):
        self.controller.simulate_speed(30)
        self.controller.simulate_speed(50)
        self.controller.simulate_speed(70)
        self.controller.simulate_speed(10)

if __name__ == "__main__":
    train_system = TrainSystem()
    train_system.run()
