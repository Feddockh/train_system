"""
Updating Switch Positions for Wayside 5
"""

#if empty - do whatever
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
    and track_blocks[29].occupancy == False):
    track_blocks[8]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[7]._plc_unsafe = False
    track_blocks[8]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[2]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False

# emergency stop - elif(Q & H.M-H.B)
elif(track_blocks[2].occupancy == True and 
    track_blocks[11].switch.get_child_index() == 0):
    track_blocks[2]._authority = 0
    track_blocks[2]._plc_unsafe = False

# emergency stop - elif(H.T & H-T)
elif(track_blocks[7].occupancy == True and
    track_blocks[8].switch.get_child_index() == 1):
    track_blocks[7]._authority = 0
    track_blocks[7]._plc_unsafe = False

# Train coming down
elif(track_blocks[7].occupancy == True and
    (track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False and 
    track_blocks[12].occupancy == False) and
    ((track_blocks[20].occupancy == False and 
    track_blocks[21].occupancy == False and
    track_blocks[22].occupancy == False) or (
    track_blocks[7].occupancy == True and
    track_blocks[0].occupancy == True and
    track_blocks[1].occupancy == True and 
    track_blocks[2].occupancy == True and
    track_blocks[3].occupancy == True and 
    track_blocks[4].occupancy == True and 
    track_blocks[5].occupancy == True and 
    track_blocks[6].occupancy == True))):
    track_blocks[8].switch.set_child_index(0)
    track_blocks[11].switch.set_child_index(0)
    track_blocks[8]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False

# Train Leaving
elif(track_blocks[2].occupancy == True and
    (track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False and 
    track_blocks[12].occupancy == False) and
    ((track_blocks[20].occupancy == True and 
    track_blocks[21].occupancy == True and
    track_blocks[22].occupancy == True) or (
    track_blocks[7].occupancy == False and
    track_blocks[0].occupancy == False and
    track_blocks[1].occupancy == False and 
    track_blocks[2].occupancy == False and
    track_blocks[3].occupancy == False and 
    track_blocks[4].occupancy == False and 
    track_blocks[5].occupancy == False and 
    track_blocks[6].occupancy == False))):
    track_blocks[8].switch.set_child_index(1)
    track_blocks[11].switch.set_child_index(1)
    track_blocks[8]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False

# Unsafe by PLC
elif(track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True or 
    track_blocks[12].occupancy == True):
    track_blocks[8]._plc_unsafe = True
    track_blocks[11]._plc_unsafe = True


"""
Light Signals for Wayside 5
"""
# emergency stop - elif(Q & H.M-H.B)
if(track_blocks[2].occupancy == True and 
    track_blocks[11].switch.get_child_index() == 0):
    track_blocks[2]._crossing_signal = False
    track_blocks[11]._crossing_signal = True
    track_blocks[12]._crossing_signal = False

    track_blocks[2]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False

# emergency stop - elif(H.T & H-T)
elif(track_blocks[7].occupancy == True and
    track_blocks[8].switch.get_child_index() == 1):
    track_blocks[7]._crossing_signal = False
    track_blocks[8]._crossing_signal = True
    track_blocks[3].crossing_signal = False

    track_blocks[7]._plc_unsafe = False
    track_blocks[8]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False

# Train coming down
elif(track_blocks[7].occupancy == True and
    (track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False and 
    track_blocks[12].occupancy == False) and
    ((track_blocks[20].occupancy == False and 
    track_blocks[21].occupancy == False and
    track_blocks[22].occupancy == False) or (
    track_blocks[7].occupancy == True and
    track_blocks[0].occupancy == True and
    track_blocks[1].occupancy == True and 
    track_blocks[2].occupancy == True and
    track_blocks[3].occupancy == True and 
    track_blocks[4].occupancy == True and 
    track_blocks[5].occupancy == True and 
    track_blocks[6].occupancy == True))):
    track_blocks[7]._crossing_signal = True
    track_blocks[8]._crossing_signal = False
    track_blocks[3]._crossing_signal = False
    track_blocks[2]._crossing_signal = True
    track_blocks[11]._crossing_signal = False
    track_blocks[12]._crossing_signal = False

    track_blocks[7]._plc_unsafe = False
    track_blocks[8]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[2]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False

# Train Leaving
elif(track_blocks[2].occupancy == True and
    (track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False and 
    track_blocks[12].occupancy == False) and
    ((track_blocks[20].occupancy == True and 
    track_blocks[21].occupancy == True and
    track_blocks[22].occupancy == True) or (
    track_blocks[7].occupancy == False and
    track_blocks[0].occupancy == False and
    track_blocks[1].occupancy == False and 
    track_blocks[2].occupancy == False and
    track_blocks[3].occupancy == False and 
    track_blocks[4].occupancy == False and 
    track_blocks[5].occupancy == False and 
    track_blocks[6].occupancy == False))):
    track_blocks[7]._crossing_signal = False
    track_blocks[8]._crossing_signal = False
    track_blocks[3]._crossing_signal = False
    track_blocks[2]._crossing_signal = True
    track_blocks[11]._crossing_signal = False
    track_blocks[12]._crossing_signal = True

    track_blocks[7]._plc_unsafe = False
    track_blocks[8]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[2]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False

# Unsafe by PLC
elif(track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True or 
    track_blocks[12].occupancy == True):
    track_blocks[7]._plc_unsafe = True
    track_blocks[8]._plc_unsafe = True
    track_blocks[3]._plc_unsafe = True
    track_blocks[2]._plc_unsafe = True
    track_blocks[11]._plc_unsafe = True
    track_blocks[12]._plc_unsafe = True