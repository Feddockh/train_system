



#switch from 76 - 77 and 76 to 101
#looks at Block N if occupied, switches to 101
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
    track_blocks[75]._switch_position = 0

    #set track block 77 authority to 0 so that if occupied on that train, it will stop, and therefore won't drive into an open track, if coming from that direction
    track_block[76].authority = 0

    #set the light signals
    track_blocks[75]._light_signal = True  # Signal at 75 is Green because it is still safe to enter the switch block
    track_blocks[76]._light_signal = False # Signal at 77 is Red because the switch is not connected to 77
    track_blocks[100]._light_signal = True # Signal at 101 is Green because the switch is safely connected to 101 

    #Print to terminal to error check and make sure 
    print("Switch from 76 to 101 is connected")

#else that checks T, U, V, W, X, Y, Z. 
#if there are any occupancies int hese sections, the train connects to block 76
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
    track_blocks[75]._switch_position = 1

    #set block authority for 101 so that if there is a train at 101 it'll stop until the track connects.
    track_blocks[100].authority = 0

    #set light colors
    track_blocks[76]._light_signal = True  # Light signal is Green, Train will continue straight
    track_blocks[75]._light_signal = True  # Light Signal is Green, train can continue straight
    track_blocks[100]._light_signal = False # Light to blue 101 is RED
    print("Switch from 76 to 77 is connected")

#if sections N R S T U V W X Y Z have any occupancies a the same time, the trains must emergency stop
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

    #make all authorities around the switch 0, so the train doesn't continue driving in a 3 way occupied intersection of track
    #EMERGENCY
    track_blocks[75].authority = 0 
    track_blocks[76].authority = 0
    track_blocks[100].authority = 0
    
    #Print to terminal to error check
    print("EMERGENCY STOP, TRAIN HAS NO WHERE TO GO AT BLOCK 76")


"""
#switch from 76 - 77 and 76 to 101
if(track_blocks[76]._occupancy == True 
   or track_blocks[77]._occupancy == True 
   or track_blocks[78]._occupancy == True 
   or track_blocks[79]._occupancy == True
   or track_blocks[80]._occupancy == True
   or track_blocks[81]._occupancy == True
   or track_blocks[82]._occupancy == True
   or track_blocks[83]._occupancy == True
   or track_blocks[84]._occupancy == True):
    
    track_blocks[75]._switch_position = 0

    #authority
    track_blocks[100].authority = track_blocks[100].authority
    track_blocks[75].authority = track_blocks[100].authority
    track_blocks[76].authority = 1

    #set light colors

    track_blocks[75]._light_signal = True #Signal at 75 is red because the train must now turn around instead of heading straight
    track_blcoks[76]._light_signal = False
    track_blocks[100]._light_signal = True
    print("Switch from 76 to 101 is connected")
else:
    track_blocks[75]._switch_position = 0
        #authority
    track_blocks[100].authority = 0
    track_blocks[75].authority = track_blocks[75].authority
    track_blocks[76].authority = track_blocks[76].authority

    #set light colors
    
    track_blocks[76]._light_signal = True
    track_blocks[100]._light_signal = False
    track_blocks[75]._light_signal = True #Light Signal is Green, train can continue straigth
    print("Switch from 76 to 77 is connected")
    """