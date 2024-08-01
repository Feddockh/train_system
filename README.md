# Choo Choo On My Caboose Train System

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
    - [Clone the Repository](#clone-the-repository)
    - [Install Dependencies](#install-dependencies)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)
7. [Contact](#contact)

## Introduction
The objective of this project is to develop a fully operational train simulation. The system will include software and hardware elements that will allow for a demonstration of a scheduling center, a control office, a train model, track and train controllers, as well as the necessary communications between different modules. The system will have user interfaces for each model that allow for input and interactions for all possible users.

## Features

### Centralized Traffic Control (CTC) Office
- Select and Switch Between Manual and Automatic Dispatch Modes
- Select and Load Schedules in Automatic Modes
- Dispatch Trains with Destination Station and Arrival Time
- Dispatch Train Manually to a Destination Block
- Determines Authority within Safety Limits
- Determines Speed within Safety Limits
- Display Track Occupancy of the Transit System
- Display Passenger Throughput Metrics
- Maintenance Mode: Close Track Blocks and Switch Between Track Sections

### Track Controller
- Detects and Reports Track Block Occupancy Status
- Control Railway Crossing Lights and Gates
- Determines Railway Signal Status
- Determines Track Switch Positions
- Receives Speed and Authority
- PLC Program Upload
- Maintenance Mode: Manual Track Switching

### Track Model
- Displays track from Excel file

### Train Model
- Set and Regulate Internal Train Temperature
- Train Lights Status
- Train Doors Status
- Passenger Emergency Brake
- Calculates Newton’s Laws
- Display Train Properties
- Receive Track Circuit Signal with Speed and Authority
- Failure Modes

### Train Controller
- Safety Critical Architecture
- Train Lighting Control
- Train Door Control
- On-Board Station Announcement 
- Stopping Procedure
- Driver Speed Control
- Driver Emergency Brake
- Driver Service Brake
- Configurable Train Parameters
- Train Restriction by Authority and Speed Limit
- Train Regulation by Commanded Speed
- Fault Monitoring and Safety

### Moving Block Overlay (MBO) Controller
- Create Personell Schedules
- Create Train Schedules
- Load in Crewmember Profiles

## Installation

### Clone the Repository
To clone the repository, run the following command:

```bash
git clone git@github.com:Feddockh/train_system.git
```

### Install Dependencies
Make sure you have [Python](https://www.python.org/) installed. Use `pip` to install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage
Make sure you are at the top level of the repo
```bash
python -m train_system.main
```
or to run the ctc tc demo
```bash
python -m train_system.ctc_tc_demo
```

### Centralized Traffic Control (CTC) Office
```bash
python -m train_system.ctc_manager.ctc_manager
```

### Track Controller
```bash
python -m train_system.track_controller.track_controller_manager
```

### Track Model
```bash
python -m train_system.track_model.track_model
```

### Train Model
```bash
python -m train_system.train_model.
```

### Train Controller
```bash
python -m train_system.train_controller.tc_manager
```

### Moving Block Overlay (MBO) Controller
```bash
python -m train_system.mbo_manager.mbo_ui
```

## Contributing
- Hayden Feddock: common, ctc_manager
- Garrett Deller, Isabella Terick: track_controller
- Matt Discepola: track_model
- Jeremy Love: train_model
- Amber Earnest, Daniel Stoller: train_controller
- Arissa Buchina - mbo_manager

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For any questions, issues, or contributions, please feel free to reach out to us:

Email: hayden4feddock@gmail.com
GitHub Issues: GitHub Issues Page