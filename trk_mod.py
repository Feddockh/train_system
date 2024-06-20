from trk_mod_ui import MainWindow
from testbench_datatypes import TestbenchDatatype
import time


window = MainWindow()

occupied_blocks = [[]]
ticket_sales = [["Station 1", 0], ["Station 2", 0]]
signal_states = [["AB", "Green"], ["CD", "Red"]]
switch_states = [["AB", "A"], ["CD", "C"]]


def retrieve_test_input():
    print("in main retrieve input")

    enum, val = window.test_input()

    if enum == TestbenchDatatype.ADD_OCC:
        occupied_blocks.append(val)

    elif enum == TestbenchDatatype.REM_OCC:
        for i in occupied_blocks:
            if i == val:
                occupied_blocks.remove(i)
                break
    
    elif enum == TestbenchDatatype.TIX:
        for i in ticket_sales:
            if i[0] == val[0]:
                i[1] = val[1]
                break
    
    elif enum == TestbenchDatatype.SIG:
        for i in signal_states:
            if i[0] == val[0]:
                i[1] = val[1]
                break

    elif enum == TestbenchDatatype.SWI:
        for i in switch_states:
            if i[0] == val[0]:
                i[1] = val[1]
                break


#wait for file upload
while window.get_view() == 0:
    time.sleep(0.01)


#murphy's loop
while window.get_view() == 1:
    time.sleep(0.01)

    retrieve_test_input()
    window.draw_tables()
    