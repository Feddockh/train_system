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
    and track_blocks[26].occupancy == False):
    print("")

# if (M.lastBlock & (N-R OR N-Q)) // emergency stop
elif track_blocks[2].occupancy == True and track_blocks[3].switch_position == 1:
    track_blocks[3].switch_position = 0
    track_blocks[11].switch_position = 0
    track_blocks[3].authority = 0 # UNSAFE
    print("Unsafe")
elif track_blocks[2].occupancy == True and track_blocks[11].switch_position == 1:
    track_blocks[3].switch_position = 0
    track_blocks[11].switch_position = 0
    track_blocks[11].authority = 0 # UNSAFE

#elif (M.lastBlock) // can update other blocks {switch1 = N-M & switch2 = N-0}
elif track_blocks[2].occupancy == True:
    track_blocks[3].switch_position = 0
    track_blocks[11].switch_position = 0

# elif (Loop.lastBlock & (N-O OR N-M)) // emergency stop
elif track_blocks[26].occupancy == True and track_blocks[3].switch_position == 0:
    track_blocks[3].authority = 0 # UNSAFE
    track_blocks[3].switch_position = 1
    track_blocks[11].switch_position = 1
elif track_blocks[26].occupancy == True and track_blocks[11].switch_position == 0:
    track_blocks[11].authority = 0 # UNSAFE
    track_blocks[3].switch_position = 1
    track_blocks[11].switch_position = 1

# elif (Loop.lastBlock) // can update other blocks {switch2 = N-Q & N-M}
elif track_blocks[26].occupancy == True:
    track_blocks[3].switch_position = 1
    track_blocks[11].switch_position = 1

# elif (N): // no switches can be changed while in N
elif (track_blocks[3].occupancy == True or
      track_blocks[4].occupancy == True or
      track_blocks[5].occupancy == True or
      track_blocks[6].occupancy == True or
      track_blocks[7].occupancy == True or
      track_blocks[8].occupancy == True or 
      track_blocks[9].occupancy == True or
      track_blocks[10].occupancy == True or
      track_blocks[11].occupancy == True):
    track_blocks[3].authority = 0 # UNSAFE
    track_blocks[11].authority = 0 # UNSAFE


"""
Updating Light Signals
"""
# if (N-M & R = Green)
if track_blocks[3].switch_position == 0 and track_blocks[27]._light_signal == True:
    track_blocks[27].authority = 0 # UNSAFE

# elif (N-R & M = Green)
elif track_blocks[3].switch_position == 1 and track_blocks[2]._light_signal == True:
    track_blocks[2].authority = 0 # UNSAFE

# elif (N-O & G == Green)
elif track_blocks[11].switch_position == 0 and track_blocks[26]._light_signal == True:
    track_blocks[26].authority = 0 # UNSAFE

# elif (N-Q & O == Green)
elif track_blocks[11].switch_position == 0 and track_blocks[12]._light_signal == True:
    track_blocks[12].authority = 0 # UNSAFE


elif(track_blocks[3].switch_position == 0
    and track_blocks[2].occupancy == True and
    track_blocks[2]._light_signal == False):
    track_blocks[2].authority = 0

elif(track_blocks[3].switch_position == 0
    and track_blocks[2].occupancy == True and
    track_blocks[3]._light_signal == False):
    track_blocks[3].authority = 0

elif(track_blocks[3].switch_position == 0
    and track_blocks[2].occupancy == True and
    track_blocks[27]._light_signal == False):
    track_blocks[27].authority = 0

elif(track_blocks[3].switch_position == 0
    and track_blocks[2].occupancy == True and
    track_blocks[11]._light_signal == False):
    track_blocks[11].authority = 0

elif(track_blocks[3].switch_position == 0
    and track_blocks[2].occupancy == True and
    track_blocks[12]._light_signal == False):
    track_blocks[12].authority = 0

elif(track_blocks[3].switch_position == 0
    and track_blocks[2].occupancy == True and
    track_blocks[26]._light_signal == False):
    track_blocks[26].authority = 0

# elif (N-M & M.lastBlock)
elif (track_blocks[3].switch_position == 0 and
    track_blocks[2].occupancy == True):
    track_blocks[2]._light_signal = True
    track_blocks[3]._light_signal = False
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = False
    
elif (track_blocks[11].switch_position == 0 and 
    track_blocks[26].occupancy == True and 
    track_blocks[2]._light_signal == False):
    track_blocks[2].authority = 0

elif (track_blocks[11].switch_position == 0 and 
    track_blocks[26].occupancy == True and 
    track_blocks[3]._light_signal == False):
    track_blocks[3].authority = 0

elif (track_blocks[11].switch_position == 0 and 
    track_blocks[26].occupancy == True and 
    track_blocks[27]._light_signal == False):
    track_blocks[27].authority = 0

elif (track_blocks[11].switch_position == 0 and 
    track_blocks[26].occupancy == True and 
    track_blocks[11]._light_signal == False):
    track_blocks[11].authority = 0

elif (track_blocks[11].switch_position == 0 and 
    track_blocks[26].occupancy == True and 
    track_blocks[12]._light_signal == False):
    track_blocks[12].authority = 0

elif (track_blocks[11].switch_position == 0 and 
    track_blocks[26].occupancy == True and 
    track_blocks[26]._light_signal == False):
    track_blocks[26].authority = 0

#elif (N-Q & Loop.last block)
elif (track_blocks[11].switch_position == 0 and 
    track_blocks[26].occupancy == True):
    track_blocks[2]._light_signal = False
    track_blocks[3]._light_signal = True
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = True


elif(track_blocks[3].switch_position == 1
    and track_blocks[2].occupancy == True and
    track_blocks[2]._light_signal == True):
    track_blocks[2].authority = 0

elif(track_blocks[3].switch_position == 1
    and track_blocks[2].occupancy == True and
    track_blocks[3]._light_signal == True):
    track_blocks[3].authority = 0

elif(track_blocks[3].switch_position == 1
    and track_blocks[2].occupancy == True and
    track_blocks[27]._light_signal == True):
    track_blocks[27].authority = 0

elif(track_blocks[3].switch_position == 1
    and track_blocks[2].occupancy == True and
    track_blocks[11]._light_signal == True):
    track_blocks[11].authority = 0

elif(track_blocks[3].switch_position == 1
    and track_blocks[2].occupancy == True and
    track_blocks[12]._light_signal == True):
    track_blocks[12].authority = 0

elif(track_blocks[3].switch_position == 1
    and track_blocks[2].occupancy == True and
    track_blocks[26]._light_signal == True):
    track_blocks[26].authority = 0

# elif (N-M & M.lastBlock)
elif (track_blocks[3].switch_position == 1 and
    track_blocks[2].occupancy == True):
    track_blocks[2]._light_signal = True
    track_blocks[3]._light_signal = False
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = False
    
elif (track_blocks[11].switch_position == 1 and 
    track_blocks[26].occupancy == True and 
    track_blocks[2]._light_signal == True):
    track_blocks[2].authority = 0

elif (track_blocks[11].switch_position == 1 and 
    track_blocks[26].occupancy == True and 
    track_blocks[3]._light_signal == False):
    track_blocks[3].authority = 0

elif (track_blocks[11].switch_position == 1 and 
    track_blocks[26].occupancy == True and 
    track_blocks[27]._light_signal == True):
    track_blocks[27].authority = 0

elif (track_blocks[11].switch_position == 1 and 
    track_blocks[26].occupancy == True and 
    track_blocks[11]._light_signal == True):
    track_blocks[11].authority = 0

elif (track_blocks[11].switch_position == 1 and 
    track_blocks[26].occupancy == True and 
    track_blocks[12]._light_signal == True):
    track_blocks[12].authority = 0

elif (track_blocks[11].switch_position == 1 and 
    track_blocks[26].occupancy == True and 
    track_blocks[26]._light_signal == False):
    track_blocks[26].authority = 0

#elif (N-Q & Loop.last block)
elif (track_blocks[11].switch_position == 1 and 
    track_blocks[26].occupancy == True):
    track_blocks[2]._light_signal = False
    track_blocks[3]._light_signal = True
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = True
    
# elif (N): // no switches can be changed while in N
elif (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True):
    #UNSAFE
    track_blocks[2].authority = 0
    track_blocks[3].authority = 0
    track_blocks[27].authority = 0
    track_blocks[11].authority = 0
    track_blocks[12].authority = 0
    track_blocks[26].authority = 0