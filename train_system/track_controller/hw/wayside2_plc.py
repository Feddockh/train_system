#train_system/track_controller/sw_plc.py

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
#PLC Code for Wayside 2

#Wayside 2 is in charge of switch 58 to yard or track 63, yard to 63, block 76 to 77 and 76 to 101. 
#switch 58 is going to look at the track occupancy of 63. If occupied it will go to ayrd
#switch from yard is going to look at the 
#Determining switch position

#switch from 58 to yard
if(track_blocks[62].occupancy == True 
   or track_blocks[63].occupancy == True 
   or track_blocks[64].occupancy == True
   or track_blocks[65].occupancy == True
   or track_blocks[66].occupancy == True):
    
    track_blocks[57].switch_position = 1
    track_blocks[57]._light_signal = True #Light is GREEN

    print("Switch from 58 to yard is connected, all trains going into yard")
else:
    track_blocks[57].switch_position = 0
    track_blocks[57]._light_signal = False #Light is RED
    print("Switch from 58 to yard is not connected, all trains are continuing along section J ")


#switch from yard to 63
if(track_blocks[58].occupancy == True 
   or track_blocks[59].occupancy == True 
   or track_blocks[60].occupancy == True
   or track_blocks[61].occupancy == True):

    track_blocks[62].switch_position = 0 #zero if section J is occupied, trains must stay in the yard
    track_blocks[62]._light_signal = False #switch is not connected, so light is RED
    print("Switch from yard is open, Trains cannot leave yard, Trains must wait for section J to be unoccupied")

else:
    track_blocks[62].switch_position = 1 #Trains can leave the yard
    track_blocks[62]._light_signal = True #Light is Green
    print("Switch from yard to Block 63 is open, Trains can leave the yard")


#switch from 76 - 77 and 76 to 101
if(track_blocks[76].occupancy == True 
   or track_blocks[77].occupancy == True 
   or track_blocks[78].occupancy == True 
   or track_blocks[79].occupancy == True
   or track_blocks[80].occupancy == True
   or track_blocks[81].occupancy == True
   or track_blocks[82].occupancy == True
   or track_blocks[83].occupancy == True
   or track_blocks[84].occupancy == True):
    
    track_blocks[75].switch_position = 0
    track_blocks[75]._light_signal = False #Signal at 75 is red because the train must now turn around instead of heading straight
    print("Switch from 76 to 101 is connected")
else:
    track_blocks[75].switch_position = 1
    track_blocks[75]._light_signal = True #Light Signal is Green, train can continue straigth
    print("Switch from 76 to 77 is connected")

