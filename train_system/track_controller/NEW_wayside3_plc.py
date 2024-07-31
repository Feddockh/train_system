"""
Determining Switch Positions for Wayside 3
"""
"""
#UNSAFE BY PLC - if(M.lastBlock & N & N-Q & N-M)
elif(track_blocks[2].occupancy == True  # 76 -> 2
     and track_blocks[11].switch.position == track_blocks[11].switch.child_blocks[1]  # 85 -> 11
     and track_blocks[3].switch.position == track_blocks[3].switch.child_blocks[0]  # 77 -> 3
     and (track_blocks[3].occupancy == True or  # 3 already correct
      track_blocks[4].occupancy == True or
      track_blocks[5].occupancy == True or
      track_blocks[6].occupancy == True or
      track_blocks[7].occupancy == True or
      track_blocks[8].occupancy == True or 
      track_blocks[9].occupancy == True or
      track_blocks[10].occupancy == True or
      track_blocks[11].occupancy == True)):
    
#UNSAFE BY PLC - if (Loop.lastBlock & N & N-Q & N-M)


elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[3]._light_signal == False):
    track_blocks[3]._authority = 10000

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
    and track_blocks[26].occupancy == False):
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 
    track_blocks[2]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[27]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False
    track_blocks[26]._plc_unsafe = False

#Train waiting to join or leave loop - if((M.lastBlock & N) OR (Loop.lastBlock & N))
elif(track_blocks[2].occupancy == True and  
    (track_blocks[3].occupancy == True or  
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True)):
    track_blocks[2]._authority = 0 
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 
elif(track_blocks[12].occupancy == True and 
    (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True)):
    track_blocks[12]._authority = 0  
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 

#First train joining loop - if(M.lastBound & (N EMPTY) & (LOOP EMPTY))
elif(track_blocks[2].occupancy == True and  
    (track_blocks[3].occupancy == False and 
    track_blocks[4].occupancy == False and
    track_blocks[5].occupancy == False and
    track_blocks[6].occupancy == False and
    track_blocks[7].occupancy == False and
    track_blocks[8].occupancy == False and
    track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False) and
    (track_blocks[12].occupancy == False and  
    track_blocks[13].occupancy == False and  
    track_blocks[14].occupancy == False and  
    track_blocks[15].occupancy == False and  
    track_blocks[16].occupancy == False and  
    track_blocks[17].occupancy == False and  
    track_blocks[18].occupancy == False and  
    track_blocks[19].occupancy == False and  
    track_blocks[20].occupancy == False and  
    track_blocks[21].occupancy == False and  
    track_blocks[22].occupancy == False and  
    track_blocks[23].occupancy == False and  
    track_blocks[24].occupancy == False and  
    track_blocks[25].occupancy == False and  
    track_blocks[26].occupancy == False)):  
    track_blocks[3].switch.position = track_blocks[3].switch.child_blocks[0] 
    track_blocks[11].switch.position = track_blocks[11].switch.child_blocks[1]  
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 

#Another train joining - if(M.lastBlock & (N EMPTY) & (First block of loop empty)) 
elif(track_blocks[2].occupancy == True and  
    (track_blocks[3].occupancy == False and  
    track_blocks[4].occupancy == False and
    track_blocks[5].occupancy == False and
    track_blocks[6].occupancy == False and
    track_blocks[7].occupancy == False and
    track_blocks[8].occupancy == False and
    track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False) and
    track_blocks[26].occupancy == False):  
    track_blocks[3].switch.position = track_blocks[3].switch.child_blocks[0]  
    track_blocks[11].switch.position = track_blocks[11].switch.child_blocks[1] 
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False  

#Train ready to leave the loop - if(LOOP.lastBlock & N-O & N-M & (N EMPTY) & (M EMPTY OR LOOP FULL))
elif(track_blocks[26].occupancy == True and  
    (track_blocks[3].occupancy == False and 
    track_blocks[4].occupancy == False and
    track_blocks[5].occupancy == False and
    track_blocks[6].occupancy == False and
    track_blocks[7].occupancy == False and
    track_blocks[8].occupancy == False and
    track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False) and
    ((track_blocks[2].occupancy == False) or  
    (track_blocks[12].occupancy == True and 
    track_blocks[13].occupancy == True and  
    track_blocks[14].occupancy == True and  
    track_blocks[15].occupancy == True and  
    track_blocks[16].occupancy == True and  
    track_blocks[17].occupancy == True and  
    track_blocks[18].occupancy == True and  
    track_blocks[19].occupancy == True and  
    track_blocks[20].occupancy == True and  
    track_blocks[21].occupancy == True and  
    track_blocks[22].occupancy == True and  
    track_blocks[23].occupancy == True and  
    track_blocks[24].occupancy == True and  
    track_blocks[25].occupancy == True and  
    track_blocks[26].occupancy == True))):  
    track_blocks[3].switch.position = track_blocks[3].switch.child_blocks[1] 
    track_blocks[11].switch.position = track_blocks[11].switch.child_blocks[1]  
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 

#Trains continuing to leave the loop - if(LOOP.lastBlock & N EMPTY & N-Q & N-R & (R EMPTY))
elif(track_blocks[26].occupancy == True and  
    (track_blocks[3].occupancy == False and 
    track_blocks[4].occupancy == False and
    track_blocks[5].occupancy == False and
    track_blocks[6].occupancy == False and
    track_blocks[7].occupancy == False and
    track_blocks[8].occupancy == False and
    track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False) and
    track_blocks[3].switch.get_child_index() == True and  
    track_blocks[12].switch.get_child_index() == False and  
    track_blocks[27].occupancy == False):  
    track_blocks[3].switch.position = track_blocks[3].switch.child_blocks[1]  
    track_blocks[11].switch.position = track_blocks[11].switch.child_blocks[1]  
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 
 
#emergency stop - if(M.lastBlock & N-R)
elif(track_blocks[2].occupancy == True and track_blocks[3].switch.get_child_index() == True): 
    track_blocks[2]._authority = 0  
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 

#emergency stop - if(LOOP.lastBlock & N-O)
elif(track_blocks[12].occupancy == True and track_blocks[11].switch.get_child_index() == False): 
    track_blocks[12]._authority = 0  
    track_blocks[3]._plc_unsafe = False  
    track_blocks[11]._plc_unsafe = False 

#IF IN N - Don't change anything - automatic authority = 10,000
elif(track_blocks[3].occupancy == True or 
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True):
    track_blocks[3]._plc_unsafe = True  
    track_blocks[11]._plc_unsafe = True  
 

"""
Determining Light Signals for Wayside 3
"""

print(track_blocks[11].switch.get_child_index())

#Another train wanting to leave the loop - red until first train leaves loop
if(track_blocks[11].switch.get_child_index() == False and
    track_blocks[26].occupancy == True and 
    (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True)):
    track_blocks[26]._light_signal == False
    track_blocks[26]._plc_unsafe = False

elif(track_blocks[11].switch.get_child_index() == False and
    track_blocks[26].occupancy == True and 
    (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True) and
    track_blocks[26]._light_signal == True):
    track_blocks[26]._plc_unsafe = True
    print("2")

elif(track_blocks[11].switch.get_child_index() == False and
    track_blocks[26].occupancy == True and 
    (track_blocks[3].occupancy == False and
    track_blocks[4].occupancy == False and
    track_blocks[5].occupancy == False and
    track_blocks[6].occupancy == False and
    track_blocks[7].occupancy == False and
    track_blocks[8].occupancy == False and 
    track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False)):
    track_blocks[26]._light_signal = True
    track_blocks[26]._plc_unsafe = False

#Another train wanting to leave the loop - red until first train leaves loop
if(track_blocks[11].switch.get_child_index() == True and
    track_blocks[26].occupancy == True and 
    (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True)):
    track_blocks[2]._light_signal = False
    track_blocks[3]._light_signal = True
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = False

    track_blocks[2]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[27]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False
    track_blocks[26]._plc_unsafe = False
    print("4")

elif(track_blocks[11].switch.get_child_index() == True and
    track_blocks[26].occupancy == True and 
    (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True) and
    track_blocks[26]._light_signal == True):
    track_blocks[26]._plc_unsafe = True
    print("5")

elif(track_blocks[11].switch.get_child_index() == True and
    track_blocks[26].occupancy == True and 
    (track_blocks[3].occupancy == False and
    track_blocks[4].occupancy == False and
    track_blocks[5].occupancy == False and
    track_blocks[6].occupancy == False and
    track_blocks[7].occupancy == False and
    track_blocks[8].occupancy == False and 
    track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False)):
    track_blocks[2]._light_signal = False
    track_blocks[3]._light_signal = True
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = True

    track_blocks[2]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[27]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False
    track_blocks[26]._plc_unsafe = False
    print("6")

#Another train wanting to join the loop - red until first train leaves N
elif(track_blocks[3].switch.get_child_index() == False and
    track_blocks[2].occupancy == True and 
    (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True)):
    track_blocks[2]._light_signal = False
    track_blocks[2]._plc_unsafe = False

elif(track_blocks[3].switch.get_child_index() == False and
    track_blocks[2].occupancy == True and 
    (track_blocks[3].occupancy == True or
    track_blocks[4].occupancy == True or
    track_blocks[5].occupancy == True or
    track_blocks[6].occupancy == True or
    track_blocks[7].occupancy == True or
    track_blocks[8].occupancy == True or 
    track_blocks[9].occupancy == True or
    track_blocks[10].occupancy == True or
    track_blocks[11].occupancy == True) and
    track_blocks[2]._light_signal == True):
    track_blocks[2]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False and
    track_blocks[2].occupancy == True and 
    (track_blocks[3].occupancy == False and
    track_blocks[4].occupancy == False and
    track_blocks[5].occupancy == False and
    track_blocks[6].occupancy == False and
    track_blocks[7].occupancy == False and
    track_blocks[8].occupancy == False and 
    track_blocks[9].occupancy == False and
    track_blocks[10].occupancy == False and
    track_blocks[11].occupancy == False)):
    track_blocks[2]._light_signal = True
    track_blocks[2]._plc_unsafe = False


# if (N-M & R = Green)
elif track_blocks[3].switch.get_child_index() == False and track_blocks[27]._light_signal == True:
    track_blocks[27]._plc_unsafe = True # UNSAFE

# elif (N-R & M = Green)
elif track_blocks[3].switch.get_child_index() == True and track_blocks[2]._light_signal == True:
    track_blocks[2]._plc_unsafe = True # UNSAFE

# elif (N-O & G == Green)
elif track_blocks[11].switch.get_child_index() == False and track_blocks[26]._light_signal == True:
    track_blocks[26]._plc_unsafe = True # UNSAFE

# elif (N-Q & O == Green)
elif track_blocks[11].switch.get_child_index() == True and track_blocks[12]._light_signal == True:
    track_blocks[12]._plc_unsafe = True # UNSAFE


elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[3]._light_signal == True):
    track_blocks[3]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[2]._light_signal == False):
    track_blocks[2]._authority = 0
    track_blocks[2]._plc_unsafe = False


elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[27]._light_signal == False):
    track_blocks[27]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[11]._light_signal == False):
    track_blocks[11]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[12]._light_signal == False):
    track_blocks[12]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[26]._light_signal == False):
    track_blocks[26]._plc_unsafe = True

# elif (N-M & M.lastBlock)
elif (track_blocks[3].switch.get_child_index() == False and
    track_blocks[2].occupancy == True):
    track_blocks[2]._light_signal = True
    track_blocks[3]._light_signal = False
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = False

    track_blocks[2]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[27]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False
    track_blocks[26]._plc_unsafe = False
    
elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[2]._light_signal == False):
    track_blocks[2]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[3]._light_signal == False):
    track_blocks[3]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[27]._light_signal == False):
    track_blocks[27]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[11]._light_signal == False):
    track_blocks[11]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[12]._light_signal == False):
    track_blocks[12]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[26]._light_signal == False):
    track_blocks[26]._plc_unsafe = True

#elif (N-Q & Loop.last block)
elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True):
    track_blocks[2]._light_signal = False
    track_blocks[3]._light_signal = True
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = True

    track_blocks[2]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[27]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False
    track_blocks[26]._plc_unsafe = False


elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[2]._light_signal == True):
    track_blocks[2]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[3]._light_signal == True):
    track_blocks[3]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[27]._light_signal == True):
    track_blocks[27]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[11]._light_signal == True):
    track_blocks[11]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[12]._light_signal == True):
    track_blocks[12]._plc_unsafe = True

elif(track_blocks[3].switch.get_child_index() == False
    and track_blocks[2].occupancy == True and
    track_blocks[26]._light_signal == True):
    track_blocks[26]._plc_unsafe = True

# elif (N-M & M.lastBlock)
elif (track_blocks[3].switch.get_child_index() == False and
    track_blocks[2].occupancy == True):
    track_blocks[2]._light_signal = True
    track_blocks[3]._light_signal = False
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = True
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = False

    track_blocks[2]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[27]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False
    track_blocks[26]._plc_unsafe = False
    
elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[2]._light_signal == True):
    track_blocks[2]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[3]._light_signal == False):
    track_blocks[3]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[27]._light_signal == True):
    track_blocks[27]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[11]._light_signal == True):
    track_blocks[11]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[12]._light_signal == True):
    track_blocks[12]._plc_unsafe = True

elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True and 
    track_blocks[26]._light_signal == False):
    track_blocks[26]._plc_unsafe = True



#elif (N-Q & Loop.last block)
elif (track_blocks[11].switch.get_child_index() == True and 
    track_blocks[26].occupancy == True):
    track_blocks[2]._light_signal = False
    track_blocks[3]._light_signal = True
    track_blocks[27]._light_signal = False
    track_blocks[11]._light_signal = False
    track_blocks[12]._light_signal = False
    track_blocks[26]._light_signal = True

    track_blocks[2]._plc_unsafe = False
    track_blocks[3]._plc_unsafe = False
    track_blocks[27]._plc_unsafe = False
    track_blocks[11]._plc_unsafe = False
    track_blocks[12]._plc_unsafe = False
    track_blocks[26]._plc_unsafe = False
    
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
    track_blocks[2]._plc_unsafe = True
    track_blocks[3]._plc_unsafe = True
    track_blocks[27]._plc_unsafe = True
    track_blocks[11]._plc_unsafe = True
    track_blocks[12]._plc_unsafe = True
    track_blocks[26]._plc_unsafe = True
