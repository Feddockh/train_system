print("Wayside 1: ")




if(track_blocks[17].occupancy or track_blocks[16].occupancy or track_blocks[18]):
    track_blocks[17]._crossing_signal = False
else:
    track_blocks[17]._crossing_signal = True

# Check if D -> G or A are occupied
if (track_blocks[13].occupancy 
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
    or track_blocks[28].occupancy
    or track_blocks[0].occupancy 
    or track_blocks[1].occupancy
    or track_blocks[2].occupancy
    or track_blocks[3].occupancy
    or track_blocks[4].occupancy
    or track_blocks[5].occupancy):

    # Set switch
    track_blocks[12]._switch_position = 1  # connects 12 to 13

    # Set authorities
    track_blocks[0].authority = 0
    track_blocks[11].authority = track_blocks[11].authority
    track_blocks[12].authority = track_blocks[12].authority
    
    # Set lights
    track_blocks[0]._light_signal = False  # RED, trains cannot leave yet
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = True  # Green light because nothing preventing it from being deemed unsafe

# Emergency stop if sections A -> F are occupied
elif (((track_blocks[13].occupancy 
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
    or track_blocks[28].occupancy)
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
    track_blocks[11].authority = 0
    track_blocks[12].authority = 0 

    # Set all lights to red
    track_blocks[0]._light_signal = False 
    track_blocks[11]._light_signal = False 
    track_blocks[12]._light_signal = False 

# Connecting 1 -> 13
else:
    # Default connection from A to D
    track_blocks[12]._switch_position = 0
    
    # Set authorities
    track_blocks[0].authority = track_blocks[0].authority 
    track_blocks[11].authority = 0
    track_blocks[12].authority = track_blocks[12].authority

    # Set lights
    track_blocks[0]._light_signal = True
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = True


#BLOCK 29 Switch

#Checks and makes sure that no
if((track_blocks[29].occupancy
    or track_blocks[30].occupancy
    or track_blocks[31].occupancy
    or track_blocks[32].occupancy
    or track_blocks[33].occupancy
    or track_blocks[34].occupancy
    or track_blocks[35].occupancy
    or track_blocks[36].occupancy
    or track_blocks[37].occupancy
    or track_blocks[38].occupancy
    or track_blocks[39].occupancy
    or track_blocks[40].occupancy
    or track_blocks[41].occupancy
    or track_blocks[42].occupancy
    or track_blocks[43].occupancy
    or track_blocks[44].occupancy
    or track_blocks[45].occupancy
    or track_blocks[46].occupancy
    or track_blocks[47].occupancy
    or track_blocks[48].occupancy
    or track_blocks[49].occupancy
    or track_blocks[50].occupancy
    or track_blocks[51].occupancy
    or track_blocks[52].occupancy
    or track_blocks[53].occupancy
    or track_blocks[54].occupancy
    or track_blocks[55].occupancy
    or track_blocks[55].occupancy
    or track_blocks[57].occupancy) 
    and(track_blocks[12].occupancy 
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
    or track_blocks[28].occupancy)):

    #set authority at 28 to zero
    track_blocks[28].authority = 0
    track_blocks[29].authority = 0
    track_blocks[149].authority = 0

    #set light colors
    track_blocks[28]._light_signal = False
    track_blocks[149]._light_signal = False
    track_blocks[29]._light_signal = False

if not any([track_blocks[29].occupancy
    or track_blocks[30].occupancy
    or track_blocks[31].occupancy
    or track_blocks[32].occupancy
    or track_blocks[33].occupancy
    or track_blocks[34].occupancy
    or track_blocks[35].occupancy
    or track_blocks[36].occupancy
    or track_blocks[37].occupancy
    or track_blocks[38].occupancy
    or track_blocks[39].occupancy
    or track_blocks[40].occupancy
    or track_blocks[41].occupancy
    or track_blocks[42].occupancy
    or track_blocks[43].occupancy
    or track_blocks[44].occupancy
    or track_blocks[45].occupancy
    or track_blocks[46].occupancy
    or track_blocks[47].occupancy
    or track_blocks[48].occupancy
    or track_blocks[49].occupancy
    or track_blocks[50].occupancy
    or track_blocks[51].occupancy
    or track_blocks[52].occupancy
    or track_blocks[53].occupancy
    or track_blocks[54].occupancy
    or track_blocks[55].occupancy
    or track_blocks[56].occupancy
    or track_blocks[57].occupancy]):

    #set switch position
    track_blocks[28]._switch_position = 0 #connects to block 30

    track_blocks[28].authority = track_blocks[28].authority
    track_blocks[29].authority = track_blocks[29].authority
    track_blocks[149].authority = 0

    #set ligth colors
    track_blocks[28]._light_signal = True
    track_blocks[29]._light_signal = True
    track_blocks[149]._light_signal = False

elif(not any([track_blocks[12].occupancy 
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
    or track_blocks[28].occupancy])):

    #set switch position to 1 so it connects to 150
    track_block[28]._switch_position = 1

    #set authority at block 150 to zero
    track_block[28].authority = track_block[28].authority
    track_block[29].authority = 0
    track_block[149].authority = track_block[149].authority
    

    #set lights
    track_block[149]._light_signal = True
    track_block[28]._light_signal = True
    track_block[29]._light_signal = False

# Consolidated print statements for error checking
print("Switch 13 Information:\n")
# Block 1
print("Block 1 Information: ")
print(f"Light Signal: {track_blocks[0]._light_signal}")
print(f"Authority: {track_blocks[0].authority}")

# Block 12
print("Block 12 Information: ")
print(f"Light Signal: {track_blocks[11]._light_signal}")
print(f"Authority: {track_blocks[11].authority}\n")

# Block 13 (Switch)
print("Block 13 (Switch) Information: ")
print(f"Switch Position: {track_blocks[12]._switch_position}")
print(f"Light Signal: {track_blocks[12]._light_signal}")
print(f"Authority: {track_blocks[12].authority}\n")



# Block 29 (Switch)
print("Block 13 (Switch) Information: ")
print(f"Switch Position: {track_blocks[28]._switch_position}")
print(f"Light Signal: {track_blocks[28]._light_signal}")
print(f"Authority: {track_blocks[28].authority}\n")

#block 30
print("Block 30 Information: ")
print(f"Light Signal: {track_blocks[29]._light_signal}")
print(f"Authority: {track_blocks[29].authority}\n")

#block 150
print("Block 12 Information: ")
print(f"Light Signal: {track_blocks[149]._light_signal}")
print(f"Authority: {track_blocks[149].authority}\n")



