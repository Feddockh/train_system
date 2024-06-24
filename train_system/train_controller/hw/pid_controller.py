class TrainController:
    def __init__(self, kp, ki, t, p_max):
        self.kp = kp # Proportional gain
        self.ki = ki # Integral gain
        self.t = t # Sample period
        self.p_max = p_max # Maximum power

        self.u = 0 # Power command
        self.e_total = 0 # Error integral
        self.u_total = 0 # Power integral
    
    # Compute the power command based on the current speed and the setpoint
    # Returns the power command to be applied to the train
    def compute_power_command(self, setpoint: float, current_speed: float):
        e = setpoint - current_speed
        p_cmd = self.kp * e + self.ki * self.u
        
        if p_cmd < self.p_max:
            self.u = self.u_total + (self.t / 2) * (e + self.e_total)
        else:
            self.u = self.u_total
        
        self.e_total = e
        self.u_total = self.u
        
        return p_cmd
    
    # Simulate the train's response to the power command
    # This is a simple simulation and can be replaced with a more complex model if needed
    def simulate_train(self, power_command: float, current_speed: float):
        print(f"Current Speed: {round(current_speed, 1)}")
        if power_command > self.p_max:
            power_command = self.p_max
        elif power_command < -self.p_max:
            power_command = -self.p_max
        
        current_speed += power_command * self.t
        
        return current_speed

# Example usage
if __name__ == "__main__":
    # Initialize the train controller with kp, ki, sample period (T), and maximum power (P_max)
    kp = 20.0
    ki = 1.0
    T = 0.05  # Sample period
    P_max = 120  # Maximum power in KW
    
    controller = TrainController(kp, ki, T, P_max)
    
    setpoint_speed = 50  # Desired velocity
    current_speed = 0  # Initial speed of the train
    
    for _ in range(100):  # Simulate for 10 iterations
        power_command = controller.compute_power_command(setpoint_speed, current_speed)
        # print(f"Power Command: {power_command}")
        print(f"Current Speed: {round(current_speed, 1)}")
        
        # Simulate the train's response to the power command
        # This is a simple simulation and can be replaced with a more complex model if needed
        if power_command > P_max:
            power_command = P_max
        elif power_command < -P_max:
            power_command = -P_max
        
        current_speed += power_command * T  # Update current speed based on the power command
        

