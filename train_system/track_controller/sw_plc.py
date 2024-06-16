#train_system/track_controller/sw_plc.py

class SWPLC:
    def __init__(self, new_track_occupancies):
        """
        Initialize values used in PLC program
        """
        self.track_occupancies = new_track_occupancies
        self.switch = False
        self.light = False
        self.crossing = False

def plc(self):
    """
    PLC program used to determine switch, crossing, and light state.
    Representing a scenario where one train is going to Station B and
    the other is going to Station C in that order. A crossing occurs at block 8.
    
    Returns:
        switch(bool): Bool representing switch position - 0 = connected 
        6 & 1 = connected to 11. 
        crossing(bool): Bool representing crossing state - 0 = up & 1 = down
        light(bool): Bool representing light state - 0 = green & 1 = red
    """
    
    #Determining light status
    if (self.switch == False and self.track_occupancies(6)):
        self.light = True
        print("Light is red.")
    elif (self.switch == False and self.track_occupancies(11)):
        self.light = True
        print("Light is red.")
    else:
        self.light = False
        print("Light is green.")
    
    #Determining switch position
    if (self.track_occupancies(6) or self.track_occupancies(7) or self.track_occupancies(8)
       or self.track_occupancies(9) or self.track_occupancies(10)):
        self.switch = 1
        print("Switch is connected to Block 6.")
    else:
        self.switch = 0
        print("Switch is connected to Block 11.")

    #Determing crossing signal
    if (self.track_occupancies(7) or self.track_occupancies(8) or self.track_occupancies(9)):
        cross = 1
        print("Crossing Signal is down.")
    else:
        cross = 0
        print("Crossing Signal is up.")
    


        