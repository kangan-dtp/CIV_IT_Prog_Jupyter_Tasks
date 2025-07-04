from machine import Pin, PWM
from time import sleep
import os
import random
import json

# Define buttons
buttons = [
    Pin(0, Pin.IN, Pin.PULL_UP), # Green
    Pin(1, Pin.IN, Pin.PULL_UP), # Red
    Pin(2, Pin.IN, Pin.PULL_UP), # Blue
    Pin(3, Pin.IN, Pin.PULL_UP) # Yellow
]

# Define RGB light pins
lights = [
    Pin(6, Pin.OUT), # Green
    Pin(7, Pin.OUT), # Red
    Pin(8, Pin.OUT), # Blue
    Pin(9, Pin.OUT)  # Yellow
]

# Define buzzer
buzzer = PWM(Pin(10))
buzzer.freq(2000)
buzzer.duty_u16(0) # Turn the sound off
slientMode = False # Set to true if you want to turn off the buzzer

playerName = "No name given"
playerScore = 0 # Player gets a point for every correct sequence
leaderboardFile = "leaderboard.json"

# Define button sounds
button_tones = [196, 261, 329, 784]

melodies = [

    # Start game
    [(660, 0.2), (0, 0.05),  # "3"
    (740, 0.2), (0, 0.05),  # "2"
    (830, 0.2), (0, 0.05),  # "1"
    (880, 0.1), (988, 0.1), (1047, 0.1),  # Quick build-up
    (1320, 0.3)]

]

def play_level_up_tune():
    for tone in [329, 392, 659, 523, 587, 784]:
        playTone(tone, 0.15)
        sleep(0.15)



#################################################
#           Setup function
#
# 1. Checks lights and buzzer.
# 2. Make sure we have a leaderboard file
# 3. Ask for player's name
# 4. Start the game
#################################################
def setup():
    global playerName

    freq = 500 # Temporary variable to track current freqency of buzzer
    
    setlight("off")

    if slientMode == False:
        buzzer.duty_u16(5000) # Turn on buzzer
    
    # Go through each colour of the rgb light and test each one. Also turn up the frequency of the buzzer each time.
    for light in lights:
        light.on() # Turn on one of the lights
        
        buzzer.freq(freq) # Set the buzzer frequency
        sleep(0.2) # Sleep
        
        light.off() # Turn off this light
        freq += 500 # Add to frequency
    
    buzzer.freq(freq)
    setlight("all") # Test all lights on at once
    sleep(0.2)
        
    buzzer.duty_u16(0) # Turn off buzzer
    setlight("off")

    # Check if the leaderboard text file exists
    if leaderboardFile in os.listdir():
        print("Leaderboard file already created.")
    else:
        # Create the leaderboard file as it doesn't exist
        with open(leaderboardFile, "w") as file:
            file.write("{\"top5\": []}")
        print("Created the leaderboard file.")  
    
    playerName = input("Welcome to Colour Clash: Memory Edition! Enter your player name: ") # Ask for player name
    
    # Start the game
    beginTurn()



# Helper function to set the color of the RGB light
# state can be: "all", "on", or "off"
# light can be 0, 1, 2, 3
def setlight(state = "all", light = 0):
    # Turn off all lights
    for l in lights:
        l.off()
    
    # Then only turn on the requested light(s) if applicable
    if state == "all":
        for l in lights:
            l.on()
    elif state != "off":
        lights[light].on()



# Helper function to play a tone through the buzzer
def playTone(freq, duration = 0.5):
    if slientMode == False:
        buzzer.freq(freq)
        buzzer.duty_u16(30000)
        sleep(duration)
        buzzer.duty_u16(0)
    

# Helper function to play music
def playMusic(notes):
    for note in notes:
        if note[0] != 0:
            playTone(note[0], note[1])


# Helper function to add leaderboard entries
def addLeaderboardEntry(name, score):
    leaderboard = {}

    # Read the leaderboard file
    try:
        with open(leaderboardFile, "r") as file:
            leaderboard = json.loads(file.read())

    # Handle if we have issues
    except json.JSONDecodeError:
        print("There was a problem loading the leaderboard.")
    except FileNotFoundError:
        print("The leaderboard does not exist.")

    
    # Stop duplicate names from being in the leaderboard
    for entry in leaderboard["top5"]:
        if entry["name"] == name:
            if score >= entry["score"]:
                leaderboard["top5"].remove(entry)
                
    # Create a new entry
    entry = {
        "name": name,
        "score": score
    }
    leaderboard["top5"].append(entry)


    # Sort the scores from high to low
    # For each entry in the list, get the score and automatically rank them from high to low
    leaderboard["top5"].sort(key=lambda entry: entry["score"], reverse=True)

    # Then cut back the list to only 5 if applicable
    leaderboard["top5"] = leaderboard["top5"][:5]

    # Finally, save the leaderboard
    with open(leaderboardFile, "w") as file:
        file.write(json.dumps(leaderboard))



# Print the leaderboard
def showLeaderboard():
    try:
        with open(leaderboardFile, "r") as file:
            leaderboard = json.loads(file.read())

            place = 1
            for entry in leaderboard["top5"]:
                print(str(place) + ". " + entry["name"] + ": " + str(entry["score"])) # eg: 1. John Smith: 5
                place += 1


    except json.JSONDecodeError:
        print("There was a problem loading the leaderboard.")
    except FileNotFoundError:
        print("The leaderboard does not exist.")
    
    

############################################################################
# Function to start a turn.
# 1. Make a random colour based on a number
# 2. Add that colour to a "memory array"
# 3. Flash LED lights from the memory array
# 4. For each entry in the memory array ->
#       - Wait for one of the buttons to be pressed
#           - If that colour button matches the index of the array, continue.
#           - Else, end the game.
#############################################################################
def beginTurn():
    global playerName
    global playerScore

    gameStatus = 'ok'
    memoryArray = []
    playerScore = 0 # Reset player score

    playMusic(melodies[0])

    print("Let the game begin!")


    while gameStatus == 'ok':
        sleep(1)

        # Set colour and add it to the memory array
        colour = random.randint(0, 3) # Generates a random number from 0 - 3. Each one represents a colour
        memoryArray.append(colour)

        # Go through the memory array and flash the light and make a sound
        for memoryColour in memoryArray:
            setlight("on", memoryColour)
            playTone(button_tones[memoryColour], 0.4)
            sleep(0.4)
            setlight("off")
            sleep(0.1)


        # For each colour in the memory array, wait for a button to be pressed and check if correct
        for memoryColour in memoryArray:
            if gameStatus == "fail":
                break

            # Wait for button to be pressed        
            buttonPressed = False
            while buttonPressed == False:
                for button in buttons:
                    if button.value() == 0:
                        if buttons.index(button) == memoryColour:
                            # Correct button
                            setlight("on", memoryColour)
                            playTone(button_tones[memoryColour], 0.4)
                            setlight("off")
                            gameStatus = 'ok'
                        else:
                            # Wrong button
                            gameStatus = 'fail'

                        buttonPressed = True


        # Once the sequence has ended and player hasn't failed
        if gameStatus == "ok":
            playerScore += 1
            print("Correct! Current score: " + str(playerScore))   
            sleep(0.5)
            play_level_up_tune()
            sleep(0.5)



    # Game over
    if gameStatus == "fail":
        print("\nGame over! Your score:", playerScore)
        playTone(622, 0.3)
        sleep(0.3)
        playTone(587, 0.3)
        sleep(0.3)
        playTone(554, 0.3)
        sleep(0.3)
        for _ in range(1):
            for pitch in range(-10, 11): 
                playTone((523 + pitch), 0.1) 
        sleep(0.5)

        # Record score
        addLeaderboardEntry(playerName, playerScore)
        showLeaderboard()
        

    # Offer for the player to start again
    if str(input("Would you like to play again? (y/n) ")) == "y":
        if str(input("Continue playing as " + playerName + "? (y/n) ")) == "y":
            beginTurn()
        else:
            setup()
    else:
        print("Hope you enjoyed the game!")


# Run the setup function
setup()