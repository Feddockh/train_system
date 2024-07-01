# train_system/common/schedule.py

import pandas as pd

class Schedule:
    def __init__(self) -> None:

        """
        Initializes the Schedule object.
        """

        self.trains = []
        self.stops = []
        self.arrival_times = []

    def load_schedule(self, schedule_file: str) -> None:

        """
        Loads the schedule from the specified file.

        Args:
            schedule_file (str): The path to the schedule file.
        """

        df = pd.read_excel(schedule_file)
        self.trains = df['Train ID'].tolist()
        self.stops = df['Block (Station)'].tolist()
        self.arrival_times = df['Arrival'].tolist()

    def __repr__(self) -> str:

        """
        Returns a string representation of the Schedule object.

        Returns:
            str: The string representation of the Schedule object.
        """

        schedule_str = ""
        for train, stop, arrival in zip(self.trains, self.stops, self.arrival_times):
            schedule_str += f"{train}\t{stop}\t{arrival}\n"
        return schedule_str

# Test the Schedule class with an example file
if __name__ == "__main__":
    schedule_file = 'C:/Users/hayde/OneDrive/Pitt/2024_Summer_Term/ECE 1140/Project/train_system/tests/schedules/schedule_1.xlsx'
    schedule = Schedule()
    schedule.load_schedule(schedule_file)
    print(schedule)
