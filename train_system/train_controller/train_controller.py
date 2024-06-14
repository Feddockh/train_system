from PyQt5.QtWidgets import QApplication, QWidget
"""
setMode
-we need to choose between the two automatic modes and manual mode
-decide how we are doing this with other modules
-decide how we are encoding the different modes (enums?)
"""


"""
setSetpointSpeed
-if in driver mode, set speed
-authentication user is driver
-these checks would probably be set outside of function
"""

"""
openDoor
-have function for left, right and both
-set corresponding door status variables
"""

"""
closeDoor
-have function for left, right and both
-set corresponding door status variables
"""

"""
lightsOn
-turns lights on depending on block location
"""

"""
lightsOff
-turns lights off depending on block location
"""

"""
setStation
-uses beacon data to know and update upcoming station
-do we keep this station displayed after leaving?
"""

"""
getFault
-one for each fault type
-constantly looking from Train Model
-update Train Controller fault status
"""

"""
checkFault
-one for each fault type
-constantly checking Train Controller variables
-if fault is found, call fix/act function
"""

"""
get/set Kp,Ki
-member variable
"""

"""
calculateControlLaw
-output Pcmd
-save calculated uk as uk-1
-save calculated ek as ek-1
-constant T
-Kp and Ki are parameters
"""

"""
get/setCurrentSpeed
-member variable
-calculated internally
"""

"""
get/setLocation
-received from Train Model and used by MBO
-I think we measure by block and fractions
"""

"""
get/setTrainTemp
-member variable
"""

"""
get/setCommandSpeed
-from ???
"""

"""
get/setAuthority
-from???
-do we calculate this here or just input/output???
"""







