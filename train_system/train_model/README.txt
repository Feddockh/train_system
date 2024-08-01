README.txt
Train Model
Jeremy Love
8/1/2024


README.txt
train_system/train_system/train_model/README.txt

This file will explain the purpose and implementation of each file found within the Train Model Module (train_system/train_system/train_model).


__init__.py
train_system/train_system/train_model/__init__.py

This file is required for the implementation of the Train Model within itself and within the larger Train System.


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


Older_Versions/
train_system/train_system/train_model/Older_Versions

This folder contains the older versions of the train_model_vx.py file as well as other older files used and created through the development of the Train Model module. None of the files contained within the Older_Versions/ directory are used in the final implementation of the Train Model and the larger Train System.
