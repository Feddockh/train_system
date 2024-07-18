print("Wayside 1: ")

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


#



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

#SWITCH 29 Print statements
print("Switch 29 Information:\n")
# Block 29
print("Block 29 Information: ")
print(f"Switch Position: {track_blocks[28]._switch_position}")
print(f"Light Signal: {track_blocks[28]._light_signal}")
print(f"Authority: {track_blocks[28].authority}")

# Block 30
print("Block 30 Information: ")
print(f"Light Signal: {track_blocks[29]._light_signal}")
print(f"Authority: {track_blocks[29].authority}\n")

# Block 150
print("Block 150 Information: ")
print(f"Light Signal: {track_blocks[149]._light_signal}")
print(f"Authority: {track_blocks[149].authority}\n")
