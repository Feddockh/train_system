#track_blocks[0].authority = 0

#switch
if(track_blocks[0].occupancy == False and track_blocks[1].occupancy == False and track_blocks[2].occupancy == True):
    track_blocks[0].switch_position = 0
elif(track_blocks[0].occupancy == True and track_blocks[1].occupancy == True and track_blocks[2].occupancy == False):
    track_blocks[0].switch_position = 1
elif(track_blocks[0].occupancy == True and track_blocks[1].occupancy == True and track_blocks[2].occupancy == True and track_blocks[0].switch_position == 1):
    track_blocks[0].authority = 0 #EMERGENCY BRAKE