print("Wayside 1: ")
"""
POST INDEX CHANGE
"""
#Scenario 1: 1-->13, block 1 = OCCUPIED, D through F are unoccupied
if(track_blocks[0].occupancy and track_blocks[12].occupancy == False and (track_blocks[13].occupancy == False and track_blocks[14].occupancy == False and track_blocks[15].occupancy == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and track_blocks[27].occupancy == False and track_blocks[28].occupancy == False)):
    
    #set switch position
    track_blocks[12].switch.position = track_blocks[12].switch.child_blocks[0]
    #track_blocks[12].switch.child_blocks[0]

    #set lights
    track_blocks[0]._light_signal = True
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False

#Scenario 2: 13-->12, block 13 is occupied, A is unoccupied
if(track_blocks[12].occupancy and track_blocks[0].occupancy == False and track_blocks[11].occupancy == False):

    #set switch position
    track_blocks[12].switch.position = track_blocks[12].switch.child_blocks[1]
    #track_blocks[12].switch.child_blocks[11]

    #set lights
    track_blocks[0]._light_signal = False
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = True

#Scenario 3: 13-->12, block 13 is occupied, 1 is occupied, load loop, until D through F is unoccupied, then send through train
if(track_blocks[12].occupancy and track_blocks[0].occupancy and track_blocks[11].occupancy == False):
    
    #set authority at 1 to 0
    track_blocks[0].authority = 0

    #set switch position
    track_blocks[12].switch.position = track_blocks[12].switch.child_blocks[1]
    #track_blocks[12].switch.child_blocks[11]

    #set ligths
    track_blocks[0]._light_signal = False
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = True

#CROSSING SIGNAL
if(track_blocks[19].occupancy or track_blocks[18].occupancy or track_blocks[17].occupancy):

    #set crossing signal 
    track_blocks[18]._crossing_signal = True

    print("Crossing Signal: Down\n")

if(track_blocks[19].occupancy == False and track_blocks[18].occupancy == False and track_blocks[17].occupancy == False):

    #set crossing signal
    track_blocks[18]._crossing_signal = False

    print("Crossing Signal: Up\nPedestrians May Cross\n")




#SWITCH AT BLOCK 29

#Scenario 1: 29-> 30, block 150 is not occupied
if(track_blocks[28].occupancy and track_blocks[32].occupancy == False and track_blocks[29].occupancy == False):
    
    #set switch position
    track_blocks[28].switch.position = track_blocks[28].switch.child_blocks[0]
    #track_blocks[28].switch.child_blocks[29]

    #set lights
    track_blocks[28]._light_signal = True
    track_blocks[29]._light_signal = True
    track_blocks[32]._light_signal = False

#Scenario 2: 29-> 30, block 150 is occupied, set authority to zero at 150
if(track_blocks[28].occupancy and track_blocks[32].occupancy and track_blocks[29].occupancy == False):

    #set authority at 150 to zero
    track_blocks[32].authority = 0

    #set switch position
    track_blocks[28].switch.position = track_blocks[28].switch.child_blocks[0]
    #track_blocks[28].switch.child_blocks[29]

    #set lights
    track_blocks[28]._light_signal = True
    track_blocks[29]._light_signal = True
    track_blocks[32]._light_signal = False

#Scenario 3: 150 -> 29, blocks 13 through 29 are unoccupied
if(track_blocks[32].occupancy and (track_blocks[12].occupancy == False and track_blocks[13].occupancy == False and track_blocks[14].occupancy == False and track_blocks[15].occupancy == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False
                                    and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and track_blocks[27].occupancy == False and track_blocks[28].occupancy == False)):
    
    #set switch pos
    track_blocks[28].switch.position = track_blocks[28].switch.child_blocks[1]
    #track_blocks[28].switch.child_blocks[32]

    #set lights
    track_blocks[28]._light_signal = False
    track_blocks[32]._light_signal = True
    #track_blocks[29]._light_signal = False



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
print(f"Switch Position: {track_blocks[12].switch.position}")
print(f"Light Signal: {track_blocks[12]._light_signal}")
print(f"Authority: {track_blocks[12].authority}\n")

# Block 29 (Switch)
print("Block 29 (Switch) Information: ")
print(f"Switch Position: {track_blocks[28].switch.position}")
print(f"Light Signal: {track_blocks[28]._light_signal}")
print(f"Authority: {track_blocks[28].authority}\n")

#block 30
print("Block 30 Information: ")
print(f"Light Signal: {track_blocks[29]._light_signal}")
print(f"Authority: {track_blocks[29].authority}\n")

#block 150
print("Block 150 Information: ")
print(f"Light Signal: {track_blocks[32]._light_signal}")
print(f"Authority: {track_blocks[32].authority}\n")









"""
PRE INDEX CHANGE 
"""
"""
#Updated Wayside 1 as of 7/25/2024

#switch at block 13

#Scenario 1: 1-->13, block 1 = OCCUPIED, D through F are unoccupied
# if true, switch position is 1-->13
if(track_blocks[1].occupancy and track_blocks[13].occupancy == False and (track_blocks[14].occupancy == False and track_blocks[15].occupany == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and track_blocks[27].occupancy == False and track_blocks[28].occupancy == False and track_blocks[29].occupancy == False)):

    #set switch position
    track_blocks[13].switch_position = 0

    #set lights
    track_blocks[1]._light_signal = True
    track_blocks[12]._light_signal = False
    track_blocks[13]._light_signal = True

#Scenario 2: 13-->12, block 13 is occupied, A is unoccupied
if(track_blocks[13].occupancy and track_block[1].occupancy == False and track_blocks[12].occupancy == False):

    #set switch position
    track_blocks[13].switch_position = 1

    #set lights
    track_blocks[1]._light_signal = False
    track_blocks[12]._light_signal = True
    track_blocks[13]._light_signal = True

#Scenario 3: 13-->12, block 13 is occupied, 1 is occupied, load loop, until D through F is unoccupied, then send through train
if(track_blocks[13].occupancy and track_blocks[1].occupancy and track_blocks[12].occupancy == False):
    
    #set authority at 1 to 0
    track_blocks[1].authority = 0

    #set switch position
    track_blocks[13].switch_position = 1

    #set ligths
    track_blocks[1]._light_signal = False
    track_blocks[12]._light_signal = True
    track_blocks[13]._light_signal = True



#SWITCH AT BLOCK 29

#Scenario 1: 29-> 30, block 150 is not occupied
if(track_blocks[29].occupancy and track_blocks[150].occupancy == False and track_blocks[30].occupancy == False):
    
    #set switch position
    track_blocks[29].switch_position = 0

    #set lights
    track_blocks[29]._light_signal = True
    track_blocks[30]._light_signal = True
    track_blocks[150]._light_signal = False

#Scenario 2: 29-> 30, block 150 is occupied, set authority to zero at 150
if(track_blocks[29].occupancy and track_blocks[150].occupancy and track_blocks[30].occupancy == False):

    #set authority at 150 to zero
    track_blocks[150].authority = 0

    #set switch position
    track_blocks[29].switch_position = 0

    #set lights
    track_blocks[29]._light_signal = True
    track_blocks[30]._light_signal = True
    track_blocks[150]._light_signal = False

 
#Scenario 3: 150 -> 29, blocks 13 through 29 are unoccupied
if(track_blocks[150].occupancy and (track_blocks[13].occupancy == False and track_blocks[14].occupancy == False and track_blocks[15].occupancy == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False
                                    and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy and track_blocks[27].occupancy and track_blocks[28].occupancy and track_blocks[29].occupancy)):
    
    #set switch pos
    track_blocks[29].switch_position = 1

    #set lights
    track_blocks[29]._light_signal = True
    track_blocks[150]._light_signal = True
    track_blocks[30]._light_signal = False



# Consolidated print statements for error checking
print("Switch 13 Information:\n")
# Block 1
print("Block 1 Information: ")
print(f"Light Signal: {track_blocks[1]._light_signal}")
print(f"Authority: {track_blocks[1].authority}")

# Block 12
print("Block 12 Information: ")
print(f"Light Signal: {track_blocks[12]._light_signal}")
print(f"Authority: {track_blocks[12].authority}\n")

# Block 13 (Switch)
print("Block 13 (Switch) Information: ")
print(f"Switch Position: {track_blocks[13]._switch_position}")
print(f"Light Signal: {track_blocks[13]._light_signal}")
print(f"Authority: {track_blocks[13].authority}\n")

# Block 29 (Switch)
print("Block 29 (Switch) Information: ")
print(f"Switch Position: {track_blocks[29]._switch_position}")
print(f"Light Signal: {track_blocks[29]._light_signal}")
print(f"Authority: {track_blocks[29].authority}\n")

#block 30
print("Block 30 Information: ")
print(f"Light Signal: {track_blocks[30]._light_signal}")
print(f"Authority: {track_blocks[30].authority}\n")

#block 150
print("Block 150 Information: ")
print(f"Light Signal: {track_blocks[150]._light_signal}")
print(f"Authority: {track_blocks[150].authority}\n")
"""