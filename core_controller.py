import libpyAI as ai
import math
import random
import random
import os 
from os import path
import sys
import traceback

from chromosome import *

# Sets all needed values for a new agent, by default creates a new chromosome, a chromosome can be passed in.
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
    global framesPostDeath # 

    framesPostDeath = 0

    chromosome = input_chrome
    chrome = readChrome(chromosome)
    print("Chromosome: {}".format(chromosome))
    current_loop_idx = 0 # Current Loop Number
    current_loop = chrome[current_loop_idx]
    current_gene_idx = 0 # Current gene Number within a given loop

# Checks if a kill has been made, if yes -> write it to file and send the file name to chat
def earnedKill(ai):
    global score
    global prev_score
    global chromosome
   
    filename = "selChrome_0.txt" #Baseline file name

    # Modify file ending for pre-existing files
    while os.path.exists(("data/" + filename)):
        index = int((filename.split("_")[1]).split(".")[0]) # Get the number at end of file name
        index = str(index+1)
        filename = "selChrome_{}.txt".format(index)

    # Score increment indicates a kill
    if score > prev_score:
        writeChromosomeToFile(chromosome, filename) 
        ai.talk('New Chrome File -' + filename) #Chat the file name

# Checks if the agent has died, if yes and it was killed by another agent
# finds the chromosome file, and initalizes it as its new chromosome

def died(ai):
    global score
    global prev_score
    global chromosome
    global framesPostDeath
    global MUT_RATE

    MUT_RATE = 300

    # Start frame counter after a negative score change
    if score < prev_score:
        framesPostDeath = 1
        #print("Score: {}".format(score))
        #print("Previous Score: {}".format(prev_score))

    if framesPostDeath >= 1 and framesPostDeath < 100:
        framesPostDeath += 1
    else:
        framesPostDeath = 0
    #print("Frames post Death: {}".format(framesPostDeath))

    # Score change and message with hyphen (indicating killed instead of wall collision)
    if (framesPostDeath != 0): 
        message = ai.scanMsg(0) # Get most recent chat message
        
        if "-" in message: # Hyphen is only in our file messages from other agents
            framesPostDeath = 0
            print("Message: {}".format(message))

            if len(message) > 1:
                print("Death and death message found")
                message = (message.split("-")[1]).split(" ")[0] # Extract filename from message
                print("New Chrome filepath: {}".format(message))
                new_chromosome_file_name = "data/" + message
               
                new_chromosome = None
                with open(new_chromosome_file_name, 'r') as f:
                    new_chromosome = eval(f.read())

                # Evolution
                #print("Transferred Chrome: {}".format(new_chromosome))
                cross_over_child = crossover(chromosome, new_chromosome)
                #print("Crossover child: {}".format(cross_over_child))
                mutated_child = mutate(cross_over_child, MUT_RATE)
                #print("Mutated child: {}".format(mutated_child))
                
                ## Check that the new chromosome is different than old, insanely low odds for it to be the same
                #print("*"*50)
                #print(mutated_child == chromosome)
                #print("*"*50)

                initializeAgent(mutated_child) # Set new chromosome in place of old

# Relative to us
def findMinWallAngle(wallFeelers):
    min_wall = min(wallFeelers)
    min_index = wallFeelers.index(min_wall)

    angle = int(10*min_index)

    #angleToEnemy = heading - enemy_angle

    if angle < 180: # wall to the right
        return angle
    else:
        return angle - 360

# Relative to us
def findMaxWallAngle(wallFeelers):
    max_wall = max(wallFeelers)
    max_index = wallFeelers.index(max_wall)

    angle = int(10*max_index)

    #angleToEnemy = heading - enemy_angle

    if angle < 180: # wall to the right
        return angle
    else:
        return angle - 360

# Relative to world internally, returns relative to us
def findAngle(X, Y, ENEMY_X, ENEMY_Y, heading):
    new_enemy_x = ENEMY_X - X
    new_enemy_y = ENEMY_Y - Y

    # If positive, enemy to right
    # If negative, enemy to left
    try:
        enemy_angle = math.degrees(math.atan(new_enemy_y/new_enemy_x))
    except:
        enemy_angle = 0 # in the case of division by 0

    angleToEnemy = int(heading - enemy_angle)

    if angleToEnemy < 360 - angleToEnemy: # enemy to the right
        return angleToEnemy
    else:
        return angleToEnemy - 360

    #hyp = ENEMY_DIST
    #if ENEMY_X - X > 0:
    #    x_dist = ENEMY_X - X
    #else:
    #    x_dist = X - ENEMY_X


    #theta = int(math.degrees(math.acos(x_dist / hyp))) - 90

def checkConditional(conditional_index, sensors):
    speed = sensors[0]
    enemy_dist = sensors[1]
    min_wall_dist = sensors[2]
    closestBulletDistance = sensors[3]
    enemy_x = sensors[4]
    enemy_y = sensors[5]
    x = sensors[6]
    y = sensors[7]
    heading = sensors[8]
    
    
    if enemy_dist == None:
        enemy_dist = -1
        enemy_dir = -1
        enemy_x = -1
        enemy_y = -1
        
    enemy_dir = getEnemyDirection(enemy_dist, enemy_x, enemy_y, x, y, heading)
    
            

    # 16 conditionals Core 2.0 in Action
    conditional_list = ["speed > 6", "speed == 0",
                        "enemy_dist < 50", "enemy_dist > 200", 
                        "enemy_dist < 100 and enemy_dir == 1", 
                        "enemy_dist < 100 and enemy_dir == 2", 
                        #"True",
                        "enemy_dist < 100 and enemy_dir == 3",
                        "enemy_dist < 100 and enemy_dir == 4",
                         "min_wall_dist < 200", "min_wall_dist < 75", "min_wall_dist > 200" , "min_wall_dist < 150",
                        "closestBulletDistance < 100", "closestBulletDistance < 200", "closestBulletDistance <50",
                        "enemy_dist == -1"
                        ]
    
    
    result = eval(conditional_list[conditional_index])
    return result
    
def wallBetweenTarget(X, Y, ENEMY_X, ENEMY_Y):
    return ai.wallBetween(int(X), int(Y), int(ENEMY_X), int(ENEMY_Y)) != -1
    
def getEnemyDirection(Enemy_Dist, Enemy_X, Enemy_Y, X, Y, heading):
    direction = -1
    
    theta = None
    wallPreEnemy = False
    shotTolerance = random.randint(-5,5)
    
    if Enemy_Dist != -1: 
        xDistToEnemy = Enemy_X - X
        yDistToEnemy = Enemy_Y - Y
        theta = findAngle(X, Y, Enemy_X, Enemy_Y, heading)
        wallPreEnemy = wallBetweenTarget(X,Y, Enemy_X, Enemy_Y)
        
    else:
        xDistToEnemy = 0
        yDistToEnemy = 0
        
    if Enemy_Dist and xDistToEnemy > 0 and yDistToEnemy > 0 and not wallPreEnemy: #Q1
        direction = 1
    elif Enemy_Dist and xDistToEnemy < 0 and yDistToEnemy > 0 and not wallPreEnemy: # Q2
        direction = 2
    elif Enemy_Dist and xDistToEnemy < 0 and yDistToEnemy < 0 and not wallPreEnemy: # Q3
        direction = 3
    elif Enemy_Dist and xDistToEnemy > 0 and yDistToEnemy < 0 and not wallPreEnemy: #Q4
        direction = 4
        
    return direction

def AI_loop():
    try:
        #speed = sensors[0]
        #enemy_dist = sensors[1]
        #min_wall_dist= sensors[2] # minimum wall distance
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
        trackingFeelers = []
        headingFeelers = []

        # Tracking
        for angle in range(0, 360, 10):
            trackingFeelers.append(ai.wallFeeler(500, tracking + angle))

        # Heading
        for angle in range(0, 360, 10):
            headingFeelers.append(ai.wallFeeler(500, heading + angle))

        min_wall_dist = min(headingFeelers)

        # Disable turns by default each loop
        #ai.turnRight(0)
        #ai.turnRight(0)


        global current_loop_idx
        global chrome # Decoded chromosome
        global current_loop
        global current_gene_idx
        global chromosome
        
        GENES_PER_LOOP = 8
    
        #print("Chrome: {}".format(chrome))
        #print("Raw chrome values: {}".format(raw_chrome_values))
        #print("Current gene: {}".format(current_loop))
        #print("Current loop: {}".format(current_loop[current_gene_idx]))
        #print("Current Gene index: {}".format(current_gene_idx))
        #print("Current Loop Index: {}".format(current_loop_idx))
        #print("-"*10)
        sensors = [speed, ENEMY_DIST, min_wall_dist, closestBulletDistance, ENEMY_X, ENEMY_Y, X, Y, heading]

        # If current gene is a jump gene
        if current_loop[current_gene_idx][0] == False: # First item in gene being false indicates jump gene

            # If the Jump Gene conditional is true
            checkConditionalResult = checkConditional(current_loop[current_gene_idx][1], sensors)
            if checkConditionalResult:
                current_loop_idx = current_loop[current_gene_idx][2] # Update to the gene determined by jump 
                current_loop = chrome[current_loop_idx] # Set new current gene based on the index
                current_gene_idx = 0 # Reset loop index to 0 for the new gene

                #print("Jumping to: {}".format(current_loop_idx))
            else:
                current_gene_idx = ((current_gene_idx + 1) % GENES_PER_LOOP) # Move to next loop in the gene (max 15)
        else: 
            # Convert from boolean to 1 or 0 for x-pilot inputs
            shoot = current_loop[current_gene_idx][1] 
            thrust = 1 if current_loop[current_gene_idx][2] else 0
            
            turnQuantity = int((current_loop[current_gene_idx][3]) * 2) # Scale up
            turnTarget = current_loop[current_gene_idx][4]
            
            #print("Action Gene:")
            #print("Shoot: {}".format(shoot))
            #print("Thrust: {}".format(thrust))
            #print("Turn Quantity: {}".format(turnQuantity))
            #print("Turn Target Num: {}".format(turnTarget))
            #print("-"*40)

            ai.thrust(thrust)
            ai.fireShot() if shoot else None #ai.fireShot(shoot) # Shoot if shoot is true
          
            # Pick turn target based on numerical identifier from loop.
            #Examples from paper: nearestShip, oppsoiteClosestWall, most dangerous bullet etc    
            match turnTarget:
                case 0:
                    #turn towards closest wall heading
                    angle = findMinWallAngle(headingFeelers)

                    if angle < 0:
                        ai.turn(-1*turnQuantity)
                    elif angle > 0:
                        ai.turn(turnQuantity)
                case 1:
                    #turn away from closest wall heading
                    angle = findMinWallAngle(headingFeelers)

                    if angle > 0:
                        ai.turn(-1*turnQuantity)
                    elif angle < 0:
                        ai.turn(turnQuantity)
                case 2:
                    #turn towards furthest wall heading
                    angle = findMaxWallAngle(headingFeelers)

                    if angle < 0:
                        ai.turn(-1*turnQuantity)
                    elif angle > 0:
                        ai.turn(turnQuantity)
                case 3:
                    #turn away from furthest wall heading
                    angle = findMaxWallAngle(headingFeelers)

                    if angle > 0:
                        ai.turn(-1*turnQuantity)
                    elif angle < 0:
                        ai.turn(turnQuantity)
                case 4:
                    #turn towards enemy ship
                    if ENEMY_DIST != None:
                        angleToEnemy = findAngle(X, Y, ENEMY_X, ENEMY_Y, heading)

                        if angleToEnemy < 0:
                            ai.turn(-1*turnQuantity)
                        elif angleToEnemy > 0:
                            ai.turn(turnQuantity)
                    
                case 5:
                    #turn away from enemy ship
                    if ENEMY_DIST != None:
                        angleToEnemy = findAngle(X, Y, ENEMY_X, ENEMY_Y, heading)

                        if angleToEnemy > 0:
                            ai.turn(-1*turnQuantity)
                        else:
                            ai.turn(turnQuantity)

                case 6:
                    #turn towards bullet
                    if ai.shotDist(0) != -1:
                        SHOT_X = ai.shotX(0)
                        SHOT_Y = ai.shotY(0)
                        angleToShot = findAngle(X, Y, SHOT_X, SHOT_Y, heading)

                        if angleToShot < 0:
                            ai.turn(-1*turnQuantity)
                        elif angleToShot > 0:
                            ai.turn(turnQuantity)

                case 7:
                    #turn away from bullet
                    if ai.shotDist(0) != -1:
                        SHOT_X = ai.shotX(0)
                        SHOT_Y = ai.shotY(0)
                        angleToShot = findAngle(X, Y, SHOT_X, SHOT_Y, heading)

                        if angleToShot > 0:
                            ai.turn(-1*turnQuantity)
                        elif angleToShot < 0:
                            ai.turn(turnQuantity)

            current_gene_idx = ((current_gene_idx + 1) % GENES_PER_LOOP) # Move to next loop in the gene (max 15)
         
        #print("-"*20)
        
        # Kill/Death Tracking
        global score
        global prev_score

        earnedKill(ai)
        died(ai)
        prev_score = score
        score = ai.selfScore()

        #print("Main Loop Score: {}".format(score))
        #print("Main Loop Prev_Score: {}".format(score))

        # NOTE: Do we want to crossover with a random new chroomsome if we crash ourselves?



    except Exception as e:
        print("Exception")
        print(str(e))
        traceback.print_exc()
        ai.quitAI()

def main():
    args = sys.argv
    bot_num = sys.argv[1]

    createDataFolder()


    initializeAgent()
    global prev_score
    global score
    
    score = 0
    prev_score = 0


    ai.start(AI_loop, ["-name", "Core Agent {}".format(bot_num), "-join", "localhost"])

if __name__ =="__main__":
    main()
