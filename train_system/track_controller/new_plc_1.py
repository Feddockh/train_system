"""
Updating Switch Positions
"""

# if empty - can do anything
if (track_blocks[0].occupancy == False
    and track_blocks[1].occupancy == False
    and track_blocks[2].occupancy == False
    and track_blocks[3].occupancy == False
    and track_blocks[4].occupancy == False
    and track_blocks[5].occupancy == False
    and track_blocks[6].occupancy == False
    and track_blocks[7].occupancy == False
    and track_blocks[8].occupancy == False
    and track_blocks[9].occupancy == False
    and track_blocks[10].occupancy == False
    and track_blocks[11].occupancy == False
    and track_blocks[12].occupancy == False
    and track_blocks[13].occupancy == False
    and track_blocks[14].occupancy == False
    and track_blocks[15].occupancy == False
    and track_blocks[16].occupancy == False
    and track_blocks[17].occupancy == False
    and track_blocks[18].occupancy == False
    and track_blocks[19].occupancy == False
    and track_blocks[20].occupancy == False
    and track_blocks[21].occupancy == False
    and track_blocks[22].occupancy == False
    and track_blocks[23].occupancy == False
    and track_blocks[24].occupancy == False
    and track_blocks[25].occupancy == False
    and track_blocks[26].occupancy == False
    and track_blocks[27].occupancy == False
    and track_blocks[28].occupancy == False
    and track_blocks[29].occupancy == False
    and track_blocks[30].occupancy == False
    and track_blocks[31].occupancy == False
    and track_blocks[32].occupancy == False):
    print("")

# if (Z.lastBlock & (F-G OR D-A)) // emergency stop
elif track_blocks[32].occupancy == True and track_blocks[28].switch_position == 1:
    track_blocks[28].switch_position = 0
    track_blocks[12].switch_position = 0
    track_blocks[28].authority = 0 # UNSAFE
    print("Unsafe")
elif track_blocks[32].occupancy == True and track_blocks[12].switch_position == 1:
    track_blocks[28].switch_position = 0
    track_blocks[12].switch_position = 0
    track_blocks[12].authority = 0 # UNSAFE

#elif (Z.lastBlock) // can update other blocks {switch1 = N-M & switch2 = N-0}
elif track_blocks[32].occupancy == True:
    track_blocks[12].switch_position = 0
    track_blocks[28].switch_position = 0

# elif (Loop.lastBlock & (D-C OR F-Z)) // emergency stop
elif track_blocks[0].occupancy == True and track_blocks[28].switch_position == 0:
    track_blocks[28].authority = 0 # UNSAFE
    track_blocks[12].switch_position = 1
    track_blocks[28].switch_position = 1
elif track_blocks[0].occupancy == True and track_blocks[12].switch_position == 0:
    track_blocks[12].authority = 0 # UNSAFE
    track_blocks[28].switch_position = 1
    track_blocks[12].switch_position = 1

# elif (Loop.lastBlock) // can update other blocks {switch2 = N-Q & N-M}
elif track_blocks[0].occupancy == True:
    track_blocks[12].switch_position = 1
    track_blocks[28].switch_position = 1

# elif (D-E-F): // no switches can be changed while in N
elif (track_blocks[12].occupancy == True
    or track_blocks[13].occupancy == True
    or track_blocks[14].occupancy == True
    or track_blocks[15].occupancy == True
    or track_blocks[16].occupancy == True
    or track_blocks[17].occupancy == True
    or track_blocks[18].occupancy == True
    or track_blocks[19].occupancy == True
    or track_blocks[20].occupancy == True
    or track_blocks[21].occupancy == True
    or track_blocks[22].occupancy == True
    or track_blocks[23].occupancy == True
    or track_blocks[24].occupancy == True
    or track_blocks[25].occupancy == True
    or track_blocks[26].occupancy == True
    or track_blocks[27].occupancy == True):
    track_blocks[12].authority = 0 # UNSAFE
    track_blocks[28].authority = 0 # UNSAFE


"""
Updating Light Signals
"""
# if (G-F & Z = Green)
if track_blocks[28].switch_position == 0 and track_blocks[32]._light_signal == True:
    track_blocks[32].authority = 0 # UNSAFE

# elif (Z-G & F = Green)
elif track_blocks[28].switch_position == 1 and track_blocks[29]._light_signal == True:
    track_blocks[29].authority = 0 # UNSAFE

# elif (D-C & A == Green)
elif track_blocks[12].switch_position == 1 and track_blocks[0]._light_signal == True:
    track_blocks[0].authority = 0 # UNSAFE

# elif (D-A & C == Green)
elif track_blocks[12].switch_position == 0 and track_blocks[11]._light_signal == True:
    track_blocks[11].authority = 0 # UNSAFE


elif(track_blocks[28].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[32]._light_signal == False):
    track_blocks[32].authority = 0

elif(track_blocks[28].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[29]._light_signal == False):
    track_blocks[29].authority = 0

elif(track_blocks[28].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[28]._light_signal == False):
    track_blocks[28].authority = 0

elif(track_blocks[28].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[12]._light_signal == False):
    track_blocks[12].authority = 0

elif(track_blocks[28].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[0]._light_signal == False):
    track_blocks[0].authority = 0

elif(track_blocks[28].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[11]._light_signal == False):
    track_blocks[11].authority = 0

# elif (Z-F & Z.lastBlock)
elif (track_blocks[28].switch_position == 1 and
    track_blocks[32].occupancy == True):
    track_blocks[32]._light_signal = True
    track_blocks[29]._light_signal = False
    track_blocks[28]._light_signal = False
    track_blocks[12]._light_signal = True
    track_blocks[0]._light_signal = False
    track_blocks[11]._light_signal = False
    
elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[32]._light_signal == False):
    track_blocks[32].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[29]._light_signal == False):
    track_blocks[29].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[28]._light_signal == False):
    track_blocks[28].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[12]._light_signal == False):
    track_blocks[12].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[11]._light_signal == False):
    track_blocks[11].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[26]._light_signal == False):
    track_blocks[0].authority = 0

#elif (D-A & Loop.last block)
elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True):
    track_blocks[32]._light_signal = False
    track_blocks[29]._light_signal = True
    track_blocks[28]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[11]._light_signal = False
    track_blocks[0]._light_signal = True


elif(track_blocks[32].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[2]._light_signal == True):
    track_blocks[2].authority = 0

elif(track_blocks[29].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[0]._light_signal == True):
    track_blocks[0].authority = 0

elif(track_blocks[29].switch_position == 1
    and track_blocks[30].occupancy == True and
    track_blocks[12]._light_signal == True):
    track_blocks[12].authority = 0

elif(track_blocks[29].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[28]._light_signal == True):
    track_blocks[28].authority = 0

elif(track_blocks[29].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[32]._light_signal == True):
    track_blocks[32].authority = 0

elif(track_blocks[29].switch_position == 1
    and track_blocks[32].occupancy == True and
    track_blocks[29]._light_signal == True):
    track_blocks[29].authority = 0

# elif (Z-F & Z.lastBlock)
elif (track_blocks[29].switch_position == 1 and
    track_blocks[2].occupancy == True):
    track_blocks[0]._light_signal = True
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[28]._light_signal = True
    track_blocks[32]._light_signal = False
    track_blocks[29]._light_signal = False
    
elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[2]._light_signal == True):
    track_blocks[2].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[12]._light_signal == False):
    track_blocks[12].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[11]._light_signal == True):
    track_blocks[11].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[32]._light_signal == True):
    track_blocks[32].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[29]._light_signal == True):
    track_blocks[29].authority = 0

elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True and 
    track_blocks[28]._light_signal == False):
    track_blocks[28].authority = 0

#elif (D-A & Loop.last block)
elif (track_blocks[12].switch_position == 0 and 
    track_blocks[0].occupancy == True):
    track_blocks[12]._light_signal = False
    track_blocks[0]._light_signal = True
    track_blocks[11]._light_signal = False
    track_blocks[32]._light_signal = False
    track_blocks[29]._light_signal = False
    track_blocks[28]._light_signal = True
    
# elif (D-E-F): // no switches can be changed while in N
elif (track_blocks[12].occupancy == True
    or track_blocks[13].occupancy == True
    or track_blocks[14].occupancy == True
    or track_blocks[15].occupancy == True
    or track_blocks[16].occupancy == True
    or track_blocks[17].occupancy == True
    or track_blocks[18].occupancy == True
    or track_blocks[19].occupancy == True
    or track_blocks[20].occupancy == True
    or track_blocks[21].occupancy == True
    or track_blocks[22].occupancy == True
    or track_blocks[23].occupancy == True
    or track_blocks[24].occupancy == True
    or track_blocks[25].occupancy == True
    or track_blocks[26].occupancy == True
    or track_blocks[27].occupancy == True):
    #UNSAFE
    track_blocks[12].authority = 0
    track_blocks[0].authority = 0
    track_blocks[11].authority = 0
    track_blocks[32].authority = 0
    track_blocks[29].authority = 0
    track_blocks[28].authority = 0
   
if(track_blocks[17].occupancy == True or track_blocks[18].occupancy == True or track_blocks[19].occupancy == True and track_blocks[18]._crossing_signal_bool == False):
    track_blocks[18].authority = 0

elif(track_blocks[17].occupancy == True or track_blocks[18].occupancy == True or track_blocks[19].occupancy == True and track_blocks[18]._crossing_signal_bool == True):
    print()

elif(track_blocks[17].occupancy == True or track_blocks[18].occupancy == True or track_blocks[19].occupancy == True):
    track_blocks[18]._crossing_signal_bool = True
else: 
    track_blocks[18]._crossing_signal_bool = False