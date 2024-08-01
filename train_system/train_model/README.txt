README.txt
Train Model
Jeremy Love
8/1/2024

This file will explain the purpose and implementation of each file found within the Train Model Module (train_system/train_system/train_model).


train_model_v4.py
train_system/train_system/train_model/train_model_v4.py

This file implements all of the functions, calculations, and inter- & intra-module communication. More specifically, this file implements the TrainModel class which contains the aforementioned specifications. 
There is a default constructor function that implements connection to the global time keeper (train_system/common/time_keeper.py) and establishes all default variable values and connections.
There are numerous 'setter' functions that allow for the assignment of values to each functions respective variable, for variables in which it is applicable to have a setter function.
There are numerous 'getter' functions that allow for the retrieval of values for each functions respective variable, for variables and values in which it is applicable to have a getter function.
There are numerous 'handler' functions that allow for the handling of PyQt signal and slot connections that occur across module communications within the larger train system.
In addition to the above function categories, there are also numerous other functions that involved with MBO encryption, decryption, and variable communication, Track Model variable communication, Train Model physics updating, and other functions for module testing.


train_model_ui_v3.py
train_system/train_system/train_model/train_model_ui_v3.py

This file implements the user interface display for the Train Model module through implementation of PyQt.
This user interface displays all key module inputs and outputs for each train model instance, as well as a test bench for intra-module testing.
