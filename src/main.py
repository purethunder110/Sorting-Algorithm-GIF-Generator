import sys

#Define basic trace_function
def show_trace(event=""):
    print("An error has occured, printing useful info:")
    print(sys.version)
    print(sys.version_info)
    print(event)
    sys.exit(0)

#Carefully import stuff
try:
    from random import randint
    from time import time
    from algs import algorithmsDict
    from os import rmdir, walk, getcwd, system, mkdir, remove,path,environ,putenv
    from gc import collect
    import imageio.v3 as iio
    #import av #Temporary, this should be changed to only import needed functions
    import pygame
except ImportError:
    show_trace()


#Global variables
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

TEXTLOG = []
TEXTLOG_UPDATE = True
DEBUG = False
CURRENT_OUTPUT_FORMATS = ["GIF","MP4"]
SCREENSHOT_FILENAME = "pictures/screenshot"  # + a counter number + JPG
BENCHMARK_TEXT_FILE = "temp_file_for_benchmark.txt"

#printL types:
# 1 = normal log message
# 2 = reserved for progress indication
# 3 = Warning message
# 4 = Reserved for debug use

#Generating gifs requires placing files in subfolder and then loading them.
#This deletes everything except gif
def deleteTempFiles():
    try:
        myFiles = []
        myDir = []
        for pathnames,dirnames,filenames in walk("pictures"):
            myFiles.extend(filenames)
            myDir.extend(dirnames)
        for files in myFiles:
            remove("pictures/" + files)
        for directories in myDir:
            rmdir("pictures/" + directories)
    except:
        raise EIO("Could not delete files in subfolder!")

# For some uses, having an existing sorting.gif file is a problem
# Therefore, this function deletes that file using os lib
def deleteExistingFile(name):
    if path.exists(name):
        try:
            remove(name)
            printL(1, f"Removed {name}")
        except:
            printL(3,f"Could not remove {name}")

#Call function with type according to above (eg 0 for normal log)
# and a string with whatever should be added to log
def printL(type,addition):
    global TEXTLOG
    global TEXTLOG_UPDATE
    TEXTLOG_UPDATE = True
    TEXTLOG.append((type,addition))

# Function that correctly inserts new progress item into log
def printProgress(progress):
    global TEXTLOG
    global TEXTLOG_UPDATE
    TEXTLOG_UPDATE = True
    #Insert at pos 0
    TEXTLOG.insert(0,(2, progress))

# Prints progress bar, only to be called if
# in log values of type 2 exists and terminal is clear
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

def printLimitations(myType):
    printL(myType,"Limitations exceeded. For reference see below")
    printL(myType,"Current program limitations:")
    printL(myType,"Size < 1000")
    printL(myType, "if display values in bar, Size < 20")
    printL(myType,"Loops must be < 9999, set to 0 for Inf")
# Given a type, removes all entries of that type from log

def checkVersionOfPYAV():
    with iio.imopen("temp.mp4","w",plugin="pyav") as newVideo:
        exists = False
        for attr in dir(newVideo):
            if "init_video_stream" == attr:
                exists = True
        if exists:
            printL(4,"Correct version of pyav detected")
            deleteExistingFile("temp.mp4")
            #This is kinda wierd, but is really just so control-flow works correctly.
            return
        else:
            print("Incorrect version of pyav detected")
            print("Exiting program")
    deleteExistingFile("temp.mp4")
    sys.exit(0)

def deleteType(theType):
    global TEXTLOG
    counter = 0
    while True:
        if counter >= len(TEXTLOG)-2:
            return True
        type,value = TEXTLOG[counter]
        if type == theType:
            TEXTLOG.pop(counter)
            counter = counter-3
        counter +=1

# Function that clears terminal and write new info.
# To activate, set TEXTLOG_UPDATE = True
# Usually, there is no need to run the function after setting TEXTLOG_UPDATE bc it will run soon anyway.
def updateDisplay(terminal = False):
    global TEXTLOG
    global TEXTLOG_UPDATE
    if terminal:
        currentMax = 0
        for (type,value) in TEXTLOG:
            if type != 2:
                print(value)
            elif currentMax < value:
                currentMax = value
        if currentMax > 0:
            print(f"Current progress in writing to disk:{currentMax}%")
        TEXTLOG.clear()
        return -1
    # Without this, much resources would be wasted on rewriting log terminal display
    if not TEXTLOG_UPDATE:
        return -1
    TEXTLOG_UPDATE = False
    #runTime = time.strftime("%H:%M:%S", time.localtime(time.time() - startUpTime - 60 * 60))
    system("clear")
    printSign()
    #print(str(runTime))
    maxProgress = -1
    for type,value in TEXTLOG:
        if type == 2:
            if value > maxProgress:
                maxProgress = value
    if -1 < maxProgress < 100:
        printProgressBar(maxProgress)
        print("--------------------------------------------")
    for type,value in TEXTLOG:
        if type == 1:
            print(value)
        if type == 3:
            print(f"{bcolors.WARNING} Warning: {value} {bcolors.ENDC}")
        if type == 4 and DEBUG:
            print(f"{bcolors.OKBLUE} Debug: {value} {bcolors.ENDC}")

def writeGifFile(listOfImages,numberOfLoops,delay):
    newGif = iio.imopen('sorting.gif', "w", plugin="pillow")
    newGif.write(listOfImages, duration=int(delay), loop=numberOfLoops, optimize=True)
    newGif.close()

# Create GIF using existing files
def createGIF(counter,SCREENSHOT_FILENAME,delay,loops,terminal=False):
    updateDisplay(terminal)
    #Idea is that pictures are generated with numbers 0 to some MAX
    printL(1,"Trying to generate GIF, this may freeze the program and take a while")
    fileNames = []
    if loops == "Inf":
        loops = 0
    for i in range(0,counter):
        fileNames.append(f"{SCREENSHOT_FILENAME}{str(i)}.jpg")
    #This will start to load in individual pictures into gif engine
    deleteExistingFile("sorting.gif")
    printL(1, f"Adding {str(delay)} ms delay for each image in GIF")
    printL(4, "Accurate gif settings is applied \n Therefore every frame from animation will be in GIF.")
    printL(4, "This increases time to generate, but also more accurately displays how sorting function works.")
    printL(4, f"Total number of recorded images: {str(len(fileNames))}")
    updateDisplay(terminal)
    listOfImages = []
    for (counter, filename) in enumerate(fileNames):
        if counter % 1000 == 1:
            updateDisplay(terminal)
        listOfImages.append(iio.imread(filename))
        printProgress(int(((counter) / len(fileNames)) * 100*0.7))
    printL(1, "Writing GIF to disk")
    writeGifFile(listOfImages,loops,delay)
    printProgress(100)
    updateDisplay(terminal)
    #Del latest list, this does NOT decrease current RAM usage,
    #but makes next round use the same memory area instead
    printL(1,"Cleaning up remaining files")
    del listOfImages
    del fileNames
    collect()
    printL(1,"GIF generation complete as sorting.gif")
    #Delete all files in folder
    #deleteTempFiles()
    deleteType(2)
    updateDisplay(terminal)

# Create MP4 using existing files
def createMP4(numberOfPictures,SCREENSHOT_FILENAME,delay,terminal=False):
    updateDisplay(terminal)
    #Idea is that pictures are generated with numbers 0 to some MAX
    printL(1,"Trying to generate MP4, this may freeze the program and take a while")
    fileNames = []
    for i in range(0,numberOfPictures):
        fileNames.append(f"{SCREENSHOT_FILENAME}{str(i)}.jpg")
    #This will start to load in individual pictures into gif engine
    deleteExistingFile("sorting.mp4")
    printL(1, f"Adding {str(delay)} ms delay for each image in MP4")
    printL(4, "Accurate MP4 settings is applied \n Therefore every frame from animation will be in MP4.")
    printL(4, "This increases time to generate, but also more accurately displays how sorting function works.")
    printL(4, f"Total number of recorded images: {str(len(fileNames))}")
    printL(4,f"Ignoring looping options because MP4 format does not support")
    updateDisplay(terminal)
    with iio.imopen("sorting.mp4","w",plugin="pyav") as newVideo:
        newVideo.init_video_stream("mpeg4",fps=30)
        frameCounter = int((delay * 30)/1000) #Formula to get number of repeat images for delay
        if frameCounter < 1:
            frameCounter = 1
        for (counter, filename) in enumerate(fileNames):
            if counter % 500 == 458 or numberOfPictures < 50:
                updateDisplay(terminal)
                printProgress(int(((counter) / len(fileNames)) * 100))
            aFrame = iio.imread(filename) #So we don't read it more than once
            for _ in range(frameCounter):
                newVideo.write_frame(aFrame)
    printL(1, "Writing MP4 to disk")
    printProgress(100)
    updateDisplay(terminal)
    #Del latest list, this does NOT decrease current RAM usage,
    #but makes next round use the same memory area instead
    printL(1,"Cleaning up remaining files")
    del fileNames
    collect()
    printL(1,"MP4 generation complete as sorting.mp4")
    #Delete all files in folder
    deleteTempFiles()
    deleteType(2)
    updateDisplay(terminal)

#Given a list of filenames, it returns what number the highest file has.
def getMaxNumber(files):
    currentMax  = -1
    for item in files:
        myNumber = int(item[len(SCREENSHOT_FILENAME):len(item)-4])
        if myNumber > currentMax:
            currentMax = myNumber
    return currentMax

#Given a picture counter & screenshot item, takes and saves a picture of animation
def takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot):
    if not display.includeSettingsInOutput:
        pygame.image.save(screenshot, f"{SCREENSHOT_FILENAME}{str(GIF_picture_counter)}.jpg")
    else:
        pygame.image.save(display.screen, f"{SCREENSHOT_FILENAME}{str(GIF_picture_counter)}.jpg")

# We need a place to write pictures currently
# Yes, this is bad design.
# Checks if picture folder exists, and if not it is created.
def createPicturesFolder():
    myDir = []
    for pathnames,dirnames,filenames in walk(getcwd()):
            myDir.extend(dirnames)
    for directory in myDir:
        if directory == "pictures":
            return -1
    try:
        mkdir("pictures")
    except:
        raise Exception("Could not create pictures folder")

def listAsStringGood(myList):
    valid_formats = ""
    for option in myList:
        valid_formats = f"{valid_formats},{option}"
    return valid_formats


def createPicturesForOutput(TERMINAL_MODE,GIF_picture_counter,GIF_skip_image_counter,numbers,alg_iterator,GIF_WINDOW_SIZE):
    global SCREENSHOT_FILENAME
    try:
        while True:
            if len(numbers) < 50 or GIF_picture_counter % 1000 == 5:
                updateDisplay(TERMINAL_MODE)
                printL(4,f"Current pic count:{GIF_picture_counter}")
            numbers, redBar1, redBar2, blueBar1, blueBar2 = next(alg_iterator)
            display.drawInterface(numbers, redBar1, redBar2, blueBar1, blueBar2)
            screenshot = pygame.Surface(GIF_WINDOW_SIZE)
            screenshot.blit(display.screen, (0, 0))
            # Pictures needs to be generated and saved temporarily
            if len(numbers) <= 200:
                takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
                GIF_picture_counter += 1
            # If size > 200, then we need to take drastically less pictures
            else:
                if int(GIF_skip_image_counter) % int(5) == 1:
                    takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
                    GIF_picture_counter += 1
                    GIF_skip_image_counter = 0
                GIF_skip_image_counter += 1

    except StopIteration:
        # If program stops because end of sorting, gif needs to be created if selected
        # Create green bars
        a_set = set(range(display.numBars))
        display.drawInterface(numbers, -1, -1, -1, -1, greenRows=a_set)
        # Make sure they are saved for a second
        takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
        GIF_picture_counter += 1
        takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
        GIF_picture_counter += 1
        takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
        GIF_picture_counter += 1
        # Call function for GIF
        if not TERMINAL_MODE:
            if display.outputFormatBox.get_active_option() == "GIF":
                createGIF(GIF_picture_counter, SCREENSHOT_FILENAME, int(display.delay), int(display.loopBox.get_value()))
            else:
                createMP4(GIF_picture_counter, SCREENSHOT_FILENAME, int(display.delay))
        # Turn off sorting
        display.do_sorting = False
        if TERMINAL_MODE:
            return (GIF_picture_counter,GIF_skip_image_counter)


def main():
    updateDisplay()
    printL(4,"Function import and program load completed")

    #Create display
    display.createDisplay(pygame.SHOWN)

    #Init numbers and other important vars
    numbers = []
    running = True
    display.algorithmBox.add_options(list(algorithmsDict.keys()))
    display.outputFormatBox.add_options(CURRENT_OUTPUT_FORMATS)

    alg_iterator = None
    
    #One keeps track of how many files have been created, the other when to skip images
    GIF_picture_counter = 0
    GIF_skip_image_counter = 0

    #Used for rendering window
    GIF_WINDOW_SIZE = (900, 400)
    
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

        if display.playButton.isActive: # play button clicked
            try:
                if int(display.sizeBox.text) > 1000 or \
                        (display.displayValuesInOutput and int(display.sizeBox.text) > 49) or \
                        (display.loopBox.get_value() > 9999) or \
                        (display.loopBox.get_value() == "") or \
                        (display.sizeBox.text == ""):
                    # This is limitation because of RAM. size = 100 needs 2GB of RAM, so 120 is for some reason significantly higher
                    printL(3,("Halting output creation"))
                    printLimitations(3)
                else:
                    printL(1,"-------------------------------")
                    printL(1,("Creating animation"))
                    GIF_picture_counter = 0
                    GIF_picture_counter = 0
                    display.do_sorting = True
                    display.playButton.isActive = False
                    current_alg = display.algorithmBox.get_active_option()
                    display.numBars = int(display.sizeBox.text)
                    if display.numBars > 20 and display.displayValuesInOutput:
                        printL(3,"Will not render values in bars because number of bars > 20")
                    numbers = [randint(10, 400) for i in range(display.numBars)]  # random list to be sorted
                    alg_iterator = algorithmsDict[current_alg](numbers, 0, display.numBars - 1)  # initialize iterator
                display.playButton.isActive = False
            except ValueError:
                printL(4,"Text in size field is not a number")

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
            #Delete temp files. No gif is possible because early stop
            deleteTempFiles()
            GIF_picture_counter = 0
            GIF_skip_image_counter = 0
                
        #GIF may need own thing
        #screenshot = pygame.Surface(GIF_WINDOW_SIZE)
        #screenshot.blit(display.screen, (0,0))
        
        if display.do_sorting and not display.paused: # sorting animation
            #This is needed bc both terminal mode and GUI mode needs to exist
            createPicturesForOutput(False, GIF_picture_counter,GIF_skip_image_counter,numbers,alg_iterator,GIF_WINDOW_SIZE)
            display.do_sorting = False
            GIF_picture_counter = 0
            GIF_skip_image_counter = 0
        elif display.do_sorting and display.paused: # animation paused
            display.drawInterface(numbers, -1, -1, -1, -1)
        else: # no animation
            a_set = set(range(display.numBars))
            display.drawInterface(numbers, -1, -1, -1, -1, greenRows=a_set)

def validateInput(type,input):
    if type == "int":
        try:
            return (True,int(input))
        except TypeError:
            return (False,input)
        except ValueError:
            return (False, input)
    return (None,input)


if __name__ == '__main__':
    available_args = ["-f","-d","-s","-include","-l","-v","-a","-bench"]
    if len(sys.argv) > 1:
        if sys.argv[1] == "help" or sys.argv[1] == "HELP" or sys.argv[1] == "Help":
            print("--------------------------------------------------------------")
            print(f"Sorting Algorithm GIF Generator by TheStar19")
            print(f"https://github.com/thestar19/Sorting-Algorithm-GIF-Generator")
            print(f"A fork of Sorting Algorithm Visualizer by LucasPilla")
            print(f"A GIF or video can be created either by:")
            print(f"    1) Interacting with the GUI by running python3 src/main.py")
            print(f"    2) Only using the terminal by providing arguments")
            print(f"Available sorting algorithms:{list(algorithmsDict.keys())}")
            print(f"Available args:{available_args}")
            print(f"Valid inputs:")
            print(f"    Format: -f => GIF or MP4")
            print(f"    Delay for each pic: -d => 1-3000")
            print(f"    Size of array to sort: -s => 5-1000")
            print(f"    Include numbers in bars in output: -include => true/false")
            print(f"    Number of loops (GIF ONLY): -l => 0(inf)-9999")
            print(f"    Output debug info (verbose): -v => true/false")
            print(f"    Reserved use for benchmark: -bench => true/false")
            print("--------------------------------------------------------------")
            sys.exit(0)
        if sys.argv[1] == "-v" or sys.argv[1] == "-V":
            printL(4,"Debug enabled")
            DEBUG = True
    #Check if correct software is installed
    checkVersionOfPYAV()
    #Check for any args in program init
    if len(sys.argv) > 2:
        all_args = sys.argv.copy()
        all_args.pop(0)
        print("--------------------")
        instructions = []
        while True:
            if len(all_args) > 1:
                if all_args[0] in available_args:
                    instructions.append((all_args.pop(0),all_args.pop(0)))
                else:
                    print(f"Incorrects arg options")
                    print(f"Available args:{available_args}")
                    sys.exit(0)
            else:
                break
        output_format = "GIF"
        output_delay = 1
        output_size = 100
        add_numbers_to_bars = False
        output_loops = 0
        output_alg = "insertion"
        benchmark = False
        for inst,value in instructions:
            #Check for output format
            if inst == "-f" and value in CURRENT_OUTPUT_FORMATS:
                output_format = value
            elif inst == "-f" :
                print(f"Incorrect args, -f value {value} is not supported")
                sys.exit(0)
            #Check for debug mode, verbose
            elif (inst == "-v" or inst == "-V") and value == "true":
                DEBUG = True
            elif inst == "-v" or inst == "-V":
                print(f"Incorrect args, -v value {value} is not true or false")
                sys.exit(0)
            #Check for including numbers in bars or entire GUI
            elif inst == "-include" and value == "numbers":
                add_numbers_to_bars = True
            elif inst == "-include":
                print(f"Incorrect args, -include value {value} is not text \"numbers\"")
                sys.exit(0)
            # Check for which algorithm to run
            elif inst == "-a" and value in list(algorithmsDict.keys()):
                output_alg = value
            elif inst == "-a":
                print(f"Incorrect args, -a value {value} is not in accepted sorting alg")
                sys.exit(0)
            elif inst == "-bench" and value == "true":
                benchmark = True
            elif inst == "-bench":
                print(f"Incorrect args, -bench value {value} is not true or false")
                sys.exit(0)
            isInt,newValue = validateInput("int",value)
            if isInt and inst in "-d -s -l":
                #Check for delay value
                if inst == "-d" and 1 <= int(newValue) <= 3000:
                    output_delay = int(newValue)
                elif inst == "-d" :
                    print(f"Incorrect args, -d value {newValue} is not an int between 1 and 3000")
                    sys.exit(0)
                #Check for size value
                elif inst == "-s" and 5 < int(newValue) <= 1000:
                    output_size = int(newValue)
                elif inst == "-s":
                    print(f"Incorrect args, -s value {newValue} is not an int between 5 and 1000")
                    sys.exit(0)
                #Check for number of loops
                elif inst == "-l" and 0 <= int(newValue) <= 9999:
                    output_loops = int(newValue)
                elif inst == "-l":
                    print(f"Incorrect args, -l value {newValue} is not 0 <= value <= 9999")
                    sys.exit(0)
        print(f"Creating output with these settings:")
        print(f"    Output format={output_format}")
        print(f"    Delay for each pic={output_delay}")
        print(f"    Number of elements in list to sort={output_size}")
        print(f"    Include numbers in bars={add_numbers_to_bars}")
        print(f"    Sorting alg={output_alg}")
        if output_format == "GIF":
            print(f"    Number of loops={output_loops}")


        # Just to make sure nothing from prev runs is left
        deleteTempFiles()
        # Create pictures if it does not exists
        createPicturesFolder()
        #Okay, so get this.
        # If I import display before this, the window will render
        # If I first do putenv & environ crap, then no window.
        # For terminal mode, having no display thing pop up is a good feature.
        putenv('SDL_VIDEODRIVER', 'fbcon')
        environ["SDL_VIDEODRIVER"] = "dummy"
        import display as display
        numbers = [randint(10, 400) for i in range(output_size)]  # random list to be sorted
        alg_iterator = algorithmsDict["insertion"](numbers, 0, output_size - 1)  # initialize iterator

        #Okay so, for the display module to work this has to be set.
        # So honestly, instead of doing extra work this should be solved some other way.
        display.algorithmBox.add_options(list(algorithmsDict.keys()))
        display.outputFormatBox.add_options(CURRENT_OUTPUT_FORMATS)
        display.numBars = output_size
        GIF_picture_counter,_ = createPicturesForOutput(True,0,0,numbers,alg_iterator,(900, 400))
        if output_format == "GIF":
            createGIF(GIF_picture_counter,SCREENSHOT_FILENAME,output_delay,output_loops,True)
        else:
            createMP4(GIF_picture_counter,SCREENSHOT_FILENAME,output_delay,True)
        if benchmark:
            deleteExistingFile(BENCHMARK_TEXT_FILE)
            f = open(BENCHMARK_TEXT_FILE,"w")
            f.write(f"pictures={GIF_picture_counter}")
            f.close()
        print("GIF creation finished!")
        sys.exit()
        #all_args = sys.argv.split[]
    # Yes, this is a really wierd place to import stuff
    # But this is needed for current version of program
    import display as display
    main()


