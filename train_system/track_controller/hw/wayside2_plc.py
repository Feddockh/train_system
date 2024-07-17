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
#switch 58 is going to look at the track occupancy of 63. If occupied it will go to yard
#Determining switch position

#switch from 58 to yard
if (track_blocks[62].occupancy 
    or track_blocks[63].occupancy 
    or track_blocks[64].occupancy
    or track_blocks[65].occupancy
    or track_blocks[66].occupancy
    or track_blocks[58].occupancy
    or track_blocks[59].occupancy
    or track_blocks[60].occupancy
    or track_blocks[61].occupancy): 
    
    #setting switch position
    track_blocks[57].switch_position = 1

    #setting light signals
    track_blocks[56]._light_signal = True  # Light is Green leading up to the switch
    track_blocks[57]._light_signal = True  # Light is GREEN light on block 58, is green. Showing that the switch to the yard is connected
    track_blocks[58]._light_signal = False # Light at the beginning of section J is RED showing that the train will not continue on the green line

    #print to terminal/ for error checking
    print("Switch from 58 to yard is connected, all trains going into yard")

#emergency stop instance
elif ((track_blocks[62].occupancy 
       or track_blocks[63].occupancy 
       or track_blocks[64].occupancy
       or track_blocks[65].occupancy
       or track_blocks[66].occupancy  # checks if anything from section J till K is occupied, if so authority set to zero
       or track_blocks[58].occupancy
       or track_blocks[59].occupancy
       or track_blocks[60].occupancy
       or track_blocks[61].occupancy)
      and track_blocks[57].occupancy): # checks if the switch at 58 is occupied

    #set authority to zero because it's an emergency
    track_blocks[57].authority = 0 

    #setting light colors
    track_blocks[56]._light_signal = False # RED because all paths are occupied
    track_blocks[57]._light_signal = False # RED because all paths are occupied
    track_blocks[58]._light_signal = False # RED because all paths are occupied

    #print to terminal to error check
    print("EMERGENCY STOP TRAINS AT BLOCK 57")

else:
    #setting switch positions
    track_blocks[57].switch_position = 0

    #setting light colors
    track_blocks[56]._light_signal = True  # This light will typically be green unless a collision on J
    track_blocks[57]._light_signal = False # Light is RED because 58 is the path to yard and is not going to yard
    track_blocks[58]._light_signal = True  # Light is Green and headed towards section J

    #print to terminal to error check
    print("Switch from 58 to yard is not connected, all trains are continuing along section J")


#switch from yard to 63
if (track_blocks[58].occupancy 
    or track_blocks[59].occupancy 
    or track_blocks[60].occupancy # checks the block occupancies of block J,K,L, and M 
    or track_blocks[61].occupancy # which are the pieces of track that connects right to block 63
    or track_blocks[62].occupancy # 62 block indices block 63
    or track_blocks[63].occupancy
    or track_blocks[64].occupancy
    or track_blocks[65].occupancy
    or track_blocks[66].occupancy
    or track_blocks[67].occupancy
    or track_blocks[68].occupancy
    or track_blocks[69].occupancy
    or track_blocks[70].occupancy
    or track_blocks[71].occupancy
    or track_blocks[72].occupancy
    or track_blocks[73].occupancy
    or track_blocks[74].occupancy):

    #setting switch position

    track_blocks[62].switch_position = 0 # zero if section J is occupied, trains must stay in the yard
    track_blocks[62].authority = 0
    #setting light color
    track_blocks[62]._light_signal = False # switch is not connected, so light is RED

    #print to terminal to error check
    print("Switch from yard is open, Trains cannot leave yard, Trains must wait for section J to be unoccupied")

else:
    #setting switch position
    track_blocks[62].switch_position = 1 # Trains can leave the yard

    #setting light color
    track_blocks[62]._light_signal = True # Light is Green

    #print to terminal to error check
    print("Switch from yard to Block 63 is open, Trains can leave the yard")


#switch from 76 - 77 and 76 to 101
if (track_blocks[76].occupancy 
    or track_blocks[77].occupancy 
    or track_blocks[78].occupancy 
    or track_blocks[79].occupancy
    or track_blocks[80].occupancy
    or track_blocks[81].occupancy
    or track_blocks[82].occupancy
    or track_blocks[83].occupancy
    or track_blocks[84].occupancy): # I want to add an AND here to AND it will 101 and make sure it and other blocks are unoccupied
    
    #set switch_position
    track_blocks[75].switch_position = 0

    #set the light signals
    track_blocks[75]._light_signal = True  # Signal at 75 is Green because it is still safe to enter the switch block
    track_blocks[76]._light_signal = False # Signal at 77 is Red because the switch is not connected to 77
    track_blocks[100]._light_signal = True # Signal at 101 is Green because the switch is safely connected to 101 

    #Print to terminal to error check and make sure 
    print("Switch from 76 to 101 is connected")

#else that checks T, U, V, W, X, Y, Z
elif (track_blocks[100].occupancy or
      track_blocks[101].occupancy or
      track_blocks[102].occupancy or
      track_blocks[103].occupancy or
      track_blocks[104].occupancy or
      track_blocks[105].occupancy or
      track_blocks[106].occupancy or
      track_blocks[107].occupancy or
      track_blocks[108].occupancy or
      track_blocks[109].occupancy or
      track_blocks[110].occupancy or
      track_blocks[111].occupancy or
      track_blocks[112].occupancy or
      track_blocks[113].occupancy or
      track_blocks[114].occupancy or
      track_blocks[115].occupancy or
      track_blocks[116].occupancy or
      track_blocks[117].occupancy or
      track_blocks[118].occupancy or
      track_blocks[119].occupancy or
      track_blocks[120].occupancy or
      track_blocks[121].occupancy or
      track_blocks[122].occupancy or
      track_blocks[123].occupancy or
      track_blocks[124].occupancy or
      track_blocks[125].occupancy or
      track_blocks[126].occupancy or
      track_blocks[127].occupancy or
      track_blocks[128].occupancy or
      track_blocks[129].occupancy or
      track_blocks[130].occupancy or
      track_blocks[131].occupancy or
      track_blocks[132].occupancy or
      track_blocks[133].occupancy or
      track_blocks[134].occupancy or
      track_blocks[135].occupancy or
      track_blocks[136].occupancy or
      track_blocks[137].occupancy or
      track_blocks[138].occupancy or
      track_blocks[139].occupancy or
      track_blocks[140].occupancy or
      track_blocks[141].occupancy or
      track_blocks[142].occupancy or
      track_blocks[143].occupancy or
      track_blocks[144].occupancy or
      track_blocks[145].occupancy or
      track_blocks[146].occupancy or
      track_blocks[147].occupancy or  
      track_blocks[148].occupancy or
      track_blocks[149].occupancy):

    #set switch position
    track_blocks[75].switch_position = 1

    #set light colors
    track_blocks[76]._light_signal = True  # Light signal is Green, Train will continue straight
    track_blocks[75]._light_signal = True  # Light Signal is Green, train can continue straight
    track_blocks[100]._light_signal = False # Light to blue 101 is RED
    print("Switch from 76 to 77 is connected")

elif ((track_blocks[76].occupancy 
       or track_blocks[77].occupancy 
       or track_blocks[78].occupancy 
       or track_blocks[79].occupancy
       or track_blocks[80].occupancy
       or track_blocks[81].occupancy
       or track_blocks[82].occupancy
       or track_blocks[83].occupancy
       or track_blocks[84].occupancy)
      and (track_blocks[100].occupancy or
           track_blocks[101].occupancy or
           track_blocks[102].occupancy or
           track_blocks[103].occupancy or
           track_blocks[104].occupancy or
           track_blocks[105].occupancy or
           track_blocks[106].occupancy or
           track_blocks[107].occupancy or
           track_blocks[108].occupancy or
           track_blocks[109].occupancy or
           track_blocks[110].occupancy or
           track_blocks[111].occupancy or
           track_blocks[112].occupancy or
           track_blocks[113].occupancy or
           track_blocks[114].occupancy or
           track_blocks[115].occupancy or
           track_blocks[116].occupancy or
           track_blocks[117].occupancy or
           track_blocks[118].occupancy or
           track_blocks[119].occupancy or
           track_blocks[120].occupancy or
           track_blocks[121].occupancy or
           track_blocks[122].occupancy or
           track_blocks[123].occupancy or
           track_blocks[124].occupancy or
           track_blocks[125].occupancy or
           track_blocks[126].occupancy or
           track_blocks[127].occupancy or
           track_blocks[128].occupancy or
           track_blocks[129].occupancy or
           track_blocks[130].occupancy or
           track_blocks[131].occupancy or
           track_blocks[132].occupancy or
           track_blocks[133].occupancy or
           track_blocks[134].occupancy or
           track_blocks[135].occupancy or
           track_blocks[136].occupancy or
           track_blocks[137].occupancy or
           track_blocks[138].occupancy or
           track_blocks[139].occupancy or
           track_blocks[140].occupancy or
           track_blocks[141].occupancy or
           track_blocks[142].occupancy or
           track_blocks[143].occupancy or
           track_blocks[144].occupancy or
           track_blocks[145].occupancy or
           track_blocks[146].occupancy or
           track_blocks[147].occupancy or  
           track_blocks[148].occupancy or
           track_blocks[149].occupancy)):

    track_blocks[76]._light_signal = False #Red emergency
    track_blocks[75]._light_signal = False #Red emergency
    track_blocks[100]._light_signal = False #Red emergency

    track_blocks[75].authority = 0 #emergency so authority set to 0
    #Print to terminal to error check
    print("EMERGENCY STOP, TRAIN HAS NO WHERE TO GO AT BLOCK 76")
