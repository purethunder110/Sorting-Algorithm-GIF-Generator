


#Define basic trace_function
def show_trace():
    print("An error has occured, printing useful info:")
    print(sys.version)
    print(sys.version_info)

#Carefully import stuff
try:
    import sys
    from random import randint
    from time import time
    from algs import algorithmsDict
except:
    show_trace()
    raise ImportError("Could not access Sys, random, time or programs sorting alg")

try:
    import pygame
except:
    show_trace()
    raise ImportError("Pygame is not installed!")

try:
    import display as display
    import os
    import gc
except:
    show_trace()
    raise ModuleNotFoundError("Could not access display, os or gc")
try:
    import imageio.v3
except:
    show_trace()
    raise ModuleNotFoundError("Could not access imageio.v3")


# Declared in display.py
# 1. global variables : numBars, delay, do_sorting, paused, timer_space_bar
# 2. widgets : sizeBox, delayBox, algorithmBox, playButton, stopButton

textLog = []
textLogUpdate = True
#Todo:
# Add time estimate
# Make better number of pictures sorter
# Create own git page with reference
# Extend delay adjust to allow for more values than 0.1-0.2
# Add more file types, eg MP4
# Add option to print numbers in "bars"
# Add option for with/without menu visible
# Add option for GIF optimizatio
# Move loops to advanced options

#Known bugs
# Loops & start button does not move as size increases
# Loops box runs into log upon extreme numbers


#Generating gifs requires placing files in subfolder and then loading them.
#This deletes everything except gif
def deleteTempFiles():
    try:
        myFiles = []
        myDir = []
        for pathnames,dirnames,filenames in os.walk("pictures"):
            myFiles.extend(filenames)
            myDir.extend(dirnames)
        for files in myFiles:
            os.remove("pictures/" + files)
        for directories in myDir:
            os.rmdir("pictures/" + directories)
    except:
        raise EIO("Could not delete files in subfolder!")
#types:
#1=white text, just usual log
#2=progress bar change

def printL(type,addition):
    global textLog
    global textLogUpdate
    textLogUpdate = True
    textLog.append((type,addition))

def printProgress(progress):
    global textLog
    global textLogUpdate
    textLogUpdate = True
    textLog.insert(0,(2,progress))

def printProgressBar(currentValue):
    print("Progress:" +  str(currentValue) + "%")
    print("""[""",end="")
    progressCounter = 0
    for i in range(0,int(currentValue),5):
        print("""#""",end="")
        progressCounter +=1
    for i in range(0,20-progressCounter):
        print("""·""", end="")
    print("""]""")


0
def printSign():
    print("""
 _______         _______         _______ 
(  ____ \       (  ___  )       (  ____ |
| (    \/       | (   ) |       | (    \/
| (_____  _____ | (___) | _____ | |      
(_____  )(_____)|  ___  |(_____)| | ____ 
      ) |       | (   ) |       | | \_  )
/\____) |       | )   ( |       | (___) |
\_______)       |/     \|       (_______)
                                         """)

def findType(findType):
    global textLog
    for type,value in textLog:
        if type == findType:
            return True
    return False

def deleteType(theType):
    global textLog
    counter = 0
    while True:
        if counter >= len(textLog)-2:
            return True
        type,value = textLog[counter]
        if type == theType:
            textLog.pop(counter)
            counter = counter-3
        counter +=1


def updateDisplay():
    global textLog
    global textLogUpdate
    if not textLogUpdate:
        return -1
    textLogUpdate = False
    #runTime = time.strftime("%H:%M:%S", time.localtime(time.time() - startUpTime - 60 * 60))
    os.system("clear")
    printSign()
    #print(str(runTime))
    if len(textLog) > 20:
        for i in range(0,10):
            type,value = textLog[0]
            if type != 2:
                textLog.pop(0)
    maxProgress = -1
    for type,value in textLog:
        if type == 2:
            if value > maxProgress:
                maxProgress = value
    if -1 < maxProgress < 100:
        printProgressBar(maxProgress)
        print("--------------------------------------------")
    for type,value in textLog:
        if type != 2:
            print(value)

def CreateGIF(counter,SCREENSHOT_FILENAME):
    updateDisplay()
    ex = 5
    #Idea is that pictures are generated with numbers 0 to some MAX
    printL(1,"Trying to generate GIF, this may freeze the program and take a while")
    #Check for reasonable inputs
    if display.loopBox.text != "Inf":
        if int(display.loopBox.text) > 9999:
            printL(1,"Loops must be < 9999, set to 0 for infinite")
            printL(1,"Stopping GIF creation")
            deleteTempFiles()
            return -1
    if int(display.fpsBox.text) > 200:
        printL(1, "FPS must be < 200")
        printL(1, "Stopping GIF creation")
        deleteTempFiles()
        return -1
    #Find max
    fileNames = [] #Okay, let's start preparing for GIF
    for i in range(0,counter):
        fileNames.append(SCREENSHOT_FILENAME + str(i) + ".jpg")
    images = []
    #This will start to load in individual pictures into gif engine
    numberOfLoops = 0
    if display.loopBox.text != "Inf":
        numberOfLoops = int(display.loopBox.getText(type(8)))
    printL(1, "GIF settings:" + str(display.loopBox.text) + " loops, " + str(display.fpsBox.text) + "fps")
    newGif = imageio.get_writer('sorting.gif',format='GIF-PIL',mode='I',fps=int(display.fpsBox.text),loop=numberOfLoops)

    #if delay > 0, add ratio for that delay
    delay_ratio = 1
    if int(display.delay*1000/30) > 0:
        delay_ratio = int((display.delay*1000)/30)
    printL(1,("Adding " + str(display.delay) + " ms delay for each image in GIF"))
    totalRunTime = ((len(fileNames) * delay_ratio)/int(display.fpsBox.text))*0.9
    printL(1,"Approximate GIF runtime is " + str(totalRunTime) + "s")
    try:
        for (counter,filename) in enumerate(fileNames):
            updateDisplay()
            #images.append(imageio.v2.imread(filename))
            for i in range(0,delay_ratio):
                newGif.append_data(imageio.v2.imread(filename))
            printProgress(int(((counter)/len(fileNames))*100))
    except:
        raise EIO("Tried to create GIF, did not find sample pictures")
    printProgress(100)
    #Output gif
    #imageio.mimsave('sorting.gif', images, format = 'GIF-PIL', fps = 100)
    #Del latest list, this does NOT decrease current RAM usage, 
    #but makes next round use the same memory area instead
    newGif.close()
    printL(1,("Cleaning up remaining files"))
    del fileNames
    for item in images:
        del item
    del images
    gc.collect()
    printL(1,("GIF generation complete as sorting.gif"))
    #Delete all files in folder
    deleteTempFiles()
    deleteType(2)
    updateDisplay()
    
    
def getMaxNumber(files):
    currentMax  = -1
    for item in files:
        myNumber = int(item[len(SCREENSHOT_FILENAME):len(item)-4])
        if myNumber > currentMax:
            currentMax = myNumber
    return currentMax

def takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot):
    pygame.image.save(screenshot, "pictures/screenshot" + str(GIF_picture_counter) + ".jpg")

def createPicturesFolder():
    myDir = []
    for pathnames,dirnames,filenames in os.walk(os.getcwd()):
            myDir.extend(dirnames)
    for directory in myDir:
        if directory == "pictures":
            return -1
    try:
        os.mkdir("pictures")
    except:
        raise Exception("Could not create pictures folder")
    
def main():
    updateDisplay()
    printL(1,"Loading complete")
    SCREENSHOT_FILENAME = "pictures/screenshot" #+ a counter number + JPG
    GIF_WINDOW_SIZE = (900, 400)
    
    numbers = []
    running = True
    display.algorithmBox.add_options(list(algorithmsDict.keys()))

    current_alg = None
    alg_iterator = None

    timer_delay = time()
    
    #One keeps track of how many files have been created, the other how many total images
    GIF_picture_counter = 0
    GIF_skip_image_counter = 0
    
    #Just to make sure nothing from prev runs is left
    deleteTempFiles()
    
    #Create pictures if it does not exists
    createPicturesFolder()
    
    while running:
        updateDisplay()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and display.do_sorting:
                display.paused = not display.paused
                display.timer_space_bar = time()

            display.updateWidgets(event)

        #display.delay = (display.delayBox.value-display.delayBox.rect.x-6)/1000 # delay is in ms
        display.delay = (display.delayBox.value)/1000 # delay is in ms

        if display.playButton.isActive: # play button clicked
            try:
                if int(display.sizeBox.text) > 1000:
                    # This is limitation because of RAM. size = 100 needs 2GB of RAM, so 120 is for some reason significantly higher
                    printL(1,("GIF cannot be created for size > 1000"))
                else:
                    printL(1,"-------------------------------")
                    printL(1,("Creating animation"))
                    display.do_sorting = True
                    display.playButton.isActive = False
                    current_alg = display.algorithmBox.get_active_option()
                    display.numBars = int(display.sizeBox.text)
                    numbers = [randint(10, 400) for i in range(display.numBars)]  # random list to be sorted
                    alg_iterator = algorithmsDict[current_alg](numbers, 0, display.numBars - 1)  # initialize iterator
                display.playButton.isActive = False
            except:
                raise ValueError("Text in size field is not a number")

        if display.stopButton.isActive: # stop button clicked
            printL(1,("Stopping animation"))
            display.stopButton.isActive = False
            display.do_sorting = False
            display.paused = False
            try: # deplete generator to display sorted numbers
                while True:
                    numbers, redBar1, redBar2, blueBar1, blueBar2 = next(alg_iterator)
            except StopIteration:
                pass
            #Check if user wants GIF, then delete temp files. No gif is possible because early stop
            if True:
                deleteTempFiles()
                GIF_picture_counter = 0
                GIF_skip_image_counter = 0
                
        #GIF needs it's own thing
        #screenshot = pygame.Surface(GIF_WINDOW_SIZE)
        #screenshot.blit(display.screen, (0,0))
        
        if display.do_sorting and not display.paused: # sorting animation
            try:
                if True:
                    numbers, redBar1, redBar2, blueBar1, blueBar2 = next(alg_iterator)
                    display.drawInterface(numbers, redBar1, redBar2, blueBar1, blueBar2)
                    #If GIF is to be output, a picture needs to be generated and saved temporarily
                    if True:
                        #If less then 300, take every size/100 picture
                        #ergo size = 100 => every picture, size = 300 => every third picture
                        if int(display.sizeBox.text) <= 200:
                            takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,display.screen)
                            GIF_picture_counter +=1
                        #If size > 300, then we need to take draastically less pictures
                        else:
                            if int(GIF_skip_image_counter) % int(10) == 0:
                                takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,display.screen)
                                GIF_picture_counter +=1
                                GIF_skip_image_counter = 0
                            GIF_skip_image_counter +=1
                    timer_delay = time()
                    
            except StopIteration:
                display.do_sorting = False
                #If program stops because end of sorting, gif needs to be created if selected
                if True: #Check if GIF was requested
                    #Create green bars
                    a_set = set(range(display.numBars))
                    display.drawInterface(numbers, -1, -1, -1, -1, greenRows=a_set)
                    #Make sure they are saved for a second
                    takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, display.screen)
                    GIF_picture_counter += 1
                    takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, display.screen)
                    GIF_picture_counter += 1
                    takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, display.screen)
                    GIF_picture_counter += 1
                    # Call function for GIF
                    CreateGIF(GIF_picture_counter,SCREENSHOT_FILENAME)
                    #Reset counter
                    GIF_picture_counter = 0
                    GIF_skip_image_counter = 0
                
        elif display.do_sorting and display.paused: # animation paused
            display.drawInterface(numbers, -1, -1, -1, -1)
        else: # no animation
            a_set = set(range(display.numBars))
            display.drawInterface(numbers, -1, -1, -1, -1, greenRows=a_set)

if __name__ == '__main__':
    main()