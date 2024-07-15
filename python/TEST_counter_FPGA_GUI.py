

"""
counter_FPGA_GUI.py is the GUI for continuous counting using the USB counter module
as a timestamp card.

Author: Lim Chin Chean 05/2019, S-Fifteen Instruments. Modded from QO Lab Script

Edited 06/20/2023 by Namish Kukreja. Quantum Optics Lab. The University of Texas at Austin.
"""
# from qitdevices.usb_counter import *
import usbcount_class as UC
import numpy as np
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import serial.tools.list_ports
import csv

# sets the size of the font for the counters
ft_size = 42
# sets the trigger type of input signal, PLEASE CHECK THIS. 'nim' or 'ttl'
signal_type='nim'

master = {}
col1 = "Angle"
col2 = "H"
col3 = "V"
list1 = []
list2 = []
list3 = []
# append the current dateAndTime TODO
file = "exporteddata.csv"
printing = False
counter1State = True
averageStart = False
numberOfDetectors=[1,2]
averageStarttime = 0
averageEndTime = 0
correctiveRatio = 1
correctiveRatio = ((7.2/7.7)**-1)*(7.7/8)
print(correctiveRatio)
def find_closest_index(arr,target):
    left = 0
    right = len(arr)-1

    while left<= right:
        mid = (left+right)//2
        if arr[mid]==target:
            return mid
        elif arr[mid]<target:
            left = mid+1
        else:
            right = mid-1
    if left == 0:
        return 0
    if right == len(arr)-1:
        return right
    if target - arr[right]<arr[left]-target:
        return right
    else:
        return left
# Stop querying the timestamp function, close device and initiate selected device in pairs mode.
def InitDevice(*args):

    loop_flag.set(False)
    started = 1
    deviceAddress = ''
    deviceAddress = addresslist[0]
    for idx, device in enumerate(devicelist):
        if set_ports.get() == device:
            deviceAddress = addresslist[idx]
            print("SelectedPort " + deviceAddress)
    
    counter.startport(deviceAddress)
    counter.mode = 'pairs'
    # print(set_ports.get(), "ready to go.")

def on_closing():
    counter.closeport()
    root.destroy()

# Function to change the integration time.
def change_counter_f(*args):
    loop_flag.set(True)
    counter.int_time=timer_00.get()

# Function to start the counter.
def start_f(*args):
    loop_flag.set(True)
    counter_100.set(0)
    counter_101.set(0)
    counter_102.set(0)
    while loop_flag.get():
        counter_value=counter.counts
        if printing == True:
            print(counter_value)
        counter_00.set('{:6.1f}'.format(counter_value[0])) #I removed the correctiveRatio (plz don't skin me alive)
        counter_01.set('{:6.1f}'.format(counter_value[1]))
        counter_02.set('{:6.1f}'.format(counter_value[2]))
        counter_03.set('{:6.1f}'.format(counter_value[3]))
        counter_100.set('{:6.1f}'.format(counter_value[4]))
        counter_101.set('{:6.1f}'.format(counter_value[5]))
        counter_102.set('{:6.1f}'.format(counter_value[6]))
        counter_103.set('{:6.1f}'.format(counter_value[7]))
        root.update()

# Stop querying the counter function, resets counter display in GUI.
def stop_f(*args):
    counter_00.set(format(0))
    counter_01.set(format(0))
    counter_02.set(format(0))
    counter_03.set(format(0))
    counter_100.set(format(0))
    counter_101.set(format(0))
    counter_102.set(format(0))
    counter_103.set(format(0))
    loop_flag.set(False)

def snapshot(*args):
    list1.append(angle.get())
    list2.append(counter_00.get())
    list3.append(counter_01.get())

def export(*args):
    print('guys im like exporting the data now lmao')
    file = f"exporteddata.csv"
    print([col1, col2, col3])
    # make the file if it doesn't exist
    with open(file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([col1, col2, col3])
        for one, two, three in zip(list1, list2, list3):

            writer.writerow([one, two, three])
# Creates a graph for the GUI.
def analyze(*args):
    currentTime = int(round(time.time() * 1000))
    global averageStart;
    global averageStarttime;
    global averageEndTime;
    try:
        if(averageStart==False): 
            averageStart = True

            for i in range(len(numberOfDetectors)):
                # the relevant variable is going to be named f"c0{numberOfDetectors[i]-1}_yar"

                averageCounterList[i].set("loading...")
                rangeCounterList[i].set("loading...")
            averageStarttime = currentTime
            # when the case is true, mark the time that it is in the array
            print(averageStart)
        elif(averageStart==True): 
            datas = [c00_yar,c01_yar,c02_yar,c03_yar]
            averageStart = False

            averageEndTime = currentTime
            print(f"gap between clicks was {(averageEndTime-averageStarttime)/1000} secs")
            print(f"your times were {averageEndTime} and {averageStarttime}")
            # then we want to find the values of c02_yar within that range, and average them
            # find the indicies of xar that match the times, and print them
            start_index = find_closest_index(xar,averageStarttime)
            end_index = find_closest_index(xar,averageEndTime)
            print(f"The indicies of xar with those times are start at {start_index} and {end_index}")
            print('-----------------')
            # then we want to, given an array and some indecies

            for i in range(len(numberOfDetectors)):
                data = datas[numberOfDetectors[i]-1]
                print(f"c0{numberOfDetectors[i]-1}_yar")
                # the relevant variable is going to be named f"c0{numberOfDetectors[i]-1}_yar"
                    
                averageValue = sum(data[start_index:end_index])/(end_index-start_index)
                # rangeData = max(data[start_index:end_index])-min(data[start_index:end_index])
                rangeData = np.std(data[start_index:end_index])
                averageCounterList[i].set(round(averageValue,0))
                rangeCounterList[i].set(round(rangeData,0))

    except Exception as e:  
        print(e)
        print("ERRORRRR")
        averageStart = True
        
fig = plt.Figure(figsize=[9.4, 4.8])

# Initialize the counter value array for displayed graph.
xar = [0]
c00_yar = [0]
c01_yar = [0]
c02_yar = [0]
c03_yar = [0]
c100_yar = [0]
c101_yar = [0]
c102_yar = [0]
c103_yar = [0]

# Updates the graphs with new values, resizes the axes every loop. The x-axis is the UTC time in milliseconds since the epoch.

def animate(i):
    xar.append(int(round(time.time() * 1000)))
    if counter1State==True:
        c00_yar.append((float(counter_00.get())))
    else:
        c00_yar.append(0)
    c01_yar.append(float(counter_01.get()))
    c02_yar.append(float(counter_02.get()))
    c03_yar.append(float(counter_03.get()))
    c100_yar.append(float(counter_100.get()))
    c101_yar.append(float(counter_101.get()))
    c102_yar.append(float(counter_102.get()))
    c103_yar.append(float(counter_103.get()))
    if max(xar) - xar[0] > 15000:
        xar.pop(0)
        c00_yar.pop(0)
        c01_yar.pop(0)
        c02_yar.pop(0)
        c03_yar.pop(0)
        c100_yar.pop(0)
        c101_yar.pop(0)
        c102_yar.pop(0)
        c103_yar.pop(0)
    axes = fig.gca() 
    axes.set_xlim([max(xar)-20000, max(xar)+1000])
    max_values = [max(c00_yar),max(c01_yar),max(c02_yar),max(c03_yar),max(c100_yar),max(c101_yar),max(c102_yar),max(c103_yar)]
    axes.set_ylim([1, max(max_values)+10])

    line1.set_xdata(xar)
    line1.set_ydata(c00_yar)  # update the data
    line2.set_xdata(xar)
    line2.set_ydata(c01_yar)  # update the data
    line3.set_xdata(xar)
    line3.set_ydata(c02_yar)  # update the data
    line4.set_xdata(xar)
    line4.set_ydata(c03_yar)  # update the data
    line5.set_xdata(xar)
    line5.set_ydata(c100_yar)  # update the data
    line6.set_xdata(xar)
    line6.set_ydata(c101_yar)  # update the data
    line7.set_xdata(xar)
    line7.set_ydata(c102_yar)  # update the data
    line8.set_xdata(xar)
    line8.set_ydata(c103_yar)  # update the data
    if(averageStart== True):
        line9.set_xdata(averageStarttime)
        ax.axvspan(xmin =xar[-2]+40, xmax = xar[-1],color = "red",alpha = .25 )

    return line1, line2, line3, line4, line5, line6, line7, line8,line9



"""Setting up the main window"""
root = Tk()
root.title("USB counter")
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

counter = UC.FPGA_counter()
#counter.level=signal_type
#counter.mode = 'pairs'

# Device option menu.
ttk.Label(mainframe, text='Select Device', font=("Helvetica", 12)).grid(row=2, padx=0, pady=2, column=1)
portslist = list(serial.tools.list_ports.comports())
devicelist = []
addresslist = []
for port in portslist:
    devicelist.append(port.device + " " + port.description)
    addresslist.append(port.device)
devicelist=devicelist[::-1]
portslist=portslist[::-1]
addresslist=addresslist[::-1]
if printing == True:
    print(devicelist)
set_ports = StringVar(mainframe)
ports_option = ttk.OptionMenu(mainframe, set_ports, devicelist, *devicelist)
ports_option.grid(row=7, padx=2, pady=5, column=2)
ports_option.configure(width=30)
loop_flag = BooleanVar()
loop_flag.set(False)

# String Variables used

counter_00 = StringVar()
counter_00.set(format(0))
counter_01 = StringVar()
counter_01.set(format(0))
counter_02 = StringVar()
counter_02.set(format(0))
counter_03 = StringVar()
counter_03.set(format(0))
counter_100 = StringVar()
counter_100.set(format(0))
counter_101 = StringVar()
counter_101.set(format(0))
counter_102 = StringVar()
counter_102.set(format(0))
counter_103 = StringVar()
counter_103.set(format(0))

averageCounterList = []
for i in range(len(numberOfDetectors)):
    averageCounterList.append(StringVar())
    averageCounterList[i].set(format(0))

rangeCounterList = []
for i in range(len(numberOfDetectors)):
    rangeCounterList.append(StringVar())
    rangeCounterList[i].set(format(0))

    
averageCounter = StringVar()
averageCounter.set(format(0))
rangeCounter = StringVar()
rangeCounter.set(format(0))

timer_00 = StringVar()
angle = StringVar()

# Basic setup for the displayed graph.
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1)

ax = fig.add_subplot(111)
line1, = ax.plot(xar, c00_yar)
line2, = ax.plot(xar, c01_yar)
line3, = ax.plot(xar, c02_yar)
line4, = ax.plot(xar, c03_yar)
line5, = ax.plot(xar, c100_yar)
line6, = ax.plot(xar, c101_yar)
line7, = ax.plot(xar, c102_yar)
line8, = ax.plot(xar, c103_yar)
line9= ax.axvline(x=averageStarttime,color = 'red', linewidth = 5,alpha = .5)

fig.legend(['C1', 'C2', 'C3', 'C4','P13','P14','P23','P24'], loc='upper right')
fig.suptitle('Counts (TTL) vs Current Time')
ax.set_xlabel('Time')
ax.set_ylabel('Counts')
ax.grid(True)
ani = animation.FuncAnimation(fig, animate, interval=100, blit=False)

# buttons
ttk.Button(mainframe, text="Start", command=start_f).grid(
    column=1, row=1, sticky=W)
ttk.Button(mainframe, text="Stop", command=stop_f).grid(
    column=2, row=1, sticky=W)
ttk.Button(mainframe, text="Set Gate Time", command=change_counter_f).grid(
    column=3, row=1, sticky=W)
ttk.Button(mainframe, text="Init Device", command=InitDevice).grid(
    column=4, row=7, sticky=W)
ttk.Button(mainframe, text="Snapshot", command=snapshot).grid(
    column=5, row=1, sticky=W)
ttk.Button(mainframe, text='Export', command=export).grid(
    column=5, row=2, sticky=W)
ttk.Button(mainframe,text='Analyze Interval Data', command=analyze).grid(
    column=6, row=1, sticky=W)
# controls
time_entry = Spinbox(mainframe, width=7, from_=0.1, to=5,
                     increment=.1, textvariable=timer_00)

angle_entry = Spinbox(mainframe, width=7, from_=0, to=360, increment=1, textvariable=angle)
angle_entry.grid(column=5, row=7, sticky=(W, E))
time_entry.grid(column=2, row=6, sticky=(W, E))
timer_00.set(250)
if printing == True:
    print(timer_00.get())

# title
ttk.Label(mainframe, text='Counting Rate',
          font=("Helvetica", 28)).grid(column=4, row=1, sticky=(W, E))


# labels
ttk.Label(mainframe, text='Channel 1',
          font=("Helvetica", 28)).grid(column=1, row=2, sticky=(W, E))
ttk.Label(mainframe, text='Channel 2',
          font=("Helvetica", 28)).grid(column=1, row=3, sticky=(W, E))
ttk.Label(mainframe, text='Channel 3',
          font=("Helvetica", 28)).grid(column=1, row=4, sticky=(W, E))
ttk.Label(mainframe, text='Channel 4',
          font=("Helvetica", 28)).grid(column=1, row=5, sticky=(W, E))
ttk.Label(mainframe, text='Pair C1-C3',
          font=("Helvetica", 28)).grid(column=3, row=2, sticky=(W, E))
ttk.Label(mainframe, text='Pair C1-C4',
          font=("Helvetica", 28)).grid(column=3, row=3, sticky=(W, E))
ttk.Label(mainframe, text='Pair C2-C3',
          font=("Helvetica", 28)).grid(column=3, row=4, sticky=(W, E))
ttk.Label(mainframe, text='Pair C2-C4',
          font=("Helvetica", 28)).grid(column=3, row=5, sticky=(W, E))
ttk.Label(mainframe, text='Gate Time / ms',
          font=("Helvetica", 12)).grid(column=1, row=6, sticky=(W))
ttk.Label(mainframe, text='Select Device',
          font=("Helvetica", 12)).grid(column=1, row=7, sticky=(W))
ttk.Label(mainframe, text='Angle',
          font=("Helvetica", 12)).grid(column=4, row=7)

ttk.Label(mainframe, text='Average',
          font=("Helvetica", 12)).grid(column=7, row=1)
ttk.Label(mainframe, text='Range',
          font=("Helvetica", 12)).grid(column=7, row=2)
for i in range(len(numberOfDetectors)):
        print(numberOfDetectors[i]-1)
        print(averageCounterList)
        ttk.Label(mainframe, text=f"Average {numberOfDetectors[i]}",
            font=("Helvetica", ft_size)).grid(column=7, row=1+2*i)
        ttk.Label(mainframe, text=f"STD {numberOfDetectors[i]}",
            font=("Helvetica", ft_size)).grid(column=7, row=2+2*i)

# outputs
ttk.Label(mainframe, textvariable=counter_00, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=2, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_01, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=3, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_02, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=4, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_03, anchor=E,
          font=("Helvetica", ft_size)).grid(column=2, row=5, sticky=(W, E))

ttk.Label(mainframe, textvariable=counter_100, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=2, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_101, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=3, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_102, width=7, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=4, sticky=(W, E))
ttk.Label(mainframe, textvariable=counter_103, anchor=E,
          font=("Helvetica", ft_size)).grid(column=4, row=5, sticky=(W, E))


ttk.Label(mainframe, textvariable=averageCounter, anchor=E,
          font=("Helvetica", ft_size)).grid(column=8, row=1, sticky=(W, E))
ttk.Label(mainframe, textvariable=rangeCounter, anchor=E,
          font=("Helvetica", ft_size)).grid(column=8, row=2, sticky=(W, E))
for i in range(len(numberOfDetectors)):
        print(numberOfDetectors[i]-1)
        print(averageCounterList)

        ttk.Label(mainframe, textvariable=averageCounterList[numberOfDetectors[i]-1], anchor=E,
            font=("Helvetica", ft_size)).grid(column=8, row=1+2*i, sticky=(W, E))
        ttk.Label(mainframe, textvariable=rangeCounterList[numberOfDetectors[i]-1], anchor=E,
            font=("Helvetica", ft_size)).grid(column=8, row=2+2*i, sticky=(W, E))


# padding the space surrounding all the widgets
for child in mainframe.winfo_children():
    child.grid_configure(padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW",on_closing)

# finally we run it!
root.mainloop()

