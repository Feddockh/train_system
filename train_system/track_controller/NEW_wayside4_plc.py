#train_system/track_controller/wayside4_plc.py

#SWITCH AT BLOCK 9

#(Correct)
# Scenario 1: C to yard, 9 to block 77, check yards authority if negative go to yard
if(track_blocks[8].occupancy and track_blocks[39].authority < 0):
    
    # set authority to zero
    track_blocks[9].authority = 0

    # set switch pos
    track_blocks[8].switch.position = track_blocks[8].switch.child_blocks[1]

    # set light signals
    track_blocks[8]._light_signal = False
    track_blocks[9]._light_signal = False
    track_blocks[38]._light_signal = True

#(Correct)
# Scenario 2: Yard to C, 77 to 9
if(track_blocks[38].occupancy and 
    (track_blocks[0].occupancy == False and track_blocks[1].occupancy == False and track_blocks[2].occupancy == False and 
     track_blocks[3].occupancy == False and track_blocks[4].occupancy == False and track_blocks[5].occupancy == False and 
     track_blocks[6].occupancy == False and track_blocks[7].occupancy == False and track_blocks[8].occupancy == False)):

    # set authority
    track_blocks[9].authority = 0

    # set switch pos
    track_blocks[8].switch.position = track_blocks[8].switch.child_blocks[1]

    # set light signals
    track_blocks[8]._light_signal = True
    track_blocks[9]._light_signal = False
    tracK_blocks[38]._light_signal = False

# Scenario 3: Block 9 to 10
if(track_blocks[8].occupancy and track_blocks[38].occupancy and 
   (track_blocks[9].occupancy == False and track_blocks[10].occupancy == False and track_blocks[11].occupancy == False and 
    track_blocks[12].occupancy == False and track_blocks[14].occupancy == False)):

    # set authority
    track_blocks[38].authority = 0

    # set switch pos
    track_blocks[8].switch.position = track_blocks[8].switch.child_blocks[0]

    # set light signals
    track_blocks[8]._light_signal = False
    track_blocks[9]._light_signal = True
    track_blocks[38]._light_signal = False

#(Correct)
# Scenario 4: Scenario block 10 to 9, check all occpancies of 1 -> 9 if all are unoccupied, connect 
if(track_blocks[9].occupancy and 
   (track_blocks[0].occupancy == False and track_blocks[1].occupancy == False and track_blocks[2].occupancy == False and 
    track_blocks[3].occupancy == False and track_blocks[4].occupancy == False and track_blocks[5].occupancy == False and 
    track_blocks[6].occupancy == False and track_blocks[7].occupancy == False and track_blocks[8].occupancy == False)):

    # set switch pos
    track_blocks[8].switch.position = track_blocks[8].switch.child_blocks[0]

    # set light signals
    #track_blocks[8]._light_signal = True
    track_blocks[9]._light_signal = True
    track_blocks[38]._light_signal = False


#(Correct)
#Emergency stop scenario, check that A->C is occupied and any of E->D and any of F through H(27) in addition to that authority to the yard it not negative
if((track_blocks[0].occupancy or track_blocks[1].occupancy or track_blocks[2].occupancy or track_blocks[3].occupancy or track_blocks[4].occupancy or track_blocks[5].occupancy or track_blocks[6].occupancy 
    or track_blocks[7].occupancy or track_blocks[9]) and (track_blocks[10].occupancy or track_blocks[11].occupancy or track_blocks[12].occupancy or track_blocks[13].occupancy or track_blocks[14].occupancy)
    and (track_blocks[15].occupancy or track_blocks[16].occupancy or track_blocks[17].occupancy or track_blocks[18].occupancy or track_blocks[19].occupancy or track_blocks[20].occupancy or track_blocks[21].occupancy
         or track_blocks[22].occupancy or track_blocks[23].occupancy or track_blocks[23].occupancy or track_blocks[24].occupancy or track_blocks[25].occupancy or track_blocks[26].occupancy) and (track_blocks[39].authority > 0)):
    
    print("EMERGENCY STOP")

    #Set Authority
    track_blocks[0].authority = 0
    track_blocks[14].authority = 0
    track_blocks[15].authority = 0

    #set lights
    track_blocks[0]._light_signal = False
    track_blocks[14]._light_signal = False
    track_blocks[15]._light_signal = False

#SWITCH AT BLOCK 16

#(correct)
# Scenario 1: A to F, check if block 1 is occupied, then make sure no blocks from F to H(27) are unoccupeid, also check if block 15 is unoccupied
if(track_blocks[0].occupancy and track_blocks[14].occupancy == False
   (track_blocks[15].occupancy == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and 
    track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and 
    track_blocks[21].occupancy == False and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and 
    track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and 
    track_blocks[27].occupancy == False and track_blocks[28].occupancy == False)):
    
    # set switch position A->F
    track_blocks[15].switch.position = track_blocks[15].switch.child_blocks[0]

    # set light signals
    track_blocks[0]._light_signal = True
    track_blocks[14]._light_signal = False
    track_blocks[15]._light_signal = False

#(Correct)
# Scenario 2: E to F, check if all blocks 16 through 27 are unoccupied, if so connect to block. make sure block 1 is unoccupied so that it doesn't confuse switch
if(track_blocks[14].occupancy and track_blocks[0].occupancy == False and track_blocks[15].occupancy == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False
   and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False and track_blocks[22].occupancy == False
   and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False):
    
    #set switch position
    track_blocks[15].switch.position = track_blocks[15].switch.child_blocks[1]
    

    # set light signals
    track_blocks[0]._light_signal = False
    track_blocks[14]._light_signal = False
    track_blocks[15]._light_signal = True


#Questionable come back to this plc
#Scenario 3: A to F, check if F through H(27) are unoccupied, set block 15 authority to 0, 
if(track_blocks[0].occupancy and track_blocks[15].occupancy == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False
   and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False
   and track_blocks[26].occupancy == False):
    
    #set switch posiiton
    track_blocks[15].switch.position = track_blocks[15].switch.child_blocks[0]

    #set authority at 15
    track_blocks[14].authority = 0

    #set light signal
    track_blocks[0]._light_signal = False
    track_blocks[14]._light_signal = False
    track_blocks[15]._light_signal = True


#(Correct)
# Scenario 4: F to A, check if block 16 is occupied, then if so, check if A-> C are unoccupied, and if any E--> D are occupied
if(track_blocks[15].occupancy and track_blocks[0].occupancy == False and track_blocks[1].occupancy == False and track_blocks[2].occupancy == False and track_blocks[3].occupancy == False
   and track_blocks[4].occupancy == False and track_blocks[5].occupancy == False and track_blocks[6].occupancy == False and track_blocks[7].occupancy == False and track_blocks[8].occupancy == False
   and (track_blocks[9].occupancy or track_blocks[10].occupancy or track_blocks[11].occupancy or track_blocks[12].occupancy or track_blocks[13].occupancy or track_blocks[14].occupancy)):

    # set switch pos
    track_blocks[15].switch.position = track_blocks[15].switch.child_blocks[0]

    # set lights
    track_blocks[0]._light_signal = True
    track_blocks[14]._light_signal = False
    track_blocks[15]._light_signal = False

#(Correct)
# Scenario 5: F to E, check if 16 is occupied, and all E --> D are unoccupied, and check if some of A --> C are occupied
if(track_blocks[15].occupancy and track_blocks[14].occupancy == False and track_blocks[13].occupancy == False and track_blocks[12].occupancy == False and track_blocks[11].occupancy == False and track_blocks[10].occupancy == False
   and track_blocks[9] == False and (track_blocks[0].occupancy or track_blocks[1].occupancy or track_blocks[2].occupancy or track_blocks[3].occupancy or track_blocks[4].occupancy or track_blocks[5].occupancy or track_blocks[6].occupancy
    or track_blocks[7].occupancy or track_blocks[8].occupancy)):

    # set switch pos
    track_blocks[15].switch.position = track_blocks[15].switch.child_blocks[1]

    # set lights
    track_blocks[0]._light_signal = False
    track_blocks[14]._light_signal = True
    track_blocks[15]._light_signal = False


# Switch 27

#(Correct)
# Scenario 1: connect 27 to 28
if(track_blocks[26].occupancy and track_blocks[27].occupancy == False and track_blocks[28].occupancy == False and track_blocks[29].occupancy == False and track_blocks[30].occupancy == False and track_blocks[31].occupancy == False and track_blocks[32].occupancy == False):

    #set switch position
    track_blocks[26].switch.position = track_blocks[26].switch.child_blocks[0]

    #set authority at 76 to zero
    track_blocks[37].authority = 0

    #set light color
    track_blocks[26]._light_signal = False
    track_blocks[27]._light_signal = True
    track_blocks[37]._light_signal = False

#(Correct)
#  Scenario 2: connect 76 to 27, check all occupancies in F G and H(27) if unoccupied then connect if not, don't connect
if(track_blocks[37].occupancy and (track_blocks[15].occupancy == False and track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False
    and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False and track_blocks[22].occupancy == False
    and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False)):

    #set switch position
    track_blocks[26].switch.position = track_blocks[26].switch.child_blocks[1]

    #set authority to 0 at 28 jsut in case theres a trian coming form that direction
    track_blocks[27].authority = 0

    #set lights
    track_blocks[26]._light_signal = True
    track_blocks[27]._light_signal = False
    track_blocks[37]._light_signal = False

#(Correct)
#Scenario 3: 27 to 76 check that blocks 72 73 74 75 and 76 are all unoccupied, and check if 28 through 30 are occupied
if(track_blocks[26].occupancy and track_blocks[33].occupancy == False and track_blocks[34].occupancy == False and track_blocks[35].occupancy == False and track_blocks[36].occupancy == False and track_blocks[37].occupancy == False
   and (track_blocks[27].occupancy or track_blocks[28].occupancy or track_blocks[29].occupancy or track_blocks[30].occupancy or track_blocks[31].occupancy or track_blocks[32].occupancy)):
    
    #set switch position
    track_blocks[26].switch.position = track_blocks[26].switch.child_blocks[1]

    #set authority at 28 to zero
    track_blocks[27].authority = 0

    #set lights
    track_blocks[26]._light_signal = False
    track_blocks[27]._light_signal = False
    track_blocks[37]._light_signal = True


#Switch at Block 9
print("Wayside 4\n")

# Block 9
print("Switch 9: ")
print(f"Switch Position: {track_blocks[8].switch.position}")
print(f"Light Signal: {track_blocks[8]._light_signal}")
print(f"Authority: {track_blocks[8].authority}\n")

# Block 10
print("Block 16 Information: ")
print(f"Light Signal: {track_blocks[9]._light_signal}")
print(f"Authority: {track_blocks[9].authority}\n")

# Block 27
print("Block 77 Information: ")
print(f"Light Signal: {track_blocks[38]._light_signal}")
print(f"Authority: {track_blocks[38].authority}\n")


#Switch at BLOCK 16
print("Switch 16 Information: ")
print(f"Switch Position: {track_blocks[15].switch.position}")
print(f"Light Signal: {track_blocks[15]._light_signal}")
print(f"Authority: {track_blocks[15].authority}\n")

# Block 1
print("Block 1 Information: ")
print(f"Light Signal: {track_blocks[0]._light_signal}")
print(f"Authority: {track_blocks[0].authority}\n")

# Block 15
print("Block 15 Information: ")
print(f"Light Signal: {track_blocks[14]._light_signal}")
print(f"Authority: {track_blocks[14].authority}\n")


#Switch at Block 29

print("Switch 27 Information: ")
print(f"Switch Position: {track_blocks[26].switch.position}")
print(f"Light Signal: {track_blocks[26]._light_signal}")
print(f"Authority: {track_blocks[26].authority}\n")

#block 28 information
print("Block 28 Information: ")
print(f"Light Signal: {track_blocks[27]._light_signal}")
print(f"Authority: {track_blocks[27].authority}\n")

#block 76 information
print("Block 76 Information: ")
print(f"Light Signal: {track_blocks[37]._light_signal}")
print(f"Authority: {track_blocks[37].authority}\n")











"""
Pre Index Change

"""

#Correct REDLINE wayside 4 code
#new switch 9 

"""
#scenario 1: C to yard, 9 to block 77, if block 9 is occupied, and block 10 is occupied, connect switch to 9 so that the train can travel into the yard from 9
if(track_blocks[9].occupancy and (track_blocks[10].occupancy) and track_blocks[77].occupancy == False):
    
    #set authority to zero
    track_blocks[10].authority = 0

    #set switch pos
    track_blocks[9]._switch_position = 1

    #set light signals
    track_blocks[10]._light_signal = False
    track_blocks[77]._light_signal = True


#Scenario 2: Yard to C, 77 to 9, 
if(track_blocks[77].occupancy and (track_blocks[1].occupancy == False and track_blocks[2].occupancy == False and track_blocks[3].occupancy == False and track_blocks[4].occupancy == False and track_blocks[5].occupancy == False and track_blocks[6].occupancy == False and track_blocks[7].occupancy == False and track_blocks[8].occupancy == False and track_blocks[9].occupancy == False)):

    #set authority
    track_blocks[10].authority = 0

    #set switch pos
    track_blocks[9]._switch_position = 1

    #set light signals
    track_blocks[9]._light_signals = True
    track_blocks[10]._light_signals = False

#Scenario 3: Block 9 to 10, check if block 9 is occupied and block 77 is occupied, we must connect to 10 to prevent collision check that E -> D are unoccupied
if(track_blocks[9].occupancy and track_blocks[77].occupancy and (track_blocks[10].occupancy == False and track_blocks[11].occupancy == False and track_blocks[12].occupancy == False and track_blocks[13].occupancy == False and track_blocks[15].occupancy == False)):

    #set authority
    track_blocks[77].authority = 0

    #set switch pos
    track_blocks[9]._switch_position = 0

    #set light signals
    track_blocks[9]._light_signal = True
    track_blocks[10]._light_signal = True
    track_blocks[77]._light_signal = False

#Scenario 4: Scenario block 10 to 9 and need 9 and A -> C to be unoccupied
if(track_blocks[10].occupancy and (track_blocks[1].occupancy == False and track_blocks[2].occupancy == False and track_blocks[3].occupancy == False and track_blocks[4].occupancy == False and track_blocks[5].occupancy == False and track_blocks[6].occupancy == False and track_blocks[7].occupancy == False and track_blocks[8].occupancy == False and track_blocks[9].occupancy == False)):

    #set switch pos
    track_blocks[9]._switch_position = 0

    #set light signals
    track_blocks[9]._light_signal = True
    track_blocks[10]._light_signal = True
    track_blocks[77]._light_signal = False

#Scenario 5: 9, 10, and 77 are occupied, EMERGENCY STOP
if(track_blocks[9].occupancy and track_blocks[10].occupancy and track_blocks[77].occupancy):

    #set authorities
    track_blocks[9].authority = 0
    track_blocks[10].authority = 0
    track_blocks[77].authority = 0

    #set light signals
    track_blocks[9]._light_signal = False
    track_blocks[10]._light_signal = False
    track_blocks[77]._light_signal = False

#Scenario 6:




#i believe all of switch 16 code is correct

#Switch at block 16
#Scenario 1: A to F, check if block 1 is occupied, check if F -> H are unoccupied, make sure that block 15 is UNOCCUPIED but some of E->D are occupied
# if true, switch position = 0, then A connects to F
if (((track_blocks[1].occupancy) and
    track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False
    and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False
    and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False
    and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and track_blocks[27].occupancy == False
    and track_blocks[28].occupancy == False and track_blocks[29].occupancy == False) and (
    (track_blocks[15].occupancy == False) and (track_blocks[14].occupancy or track_blocks[13].occupancy or track_blocks[12].occupancy
    or track_blocks[11].occupancy or track_blocks[10].occupancy))):
    
    #set switch position A->F
    track_blocks[16]._switch_position = 0

    #set light signals
    track_blocks[1]._light_signal = True
    track_blocks[15]._light_signal = False


    
#Scenario 2: E to F, check if block 15 = OCCUPIED, check if block 1 = UNOCCUPIED and some of A-> C = OCCUPIED, then check if the F through H = UNOCCUPED
#if all are true, switch posiiton = 1, then E to F
if((track_blocks[15].occupancy) and (track_blocks[1].occupancy == False) and (track_blocks[2].occupancy or track_blocks[3].occupancy or track_blocks[4].occupancy or track_blocks[5].occupancy or track_blocks[6].occupancy or track_blocks[7].occupancy or track_blocks[8].occupancy or track_blocks[9].occupancy)
   and (track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False
        and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and track_blocks[27].occupancy == False
            and track_blocks[28].occupancy == False and track_blocks[29].occupancy == False)):
    
    #set switch position
    track_blocks[16]._switch_position = 1

    #set light signals
    track_blocks[1]._light_signal = False
    track_blocks[15]._light_signal = True

#Scenario 3: Block 1, 15, and 16 are all occupied
# if all are true set authority to zero at all points, all lights to red
if(track_blocks[1].occupancy and track_blocks[15].occupancy and track_blocks[16].occupancy):
    
    #set authoritys
    track_blocks[1].authority = 0
    track_blocks[15].authority = 0
    track_blocks[16].authority = 0

    #set lights
    track_blocks[1]._light_signal = False
    track_blocks[15]._light_signal = False
    track_blocks[16]._light_signal = False



#Scenario 4: F to A, check if block 16 = OCCUPIED, blocks A -> C are unoccupied, and some of E -> D are occupied, switch pos = 0
if(track_blocks[16].occupancy and (track_blocks[1].occupancy == False and track_blocks[2].occupancy == False and track_blocks[3].occupancy == False and track_blocks[4].occupancy == False and track_blocks[5].occupancy == False and track_blocks[5].occupancy == False and track_blocks[6].occupancy == False and track_blocks[7].occupancy == False and track_blocks[8].occupancy == False and track_blocks[9].occupancy == False)
   and (track_blocks[15].occupancy or track_blocks[14].occupancy or track_blocks[13].occupancy or track_blocks[12].occupancy or track_blocks[11].occupancy or track_blocks[10].occupancy)):
    
    #set switch pos
    track_blocks[16]._switch_position = 0

    #set lights
    track_blocks[1]._light_signal = True
    track_blocks[15]._light_signal = False

#Scenario 5: F to E, check if block 16 = OCCUPIED< blocks E -> D are unoccupied, and some of A -> C are occupied, switch pos = 1
if(track_blocks[16].occupancy and (track_blocks[1].occupancy or track_blocks[2].occupancy or track_blocks[3].occupancy or track_blocks[5].occupancy or track_blocks[6].occupancy or track_blocks[7].occupancy or track_blocks[8].occupancy or track_blocks[9].occupancy)
   and track_blocks[15].occupancy == False and track_blocks[14].occupancy == False and track_blocks[13].occupancy == False and track_blocks[12].occupancy == False and track_blocks[11].occupancy == False and track_blocks[10].occupancy == False):
    
    #set switch pos
    track_blocks[16]._switch_position = 1

    #set lights
    track_blocks[1]._light_signal = False
    track_blocks[2]._light_signal = False


#switch 27

#Scenario 1: connect 27 to 28, block 27 is occupied, check 28-> 33 for unoccupied if so then continue straight
if(track_blocks[27].occupancy and (track_blocks[28].occupancy == False and track_blocks[29].occupancy == False and track_blocks[30].occupancy == False and track_blocks[31].occupancy == False and track_blocks[32].occupancy == False and track_blocks[33].occupancy == False)):

    #set authority at T to zero
    track_blocks[76].authority = 0

    #set switch position
    track_blocks[27]._switch_position = 0

    #set light position 
    track_blocks[27]._light_signal = True
    track_blocks[28]._light_signal = True
    track_blocks[76]._light_signal = False

#Scenario 2: 28 to 27, blocks 27 through 16 are unoccupied, and, set authority at 76 to zero
if(track_blocks[28].occupancy and track_blocks[76].occupancy == False and (track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and track_blocks[27].occupancy == False)):

    #set switch position
    track_blocks[27]._switch_position = 0

    #set light signals
    track_blocks[27]._light_signal = True
    track_blocks[28]._light_signal = True
    track_blocks[76]._light_signal = False

#Scenario 3: 27 to 76, blocks on H must be occupied, set authority at 28 to zero to prevent anything from continuing, all blocks S R, and T must be unoccipued
if(track_blocks[27].occupancy and (track_blocks[76].occupancy == False and track_blocks[72].occupancy == False and track_blocks[73].occupancy == False and track_blocks[74].occupancy == False and track_blocks[75].occupancy == False)
   and (track_blocks[28].occupancy or track_blocks[29].occupancy or track_blocks[30].occupancy or track_blocks[31].occupancy or track_blocks[32].occupancy or track_blocks[33].occupancy)):
    
    #set switch position 
    track_blocks[27]._switch_position = 1

    #set light signals
    track_blocks[27]._light_signal = True
    track_blocks[28]._light_signal = False
    track_blocks[76]._light_signal = True

#Scenario 4: 76 to 27, check 16 through 27 make sure all are unoccupied, this one will be with block 28 being occupied, 76 to 27 gets priority
if(track_blocks[76].occupancy and track_blocks[28].occupancy and (track_blocks[16].occupancy == False and track_blocks[17].occupancy == False and track_blocks[18].occupancy == False and track_blocks[19].occupancy == False and track_blocks[20].occupancy == False and track_blocks[21].occupancy == False and track_blocks[22].occupancy == False and track_blocks[23].occupancy == False and track_blocks[24].occupancy == False and track_blocks[25].occupancy == False and track_blocks[26].occupancy == False and track_blocks[27].occupancy == False)):

    #76 to 27 gets priority in this situation
    track_blocks[27]._switch_position = 1

    #set lights
    track_blocks[27]._light_signal = True
    track_blocks[28]._light_signal = False
    track_blocks[76]._light_signal = True

   """ 