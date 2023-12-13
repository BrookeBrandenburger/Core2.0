import libpyAI as ai
import math
import random
import random
import os 
from os import path

from chromosome import *

def initializeAgent(input_chrome = generateChromosome()):
    # Chomosome Controllers! #[[loop1], [loop2]]
    global chrome # Decoded chromosome
    global raw_chrome_values
    global current_loop # A chromosome is made up of 16 loops
    global current_loop_idx
    global current_gene_idx # Refers to an action within a loop (jump/action)
    global chromosome
    global prev_score
    global score

    prev_score = 0
    score = 0

    chromosome = input_chrome
    #writeChromosomeToFile(chromosome, "output_chromosome.txt")#Can call whatever 
    #chrome = readChrome(chromosome)
    #current_loop_idx = 0 # Current Loop Number
    #current_loop = chrome[current_loop_idx]
    #current_gene_idx = 0 # Current gene Number within a given loop

def earnedKill(ai):
    global score
    global prev_score
    global chromosome
   
    filename = "selChrome_0.txt"

    while os.path.exists(("data/" + filename)):
        index = int((filename.split("_")[1]).split(".")[0]) # Get the number at end of file name
        index = str(index+1)
        filename = "selChrome_{}.txt".format(index)

    # Score increment indicates a kill
    if score > prev_score:
        writeChromosomeToFile(chromosome, filename)
        ai.talk('New Chrome File -' + filename)

def died(ai):
    global score
    global prev_score
    global chromosome
    
    message = (ai.scanMsg(0)).split("-")
    # Score change and message with hyphen (indicating killed instead of wall collision)
    if score != prev_score: 
        if len(message) > 1:
            print("Death and death message found")
            print(message)
            new_chromosome_file_name = "data/" + str(message[1])

            new_chromosome = None
            with open(new_chromosome_file_name, 'r') as f:
                new_chromosome = eval(f.read())

            initializeAgent(new_chromosome)


def AI_loop():
    try:
        #speed = sensors[0]
        #enemy_dist = sensors[1]
        #wall_dist= sensors[2] # minimum wall distance
        #closestBulletDistance = sensors[3]
        #enemy_x = sensors[4]
        #enemy_y = sensors[5]
        #x = sensors[6]
        #y = sensors[7]
        
        # Self details
        # handicap
        speed = int(ai.selfSpeed())
        X = int(ai.selfX())
        Y = int(ai.selfY())
        
        # get information
        heading = int(ai.selfHeadingDeg())
        tracking = int(ai.selfTrackingDeg())
        
        # Enemy Details
        closestShipId = int(ai.closestShipId())

        ENEMY_SPEED = None
        ENEMY_DIST = None
        ENEMY_X = None
        ENEMY_Y = None
        ENEMY_HEADING = None

        if closestShipId != -1:
            ENEMY_SPEED = float(ai.enemySpeedId(closestShipId))
            ENEMY_DIST = float(ai.enemyDistanceId(closestShipId))
            ENEMY_X = int(ai.screenEnemyXId(closestShipId))
            ENEMY_Y = int(ai.screenEnemyYId(closestShipId))
            ENEMY_HEADING = float(ai.enemyHeadingDegId(closestShipId))

        if ai.shotDist(0) > 0:
            closestBulletDistance = ai.shotDist(0)
        else:
            closestBulletDistance = math.inf
        
        # store in array so we can easily find the shortest feeler
        feelers = []
        frontWall = ai.wallFeeler(500, heading)
        leftWall = ai.wallFeeler(500, heading + 90)
        rightWall = ai.wallFeeler(500, heading - 90)
        trackWall = ai.wallFeeler(500, tracking)
        rearWall = ai.wallFeeler(500, heading - 180)
        backLeftWall = ai.wallFeeler(500, heading + 135)
        backRightWall = ai.wallFeeler(500, heading - 135)
        frontLeftWall = ai.wallFeeler(500, heading + 45)
        frontRightWall = ai.wallFeeler(500, heading - 45)
        rightWall1 = ai.wallFeeler(500, heading - 60)
        rightWall2 = ai.wallFeeler(500, heading - 120)
        leftWall1 = ai.wallFeeler(500, heading + 60)
        leftWall2 = ai.wallFeeler(500, heading + 120)
        slightRight = ai.wallFeeler(500, heading - 85)
        slightLeft = ai.wallFeeler(500, heading + 85)
        feelers.append(frontWall)
        feelers.append(leftWall)
        feelers.append(rightWall)
        feelers.append(trackWall)
        feelers.append(rearWall)
        feelers.append(backLeftWall)
        feelers.append(backRightWall)
        feelers.append(frontLeftWall)
        feelers.append(frontRightWall)
        feelers.append(rightWall1)
        feelers.append(rightWall2)
        feelers.append(leftWall1)
        feelers.append(leftWall2)
        feelers.append(slightRight)
        feelers.append(slightLeft)
        
        wall_dist = min(feelers)

        global current_loop_idx
        global chrome # Decoded chromosome
        global current_loop
        global current_gene_idx
        global chromosome
	    
        
        # Kill/Death Tracking
        global score
        global prev_score
        earnedKill(ai) # Check for kill
        died(ai) # If killed, get new chromosome

        # NOTE: Do we want to crossover with a random new chroomsome if we crash ourselves?
        prev_score = score
        score = ai.selfScore()



    except Exception as e:
        print("Exception")
        print(e)
        ai.quitAI()

def main():
    initializeAgent([['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000'], ['000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000', '000000000']])

    ai.start(AI_loop, ["-name", "HumanCore", "-join", "localhost"])


if __name__ =="__main__":
    main()
