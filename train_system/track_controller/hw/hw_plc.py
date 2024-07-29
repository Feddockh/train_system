#train_system/track_controller/hw_plc.py

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

#Determining switch position
if (track_occupancies[5] or track_occupancies[6] or track_occupancies[7]
    or track_occupancies[8] or track_occupancies[9]):
    switch = True
    print("Switch is connected to Block 11.")
else:
    switch = False
    print("Switch is connected to Block 6.")

#Determing crossing signal
if (track_occupancies[6] or track_occupancies[7] or track_occupancies[8]):
    cross = True
    print("Crossing Signal is down.")
else:
    cross = False
    print("Crossing Signal is up.")

#Determining light status
if (switch == False and track_occupancies[5] and track_occupancies[4]):
    light = True
    print("Light is red.")
elif (switch == True and track_occupancies[10] and track_occupancies[4]):
    light = True
    print("Light is red.")
else:
    light = False
    print("Light is green.")
   