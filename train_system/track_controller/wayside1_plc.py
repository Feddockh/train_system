# Check if D -> G or A are occupied
if (track_blocks[12].occupancy 
    or track_blocks[13].occupancy
    or track_blocks[14].occupancy
    or track_blocks[15].occupancy
    or track_blocks[16].occupancy
    or track_blocks[17].occupancy
    or track_blocks[18].occupancy
    or track_blocks[19].occupancy
    or track_blocks[20].occupancy
    or track_blocks[21].occupancy
    or track_blocks[22].occupancy
    or track_blocks[23].occupancy
    or track_blocks[24].occupancy
    or track_blocks[25].occupancy
    or track_blocks[26].occupancy
    or track_blocks[27].occupancy
    or track_blocks[0].occupancy 
    or track_blocks[1].occupancy
    or track_blocks[2].occupancy
    or track_blocks[3].occupancy
    or track_blocks[4].occupancy
    or track_blocks[5].occupancy):

    # Set switch
    track_blocks[11]._switch_position = 1  # connects 12 to 13

    # Set authorities
    track_blocks[0].authority = 0
    track_blocks[11].authority = track_blocks[11].authority
    track_blocks[12].authority = track_blocks[12].authority
    
    # Set lights
    track_blocks[0]._light_signal = False  # RED, trains cannot leave yet
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = True  # Green light because nothing preventing it from being deemed unsafe

# Emergency stop if sections A -> F are occupied
elif (((track_blocks[12].occupancy 
    or track_blocks[13].occupancy
    or track_blocks[14].occupancy
    or track_blocks[15].occupancy
    or track_blocks[16].occupancy
    or track_blocks[17].occupancy
    or track_blocks[18].occupancy
    or track_blocks[19].occupancy
    or track_blocks[20].occupancy
    or track_blocks[21].occupancy
    or track_blocks[22].occupancy
    or track_blocks[23].occupancy
    or track_blocks[24].occupancy
    or track_blocks[25].occupancy
    or track_blocks[26].occupancy
    or track_blocks[27].occupancy)
    and (track_blocks[0].occupancy 
    or track_blocks[1].occupancy
    or track_blocks[2].occupancy
    or track_blocks[3].occupancy
    or track_blocks[4].occupancy
    or track_blocks[5].occupancy)
    and (track_blocks[6].occupancy 
    or track_blocks[7].occupancy
    or track_blocks[8].occupancy
    or track_blocks[9].occupancy
    or track_blocks[10].occupancy
    or track_blocks[11].occupancy))):

    # Set emergency authorities
    track_blocks[0].authority = 0 
    track_blocks[10].authority = 0
    track_blocks[11].authority = 0 

    # Set all lights to red
    track_blocks[0]._light_signal = False 
    track_blocks[10]._light_signal = False 
    track_blocks[11]._light_signal = False 

# Connecting 1 -> 13
else:
    # Default connection from A to D
    track_blocks[11]._switch_position = 0
    
    # Set authorities
    track_blocks[0].authority = track_blocks[0].authority 
    track_blocks[10].authority = 0
    track_blocks[11].authority = track_blocks[11].authority

    # Set lights
    track_blocks[0]._light_signal = True
    track_blocks[10]._light_signal = False
    track_blocks[11]._light_signal = True


#BLOCK 29 Switch

#Checks and makes sure that no
if((track_blocks[28].occupancy
    or track_blocks[29].occupancy
    or track_blocks[30].occupancy)
    and(track_blocks[11].occupancy 
    or track_blocks[12].occupancy
    or track_blocks[13].occupancy
    or track_blocks[14].occupancy
    or track_blocks[15].occupancy
    or track_blocks[16].occupancy
    or track_blocks[17].occupancy
    or track_blocks[18].occupancy
    or track_blocks[19].occupancy
    or track_blocks[20].occupancy
    or track_blocks[21].occupancy
    or track_blocks[22].occupancy
    or track_blocks[23].occupancy
    or track_blocks[24].occupancy
    or track_blocks[25].occupancy
    or track_blocks[26].occupancy
    or track_blocks[27].occupancy)):

    #set authority at 28 to zero
    track_blocks[27].authority = 0
    track_blocks[28].authority = 0
    track_blocks[32].authority = 0

    #set light colors
    track_blocks[27]._light_signal = False
    track_blocks[32]._light_signal = False
    track_blocks[28]._light_signal = False

if (track_blocks[28].occupancy == False
    or track_blocks[29].occupancy == False
    or track_blocks[30].occupancy == False):

    #set switch position
    track_blocks[27]._switch_position = 0 #connects to block 30

    track_blocks[27].authority = track_blocks[27].authority
    track_blocks[28].authority = track_blocks[28].authority
    track_blocks[32].authority = 0

    #set ligth colors
    track_blocks[27]._light_signal = True
    track_blocks[28]._light_signal = True
    track_blocks[32]._light_signal = False

elif(track_blocks[11].occupancy == False
    or track_blocks[12].occupancy == False
    or track_blocks[13].occupancy == False
    or track_blocks[14].occupancy == False
    or track_blocks[15].occupancy == False
    or track_blocks[16].occupancy == False
    or track_blocks[17].occupancy == False
    or track_blocks[18].occupancy == False
    or track_blocks[19].occupancy == False
    or track_blocks[20].occupancy== False
    or track_blocks[21].occupancy== False
    or track_blocks[22].occupancy== False
    or track_blocks[23].occupancy== False
    or track_blocks[24].occupancy== False
    or track_blocks[25].occupancy== False
    or track_blocks[26].occupancy== False
    or track_blocks[27].occupancy== False):

    #set switch position to 1 so it connects to 150
    track_block[27]._switch_position = 1

    #set authority at block 150 to zero
    track_block[27].authority = track_block[27].authority
    track_block[28].authority = 0
    track_block[32].authority = track_block[32].authority
    
    #set lights
    track_block[32]._light_signal = True
    track_block[27]._light_signal = True
    track_block[28]._light_signal = False
