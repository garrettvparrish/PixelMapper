# imports
import math, os, time, serial, time
import Tkinter,time
from Tkinter import *
from Tkinter import Tk, Canvas, PhotoImage, mainloop
from math import sin
import threading
from tkFileDialog import askopenfilename
from numpy import loadtxt
from pixel import Pixel
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# port = serial.Serial("/dev/tty.usbmodem1411", baudrate=115200, timeout=3.0)
# time.sleep(2)

# ################################
# ######## Main UI Canvas ########
# ################################

# Root
root = Tkinter.Tk()
root.title("Lights and Magic")

# Canvas
WIDTH, HEIGHT = 480, 720
canvas = Canvas(root, width=WIDTH, height=HEIGHT, bg="#FFFFFF")
padding = 0.0
multiplier = 1.0


mouseDiameter = 15 * multiplier
showMouse = False
mouseX = 0
mouseY = 0

# Mouse Event Listeners
def mouseClick(event):
    drawOval(event)
#    print 'Mouse click: ' + str(event.x) + ', ' + str(event.y)

def mouseMove(event):
    drawOval(event)
#    print 'Mouse move: ' + str(event.x) + ', ' + str(event.y)

def drawOval(event):
    global mouseX, mouseY
    showMouse = True
    mouseX = event.x
    mouseY = event.y
    updateCanvas()

# Mouse Events
canvas.bind("<Button-1>", mouseClick)
canvas.bind("<B1-Motion>", mouseMove)
canvas.grid(row=0,column=0, rowspan=100)

################################
######### Pixel Mapping ########
################################

pixelMapping = []

################################
########## Board Coms ##########
################################

cmdMessage = StringVar()

def setIndividualPixel():
    x = 0
    command = cmdMessage.get();
    data = command.split(',')
#    setPixelToColor(data[0], data[1], data[2], data[3])
    serialMessage = "$" + command + "\r"
    print 'Sending: ' + serialMessage
    port.write(serialMessage)

def colorBoard():
    x = 0
#     for index in range(int(numLEDs.get())):
#         command = str(cmdMessage.get())    
#         data = command.split(',')
# #        setPixelToColor(index, data[0], data[1], data[2])
#         serialMessage = "$" + str(index) + "," + command + "\r"
# #        print 'Sending: ' + serialMessage
#         port.write(serialMessage)

################################
###### Command Interface #######
################################

panelSettingsLabel = Label(root, text="Panel Settings:", width=25).grid(row=0,column=1)

numLEDs = StringVar()
numLEDsLabel = Label(root, text="Number of LEDs:", width=25).grid(row=1,column=1)
numLEDsEntry = Entry(root, bg="#FFFFFF", width=25, textvariable=numLEDs).grid(row=2,column=1)

panelWidth = StringVar()
panelWidthLabel = Label(root, text="Panel Width (pixels):", width=25).grid(row=3,column=1)
panelWidthEntry = Entry(root, bg="#FFFFFF", width=25, textvariable=panelWidth).grid(row=4,column=1)

panelHeight = StringVar()
panelHeightLabel = Label(root, text="Panel Height (pixels):", width=25).grid(row=5,column=1)
panelHeightEntry = Entry(root, bg="#FFFFFF", width=25, textvariable=panelHeight).grid(row=6,column=1)


cmdLabel = Label(root, text="Color:", width=25).grid(row=8,column=1)
cmdEntry = Entry(root, bg="#FFFFFF", width=25, textvariable=cmdMessage).grid(row=9,column=1)
cmdSend = Button(root, text='Send to Pixel', width=25, command=setIndividualPixel).grid(row=10, column=1)
cmdSend = Button(root, text='Send to All', width=25, command=colorBoard).grid(row=11, column=1)

################################
########### Mappings ###########
################################

def chooseMapping():
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print 'Chose mapping: ' + filename
    loadMapping(filename)

mappingFilePath = StringVar()
mappingFileLabel = Label(root, text="Choose a mapping:", width=25).grid(row=12,column=1)
mappingChooseButton = Button(root, text='Choose', width=25, command=chooseMapping).grid(row=13, column=1)

def loadMapping(filename):
    global multiplier, padding
    print 'Loading mapping ...'
    lines = loadtxt(filename, comments="#", delimiter=",", unpack=False)
    metaData = lines[0]

    numLEDs.set(str(int(metaData[0])))
    panelWidth.set(str(int(metaData[1])))
    panelHeight.set(str(int(metaData[2])))
    mapping = lines.tolist()
    mapping.remove([metaData[0], metaData[1], metaData[2]])
    for p in mapping:
        pixelMapping.append(Pixel(p[0], p[1], p[2]))
    updateCanvas()

################################
############# Quit #############
################################

def quit():
    print 'Quitting ...'
    root.destroy()

quit = Button(root, text='Quit', width=25, command=quit).grid(row=14, column=1)

################################
############## UI ##############
################################

def setPixelToColor(n, r, g, b):
    p = pixelMapping[int(n)]
    p.r = r
    p.g = g
    p.b = b
    updateCanvas()

def updateCanvas():
    global padding, multiplier, mouseX, mouseY

    # Clear Canvas
    canvas.delete("all")

    # Set Canvas Size
    width = float(panelWidth.get())*multiplier
    height = float(panelHeight.get())*multiplier
    canvas.config(width=width, height=height, background="black")

    # Draw Bounding Box
    canvas.create_line(0, 0, width, 0)
    canvas.create_line(width, 0, width, height)
    canvas.create_line(width, height, 0, height)
    canvas.create_line(0,height,0,0)

    # Draw all pixels
    for pixel in pixelMapping:
        x = pixel.x
        y = pixel.y
        canvas.create_rectangle(x*multiplier, y*multiplier, (x+1)*multiplier, (y+1)*multiplier, fill="black", outline="white")

    # Draw Mouse
    x = mouseX
    y = mouseY
    canvas.create_oval(x - mouseDiameter/2.0, y - mouseDiameter/2.0, x + mouseDiameter/2.0, y + mouseDiameter/2.0, outline="white", fill="white")

    # Save and read for pixel processing
    canvas.postscript(file="test.eps", colormode='color')
    im = Image.open("test.eps")
    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]

#    Go Through Pixels
    for pixel in pixelMapping:
        r = 0.0
        g = 0.0
        b = 0.0
        x = pixel.x - 1.0
        y = pixel.y - 1.0
        # print 'Pixel Coordinates: (' + str(x) + ', ' + str(y) + ')'
        # print len(pixels)
        count = 0
        for i in range(int(x * multiplier), int((x+1) * multiplier)):
            for j in range(int(y * multiplier), int((y+1) * multiplier)):
                # print str(i) + ' : ' + str(j)
                p_r, p_g, p_b = pixels[j][i]
                r += p_r
                g += p_g 
                b += p_b
                count += 1
        avg_r = int(float(r)/count)
        avg_g = int(float(g)/count)
        avg_b = int(float(b)/count)
#        print "Average Color for Pixel " + str(pixel.index) + ": " + str(avg_r) + ", " + str(avg_g) + ", " + str(avg_b)
        serialMessage = "$" + str(pixel.index) + ", " + str(avg_r) + ", " + str(avg_g) + ", " + str(avg_b) + "\r"
        port.write(serialMessage)

        # canvas.create_rectangle(x*multiplier, y*multiplier, (x+1)*multiplier, (y+1)*multiplier, fill=pixel.colorString())



# ################################
# #### Serial Communication ######
# ################################

# def read_from_port():
#     while True:
#         bytesToRead = port.inWaiting()
#         msg = port.read(bytesToRead)
# #
# thread = threading.Thread(target=read_from_port, args=(port))
# thread.setDaemon(True)
# thread.start()

################################
############# RUN ##############
################################

root.mainloop()
