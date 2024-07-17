#track_blocks[0].authority = 0

#switch
if(track_blocks[0].occupancy == False and track_blocks[1].occupancy == False and track_blocks[2].occupancy == True):
    track_blocks[0].switch_position = 0
elif(track_blocks[0].occupancy == True and track_blocks[1].occupancy == True and track_blocks[2].occupancy == False):
    track_blocks[0].switch_position = 1
elif(track_blocks[0].occupancy == True and track_blocks[1].occupancy == True and track_blocks[2].occupancy == True and track_blocks[0].switch_position == 1):
    track_blocks[0].authority = 0 #EMERGENCY BRAKE

#light signal
if(track_blocks[0].occupancy == True and track_blocks[1].occupancy == True and track_blocks[2].occupancy == True and track_blocks[0]._light_signal == True):
    track_blocks[0].authority = 0 #EMERGENCY BRAKE
if(track_blocks[0].occupancy == True and track_blocks[1].occupancy == True and track_blocks[2].occupancy == True):
    track_blocks[0]._light_signal == False

#train entering the loop: N-M & N-O & (M | N)
if((track_blocks[74].occupancy == True
   or track_blocks[75].occupancy == True
   or track_blocks[76].occupancy == True) and 
   (track_blocks[77].occupancy == False
    or track_blocks[78].occupancy == False
    or track_blocks[79].occupancy == False
    or track_blocks[80].occupancy == False
    or track_blocks[81].occupancy == False
    or track_blocks[82].occupancy == False
    or track_blocks[83].occupancy == False
    or track_blocks[84].occupancy == False
    or track_blocks[85].occupancy == False) and 
    (track_block[77].switch_position == 0) and 
    (track_block[85].switch_position == 0)):
    track_block[77]._light_signal = True
    track_block[85]._light_signal = True

#train entering the loop: N-M & N-O & (M | N)
if((track_blocks[74].occupancy == False
   or track_blocks[75].occupancy == False
   or track_blocks[76].occupancy == False) and 
   (track_blocks[77].occupancy == True
    or track_blocks[78].occupancy == True
    or track_blocks[79].occupancy == True
    or track_blocks[80].occupancy == True
    or track_blocks[81].occupancy == True
    or track_blocks[82].occupancy == True
    or track_blocks[83].occupancy == True
    or track_blocks[84].occupancy == True
    or track_blocks[85].occupancy == True) and 
    (track_block[77].switch_position == 0) and 
    (track_block[85].switch_position == 0)):
    track_block[77]._light_signal = True
    track_block[85]._light_signal = True

#train in loop
if((track_blocks[74].occupancy == False
   or track_blocks[75].occupancy == False
   or track_blocks[76].occupancy == False) and 
   (track_blocks[77].occupancy == False
    or track_blocks[78].occupancy == False
    or track_blocks[79].occupancy == False
    or track_blocks[80].occupancy == False
    or track_blocks[81].occupancy == False
    or track_blocks[82].occupancy == False
    or track_blocks[83].occupancy == False
    or track_blocks[84].occupancy == False
    or track_blocks[85].occupancy == False) and 
    (track_blocks[86].occupancy == True
    or track_blocks[87].occupancy == True
    or track_blocks[88].occupancy == True
    or track_blocks[89].occupancy == True
    or track_blocks[90].occupancy == True
    or track_blocks[91].occupancy == True
    or track_blocks[92].occupancy == True
    or track_blocks[93].occupancy == True
    or track_blocks[94].occupancy == True
    or track_blocks[95].occupancy == True)
    or track_blocks[96].occupancy == True
    or track_blocks[97].occupancy == True
    or track_blocks[98].occupancy == True
    or track_blocks[99].occupancy == True
    or track_blocks[100].occupancy == True):





