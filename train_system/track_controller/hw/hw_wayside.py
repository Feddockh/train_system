#train_system/track_controller/hw_wayside.py
import paramiko

class HWWayside:
    # INITIALIZE
    def __init__(self, track_occupancies, authority, hostname, port, username, password):
        """
        Initialize all variables
        """
        # initialize all variables
        self.authority = authority
        self.track_occupancies = track_occupancies
        self.switch_position = False

        self.switch_block9 = False #switch for leaving the yard
        self.switch_block16 = False #switch at the intersection of blocks AFE
        self.switch_block27 = False #switch at the intersection of blocks H and T
        
        self.message_switch1 = ''
        self.message_switch2 = ''
        self.message_switch3 = ''

        self.light_block9 = False  # 0 = green, 1 = red
        self.light_block16 = False
        self.light_block27 = False
        self.crossing_signal = False

        self.color_block9 = ''
        self.color_block16 = ''
        self.color_block27 = ''

        self.switchpos = ''
        self.crossingsig = ''

        # for the raspberry pi config
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        self.plc()

    # PLC
    def plc(self):
        """
        This is a PLC program intended to determine the switch states, Light signals, and crossing signals.
        There are 5 scenarios that this PLC simulates
    Returns:
        switch_position(bool): Bool representing the track switch positions
        crossing_signal(bool): Bool representing the Crossing State
        light_StationB(bool): Bool representing light signal for the track headed towards StationB
        light_StationC(bool): Bool representing light signal for the track headed towards StationC
    """
        #self.crossing_signals()
        self.switch_positions()
        self.convert_to_strings()
        self.light_signals()
        self.display_output()
        
        #self.send_to_pi()

    def switch_positions(self):
        #call switch at blocks 9, 16, and 27
        self.switch_block9 = self.switch_from_yard()
        self.switch_block16 = self.switch_1()
        self.switch_block27 = self.switch_2()
    
    def crossing_signals(self):
        # Determing crossing signal / gate
        if (self.track_occupancies[2] or self.track_occupancies[3] or self.track_occupancies[4]):
            self.crossing_signal = True
        else:
            self.crossing_signal = False

        return self.crossing_signal

    def emergency_authority(self):
        # emergency authority for if both tracks are zero
        self.authority = 0
        return self.authority

    def light_signals(self):
        
        if(self.switch_block9):
            self.light_block9 = False #if switch at block 9 is connected, light is green(false)
        else:
            self.light_block9 = True #if switch at block 9 is not connected, light is red(True)

        if(self.authority == 0):
            self.light_block9 = True
            self.light_block16 = True
            self.light_block27 = True

        # Check if path to station B is occupied

        return self.light_block9, self.light_block16, self.light_block27

    def convert_to_strings(self):
        
        #color of lightB
        if(self.light_block9):
            self.color_block9 = 'RED'
        
        else:
            self.color_block9 = 'GREEN'

        #color of lightC
        if(self.light_block16):
            self.color_block16 = 'RED'
        else:
            self.color_block16 = 'GREEN'

        if(self.light_block27):
            self.color_block27 = 'RED'
        else:
            self.color_block27 = 'GREEN'

        #convert crossing signal to text
        if(self.crossing_signal):
            self.crossingsig = 'DO NOT CROSS'
        else:
            self.crossingsig = 'PEDESTRIANS MAY CROSS'

        return self.color_block9, self.color_block16, self.color_block27, self.crossingsig

    def send_to_pi(self):
        # Initialize the SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the Raspberry Pi
            ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)

            
            # Prepare the command to be sent to Raspberry Pi
            command = ""
            
            #reset log
            command = "echo 'Log Reset' > /home/garrett/pi_monitor.log\n "
            command += "echo 'Running PLC Code' >>/home/garrett/pi_monitor.log\n"
            #testing only
            command += f"echo 'TESTING' >>/home/garrett/pi_monitor.log\n"
            #actual outputs on pi
            command += f"echo '{self.message_switch1}' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.message_switch2}' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.message_switch3}' >> /home/garrett/pi_monitor.log\n"
            command += f"echo '{self.crossingsig}' >> /home/garrett/pi_monitor.log\n"
            
            # Execute the command
            stdin, stdout, stderr = ssh.exec_command(command)

            # Read the response
            response = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            #Print for debugging purposes
            print("Response: ", response)
            print("Error: ", error)

            # Check for errors
            if error:
                response += f"\nError: {error}"

        except Exception as e:
            response = str(e)

        finally:
            # Close the connection
            ssh.close()

        return response

    def display_output(self):
        #Check switch 1 and print direction of track
        if(self.switch_block9):
            self.message_switch1 = 'Switch 1 Status: connected\ntrains can leave the yard'
            print(self.message_switch1)
            print(self.color_block9)
            print("\n")
        else:
            self.message_switch1 = 'Switch 1 Status: disconnected\nTrack Occupied, Trains must wait till clear'
            print(self.message_switch1)
            print(self.color_block9)
            print("\n")

        if(self.switch_block16):
            self.message_switch2 = 'Switch 2 Status: Connecting block 1 to 16\nTrain can return to yard'
            print(self.message_switch2)
            print(self.color_block16)
            print("\n")
        else:
            self.message_switch2 = 'Switch 2 Status: Connecting block 15 to 16\nTrain must go back through loop'
            print(self.message_switch2)
            print(self.color_block16)
            print("\n")

        if(self.switch_block27):
            self.message_switch3 = 'Switch 3 Status: Connecting Block 27 to 76\nTrain turns'
            print(self.message_switch3)
            print(self.color_block27)
            print("\n")
        
        else:
            self.message_switch3 = 'Switch 3 Status: Connecting Block 27 to 28\nTrain continues straight'
            print(self.message_switch3)
            print(self.color_block27)
            print("\n")

#Wayside 4 code

    def switch_from_yard(self):

        """
        Using OR gates, this function ORs together all track occupancies from 1 through 9, and returns a bool that represents the switch position 0 = open, 1 closed

        Returns:
            switch_position(bool)
        """


        # Determining switch position for going to and from the yard, checks blocks 1 -> 9, if occupied, switch = 0, therefore it is not connect, if occupied, authority is set to zero which tells the train to not move. 
        if(self.track_occupancies[1] or self.track_occupancies[2] or self.track_occupancies[3]
            or self.track_occupancies[4] or self.track_occupancies[5] or self.track_occupancies[6] or self.track_occupancies[7] or self.track_occupancies[8]
            or self.track_occupancies[9]):
            self.emergency_authority()
            self.switch_position = False

        #if unoccupied, switch conencts, and train can continue
        else:
            self.switch_position = True

        return self.switch_position

    def switch_1(self):
        """
        Looks at all occupancies for the switch at the intersection of blocks 1->16 vs 1->15, switch 1

        Returns:
            switch position(bool)
        """
    

        #checks if A->C are occupied, and E->D are unoccupied, if so then switch_position = false, connects blocks 15->16 (F and E)
        if any(self.track_occupancies[i] for i in range(1, 10)) and not any(self.track_occupancies[i] for i in range(10, 14)):
            self.switch_position = False

        #checks if A->C are unoccupied, and E->D are occupied, if so then switch_position = true, connects blocks 1->16 (F and A)
        elif any(self.track_occupancies[i] for i in range(10, 15)) and not any(self.track_occupancies[i] for i in range(1, 9)):
            self.switch_position = True
        
        #checks if A -> H are all occupied up till the switch 2, if occupied, emergency stop all trains. 
        elif any(self.track_occupancies[i] for i in range(1, 10)) and any(self.track_occupancies[i] for i in range(10, 27)):
            self.emergency_authority()
            print("STOP ALL TRAINS")
    
        return self.switch_position

    def switch_2(self):
        """
        Checks blocks H, T, S, R and. Switch position = 0 to remain straight through H, and 1 to open up to the T
        """

        if any(self.track_occupancies[i] for i in range(73, 76)) and not any(self.track_occupancies[i] for i in range(27, 33)):
            self.switch_position = True

        elif any(self.track_occupancies[i] for i in range(27, 33)) and not any(self.track_occupancies[i] for i in range(73, 76)):
            self.switch_position = False
        
        #emergency check
        elif any(self.track_occupancies[i] for i in range(27, 33)) and all(self.track_occupancies[i] for i in range(73,76)):
            self.emergency_authority()
    
        return self.switch_position
