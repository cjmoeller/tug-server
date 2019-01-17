import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


import tkinter as tk
from tkinter import filedialog
import os

def plotIt(values, plots):
    time, x, y, z, label = zip(*values)
    time = [t - start for t in list(time)]

    pltX, pltY, pltZ = plots

    pltX.plot(time, x)
    pltY.plot(time, y)
    pltZ.plot(time, z)

    label = list(label)

    first1 = label.index(1)
    last1 = len(label) - 1 - label[::-1].index(1)
    pltX.axvspan(time[first1], time[last1], alpha=0.5, color='red')
    pltY.axvspan(time[first1], time[last1], alpha=0.5, color='red')
    pltZ.axvspan(time[first1], time[last1], alpha=0.5, color='red')

    first2 = label.index(2)
    last2 = len(label) - 1 - label[::-1].index(2)
    pltX.axvspan(time[first2], time[last2], alpha=0.5, color='green')
    pltY.axvspan(time[first2], time[last2], alpha=0.5, color='green')
    pltZ.axvspan(time[first2], time[last2], alpha=0.5, color='green')

    first3 = label.index(3)
    last3 = len(label) - 1 - label[::-1].index(3)
    pltX.axvspan(time[first3], time[last3], alpha=0.5, color='yellow')
    pltY.axvspan(time[first3], time[last3], alpha=0.5, color='yellow')
    pltZ.axvspan(time[first3], time[last3], alpha=0.5, color='yellow')


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    currdir = os.getcwd()
    file_path = filedialog.askopenfilename(initialdir = currdir, title = "Choose Recording", filetypes = (("csv files","*.csv"),("all files","*.*")))
    print(file_path)
    file = open(file_path,"r")

    fig, (plotAcc, plotRot) = plt.subplots(2,3)

    accData = []
    rotData = []

    start = 0

    for line in file:
        split = line.split(';')
        if split[1] == '5' and start == 0:
            start = int(split[0])

        if start == 0: continue

        values = (int(split[0]), float(split[2]), float(split[3]), float(split[4]), int(split[5]))
        if split[1] == '3':
            accData.append(values)
        if split[1] == '4':
            rotData.append(values)



    plotIt(accData, plotAcc)
    plotIt(rotData, plotRot)


    plt.show()


