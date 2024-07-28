#train_system/track_controller/wayside2_plc.py

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

"""
Post Index Change
"""
# Scenario 1: 57-->151, check if 58 is occupied, if so, go to yard
if (track_blocks[28].occupancy and  # block 57
    track_blocks[55].occupancy == False and  # block 151
    track_blocks[29].occupancy):  # block 58

    # set switch position
    track_blocks[28].switch_position = 1

    # set light colors
    #track_blocks[28]._light_signal = True
    track_blocks[29]._light_signal = False
    track_blocks[55]._light_signal = True

# Scenario 2: 57-->58, check if 151 is occupied, if so and 58 is not, go to 58, and continue on J
if (track_blocks[28].occupancy and  # block 57
    track_blocks[29].occupancy == False and  # block 58
    track_blocks[55].occupancy):  # block 151

    # set switch position
    track_blocks[28].switch_position = 0

    # set light colors
    #track_blocks[28]._light_signal = True
    track_blocks[29]._light_signal = True
    track_blocks[55]._light_signal = False

# Scenario 3: 57 58 and 151 are occupied, temporary stop
if (track_blocks[28].occupancy and  # block 57
    track_blocks[29].occupancy and  # block 58
    track_blocks[55].occupancy):  # block 151

    # set authority at 57 to zero, and wait for those blocks to become unoccupied
    track_blocks[28].authority = 0

    # set light signals 
    #track_blocks[28]._light_signal = False
    track_blocks[29]._light_signal = False
    track_blocks[55]._light_signal = False

# SWITCH AT BLOCK 63

# Scenario 1: 62 to 63, if block 62 is unoccupied, 
if (track_blocks[32].occupancy and  # block 62
    track_blocks[33].occupancy == False and  # block 63
    track_blocks[57].occupancy == False):  # block 153

    # set switch position
    track_blocks[33].switch_position = 0

    # set lights
    track_blocks[32]._light_signal = True
    #track_blocks[33]._light_signal = True
    track_blocks[57]._light_signal = False

# Scenario 2: 153 to 63, as long as none of block 62 is occupied and 63 is unoccupied
if (track_blocks[32].occupancy == False and  # block 62
    track_blocks[33].occupancy == False and  # block 63
    track_blocks[57].occupancy):  # block 153

    # set switch position
    track_blocks[33].switch_position = 1 

    # set light signals
    track_blocks[32]._light_signal = False
    #track_blocks[33]._light_signal = True
    track_blocks[57]._light_signal = True

# Scenario 3: 62, 63, 153 are all occupied, authority for 62 and 153 must turn red, then keep 63 green to allow
if (track_blocks[32].occupancy and  # block 62
    track_blocks[33].occupancy and  # block 63
    track_blocks[57].occupancy):  # block 153

    # set authorities of 62 and 153 to zero
    track_blocks[32].authority = 0
    track_blocks[57].authority = 0

    # set lights to red
    track_blocks[32]._light_signal = False
    #track_blocks[33]._light_signal = True
    track_blocks[57]._light_signal = False


# Consolidated print statements for error checking

#SWITCH AT BLOCK 57

print("Switch  57:\n")
# Block 57
print("Block 57 (Switch) Information: ")
print(f"Switch Position: {track_blocks[28]._switch_position}")
print(f"Light Signal: {track_blocks[28]._light_signal}")
print(f"Authority: {track_blocks[28].authority}\n")

# Block 58
print("Block 58 Information: ")
print(f"Light Signal: {track_blocks[29]._light_signal}")
print(f"Authority: {track_blocks[29].authority}\n")

# Block 151
print("Block 151 Information: ")
print(f"Light Signal: {track_blocks[55]._light_signal}")
print(f"Authority: {track_blocks[55].authority}\n")


#Switch at BLOCK 63
print("Switch 63: \n")
print("Block 63 (Switch) Information: ")
print(f"Switch Position: {track_blocks[33]._switch_position}")
print(f"Light Signal: {track_blocks[33]._light_signal}")
print(f"Authority: {track_blocks[33].authority}\n")

# Block 62
print("Block 62 Information: ")
print(f"Light Signal: {track_blocks[32]._light_signal}")
print(f"Authority: {track_blocks[32].authority}\n")

# Block 153
print("Block 153 Information: ")
print(f"Light Signal: {track_blocks[57]._light_signal}")
print(f"Authority: {track_blocks[57].authority}\n")





"""
Pre Index Change
"""
#updated wayside 2, July 24, 2024
#Switch 58

"""
#Scenario 1: 57-->151, check if 58 is occupied, if so, go to yard
if(track_blocks[57].occupancy and track_blocks[151].occupancy == False and track_blocks[58].occupancy):

    #set switch position
    track_blocks[57].switch_position = 1

    #set light colors
    track_blocks[57]._light_signal = True
    track_blocks[58]._light_signal = False
    track_blocks[151]._light_signal = True

#Scenario 2: 57-->58, check if 151 is occupied, if so and 58 is not, go to 58, and continue on J
if(track_blocks[57].occupancy and track_blocks[58].occupancy == False and track_blocks[151].occupancy):
    
    #set switch position
    track_blocks[57].switch_position = 0

    #set light colors
    track_blocks[57]._light_signal = True
    track_blocks[58]._light_signal = True
    track_blocks[151]._light_signal = False

#Scenario 3: 57 58 and 151 are occupied, temporary stop
if(track_blocks[57].occupancy and track_blocks[58].occupancy and track_blocks[151].occupancy):

    #set authority at 57 to zero, and wait for those blocks to become unoccupied
    track_blocks[57].authority = 0

    #set light signals 
    track_blocks[57]._light_signal = False
    track_blocks[58]._light_signal = False
    track_blocks[151]._light_signal = False

#SWITCH AT BLOCK 63

#Scenario 1: 62 to 63, if block 62 is unoccupied, 
if(track_blocks[62].occupancy and track_blocks[63].occupancy == False and track_blocks[153].occupancy == False):

    #set switch position
    track_blocks[63].switch_position = 0

    #set lights
    track_blocks[62]._light_signal = True
    track_blocks[63]._light_signal = True
    track_blocks[153]._light_signal = False

#Scenario 2: 153 to 63, as long as none of block 62 is occupied and 63 is unoccupied
if(track_blocks[62].occupancy == False and track_blocks[63].occupancy == False and track_blocks[153].occupancy):

    #set switch position
    track_blocks[63].switch_position = 1 

    #set light signals
    track_blocks[62]._light_signal = False
    track_blocks[63]._light_signal = True
    track_blocks[153]._light_signal = True

#Scenario 3: 62, 63, 153 are all occupied, authority for 62 and 153 must turn red, then keep 63 green to allow
if(track_blocks[62].occupancy and track_blocks[63].occupancy and track_blocks[153].occupancy):

    #set authorities of 62 and 153 to zero
    track_blocks[62].authority = 0
    track_blocks[153].authority = 0

    #set lights to red
    track_blocks[62]._light_signal = False
    track_blocks[63]._light_signal = True
    track_blocks[153]._light_signal = False


# Consolidated print statements for error checking

#SWITCH AT BLOCK 57
print("Switch  57:\n")
# Block 57
print("Block 57 (Switch) Information: ")
print(f"Switch Position: {track_blocks[57]._switch_position}")
print(f"Light Signal: {track_blocks[57]._light_signal}")
print(f"Authority: {track_blocks[57].authority}\n")

# Block 58
print("Block 58 Information: ")
print(f"Light Signal: {track_blocks[58]._light_signal}")
print(f"Authority: {track_blocks[58].authority}\n")

# Block 151
print("Block 151 Information: ")
print(f"Light Signal: {track_blocks[151]._light_signal}")
print(f"Authority: {track_blocks[151].authority}\n")


#Switch at BLOCK 63
print("Switch 63: \n")
print("Block 63 (Switch) Information: ")
print(f"Switch Position: {track_blocks[63]._switch_position}")
print(f"Light Signal: {track_blocks[63]._light_signal}")
print(f"Authority: {track_blocks[63].authority}\n")

# Block 62
print("Block 62 Information: ")
print(f"Light Signal: {track_blocks[62]._light_signal}")
print(f"Authority: {track_blocks[62].authority}\n")

# Block 151
print("Block 153 Information: ")
print(f"Light Signal: {track_blocks[153]._light_signal}")
print(f"Authority: {track_blocks[153].authority}\n")

"""




















