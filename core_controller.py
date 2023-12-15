import libpyAI as ai
import math
import random
import os
import sys
import traceback
from typing import Union, List, Any

from chromosome import *

# All run-once instructions
def setup(ai, heading, tracking) -> None:
    initializeAgent()
    generateFeelers(ai, heading, tracking)

# Create all needed wall feelers for the AI
def generateFeelers(ai, heading: float, tracking: float) -> None: 
    global headingFeelers
    global trackingFeelers

    # store in array so we can easily find the shortest feeler
    #trackingFeelers = []
    headingFeelers = []
    trackingFeelers = []

    # Tracking
    for angle in range(0, 360, 10):
        trackingFeelers.append(ai.wallFeeler(500, int(tracking + angle)))

    # Heading
    for angle in range(0, 360, 10):
        headingFeelers.append(ai.wallFeeler(500, int(heading + angle)))

# Sets all needed values for a new agent, by default creates a new chromosome, a chromosome can be passed in.

def initializeAgent(input_chrome: List[List] = generateChromosome()) -> None:
    # Chomosome Controllers! #[[loop1], [loop2]]
    global chrome  # Decoded chromosome
    global raw_chrome_values
    global current_loop  # A chromosome is made up of 16 loops
    global current_loop_idx
    global current_gene_idx  # Refers to an action within a loop (jump/action)
    global chromosome
    global prev_score 
    global score
    global framesPostDeath

    framesPostDeath = 0

    chromosome = input_chrome
    chrome = readChrome(chromosome)
    print("Chromosome: {}".format(chromosome))
    current_loop_idx = 0  # Current Loop Number
    current_loop = chrome[current_loop_idx]
    current_gene_idx = 0  # Current gene Number within a given loop

# Checks if a kill has been made, if yes -> write it to file and send the file name to chat


def earnedKill(ai) -> None:
    global prev_score
    global score
    global chromosome

    filename: str = "selChrome_0.txt"  # Baseline file name

    # Modify file ending for pre-existing files
    while os.path.exists(("data/" + filename)):
        # Get the number at end of file name
        index: Union[int, str] = int((filename.split("_")[1]).split(".")[0])
        index = str(index+1)
        filename = "selChrome_{}.txt".format(index)

    # Score increment indicates a kill
    if score > prev_score:
        writeChromosomeToFile(chromosome, filename)
        ai.talk('New Chrome File -' + filename)  # Chat the file name

# Checks if the agent has died, if yes and it was killed by another agent
# finds the chromosome file, and initalizes it as its new chromosome


def died(ai) -> None:
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
        message: str = ai.scanMsg(0)  # Get most recent chat message

        if "-" in message:  # Hyphen is only in our file messages from other agents
            framesPostDeath = 0
            print("Message: {}".format(message))

            if len(message) > 1:
                print("Death and death message found")
                # Extract filename from message
                message = (message.split("-")[1]).split(" ")[0]
                print("New Chrome filepath: {}".format(message))
                new_chromosome_file_name: str = "data/" + message

                new_chromosome: Union[None, List[List]] = None
                with open(new_chromosome_file_name, 'r') as f:
                    new_chromosome = eval(f.read())

                # Evolution
                #print("Transferred Chrome: {}".format(new_chromosome))
                cross_over_child = crossover(chromosome, new_chromosome)
                #print("Crossover child: {}".format(cross_over_child))
                mutated_child: List[List] = mutate(cross_over_child, MUT_RATE)
                #print("Mutated child: {}".format(mutated_child))

                # Check that the new chromosome is different than old, insanely low odds for it to be the same
                # print("*"*50)
                #print(mutated_child == chromosome)
                # print("*"*50)

                # Set new chromosome in place of old
                initializeAgent(mutated_child)

# Relative to us


def findMinWallAngle(wallFeelers: List[int]) -> int:
    min_wall: int = min(wallFeelers)
    min_index: int = wallFeelers.index(min_wall)

    angle: int = int(10*min_index)

    if angle < 180:  # wall to the right
        return angle
    else:
        return angle - 360

# Relative to us


def findMaxWallAngle(wallFeelers: List[int]) -> int:
    max_wall: int = max(wallFeelers)
    max_index: int = wallFeelers.index(max_wall)

    angle: int = int(10*max_index)

    if angle < 180:  # wall to the right
        return angle
    else:
        return angle - 360

# Relative to world internally, returns relative to us


def findAngle(X: int, Y: int, ENEMY_X: int, ENEMY_Y: int, heading: float) -> int:
    new_enemy_x: int = ENEMY_X - X
    new_enemy_y: int = ENEMY_Y - Y

    enemy_angle: float
    # If positive, enemy to right
    # If negative, enemy to left
    try:
        enemy_angle = math.degrees(math.atan(new_enemy_y/new_enemy_x))
    except:
        enemy_angle = 0  # in the case of division by 0

    angleToEnemy: int = int(heading - enemy_angle)

    if angleToEnemy < 360 - angleToEnemy:  # enemy to the right
        return angleToEnemy
    else:
        return angleToEnemy - 360


def checkConditional(conditional_index: int, sensors: list[Any]) -> bool: 
    speed: float = sensors[0]
    enemy_dist: Union[float, None] = sensors[1]
    min_wall_dist: int = sensors[2]
    closestBulletDistance: float = sensors[3]
    enemy_x: int = sensors[4]
    enemy_y: int = sensors[5]
    x: int = sensors[6]
    y: int = sensors[7]
    heading: float = sensors[8]

    if enemy_dist is None:
        enemy_dist = -1
        enemy_dir = -1
        enemy_x = -1
        enemy_y = -1

    enemy_dir: int = getEnemyDirection(enemy_dist, enemy_x, enemy_y, x, y, heading)

    # 16 conditionals Core 2.0 in Action
    conditional_List = [speed > 6, speed == 0,
                        enemy_dist < 50, enemy_dist > 200,
                        enemy_dist < 100 and enemy_dir == 1,
                        enemy_dist < 100 and enemy_dir == 2,
                        # True,
                        enemy_dist < 100 and enemy_dir == 3,
                        enemy_dist < 100 and enemy_dir == 4,
                        min_wall_dist < 200, min_wall_dist < 75, min_wall_dist > 300, min_wall_dist < 150,
                        closestBulletDistance < 100, closestBulletDistance < 200, closestBulletDistance <50,
                        enemy_dist == -1
                        ]

    result = conditional_List[conditional_index]
    return result


def wallBetweenTarget(X: int, Y: int, ENEMY_X: int, ENEMY_Y: int) -> bool:
    return ai.wallBetween(int(X), int(Y), int(ENEMY_X), int(ENEMY_Y)) != -1


def getEnemyDirection(Enemy_Dist: float, Enemy_X: int, Enemy_Y: int, X: int, Y: int, heading: float) -> int:
    direction: int = -1

    theta: Union[float, None] = None
    wallPreEnemy: Union[bool, None] = False
    shotTolerance: int = random.randint(-5, 5)

    if Enemy_Dist != -1:
        xDistToEnemy = Enemy_X - X
        yDistToEnemy = Enemy_Y - Y
        theta = findAngle(X, Y, Enemy_X, Enemy_Y, heading)
        wallPreEnemy = wallBetweenTarget(X, Y, Enemy_X, Enemy_Y)

    else:
        xDistToEnemy = 0
        yDistToEnemy = 0

    if Enemy_Dist and xDistToEnemy > 0 and yDistToEnemy > 0 and not wallPreEnemy:  # Q1
        direction = 1
    elif Enemy_Dist and xDistToEnemy < 0 and yDistToEnemy > 0 and not wallPreEnemy:  # Q2
        direction = 2
    elif Enemy_Dist and xDistToEnemy < 0 and yDistToEnemy < 0 and not wallPreEnemy:  # Q3
        direction = 3
    elif Enemy_Dist and xDistToEnemy > 0 and yDistToEnemy < 0 and not wallPreEnemy:  # Q4
        direction = 4

    return direction


def AI_loop():
    try:
        global headingFeelers
        global trackingFeelers
        global started

        # get information
        heading: float = float(ai.selfHeadingDeg())
        tracking: float = float(ai.selfTrackingDeg())
        if not started:
            setup(ai, heading, tracking)

        ai.setPower(8)
        ai.setTurnSpeed(20.0)

        # Self details
        # handicap
        speed: int = int(ai.selfSpeed())
        X: int = int(ai.selfX())
        Y: int = int(ai.selfY())



        # Enemy Details
        closestShipId: int = int(ai.closestShipId())

        ENEMY_SPEED: Union[float, None] = None
        ENEMY_DIST: Union[float, None] = None
        ENEMY_X: Union[int, None] = None
        ENEMY_Y: Union[int, None] = None
        ENEMY_HEADING: Union[float, None] = None

        if closestShipId != -1:
            ENEMY_SPEED = float(ai.enemySpeedId(closestShipId))
            ENEMY_DIST = float(ai.enemyDistanceId(closestShipId))
            ENEMY_X = int(ai.screenEnemyXId(closestShipId))
            ENEMY_Y = int(ai.screenEnemyYId(closestShipId))
            ENEMY_HEADING = float(ai.enemyHeadingDegId(closestShipId))

        if ai.shotDist(0) > 0:
            closestBulletDistance: float = ai.shotDist(0)
        else:
            closestBulletDistance = math.inf

        min_wall_dist: int = min(headingFeelers)

        # Disable turns by default each loop
        # ai.turnRight(0)
        # ai.turnRight(0)

        global current_loop_idx
        global chrome  # Decoded chromosome
        global current_loop
        global current_gene_idx
        global chromosome

        GENES_PER_LOOP: int = 8
        
        #print("Chrome: {}".format(chrome))
        #print("Raw chrome values: {}".format(raw_chrome_values))
        #print("Current gene: {}".format(current_loop))
        print("Current loop: {}".format(current_loop[current_gene_idx]))
        #print("Current Gene index: {}".format(current_gene_idx))
        #print("Current Loop Index: {}".format(current_loop_idx))
        # print("-"*10)
        sensors: list[Any] = [speed, ENEMY_DIST, min_wall_dist,
                   closestBulletDistance, ENEMY_X, ENEMY_Y, X, Y, heading]

        # If current gene is a jump gene
        # First item in gene being false indicates jump gene
        if current_loop[current_gene_idx][0] == False:

            # If the Jump Gene conditional is true
            checkConditionalResult = checkConditional(
                current_loop[current_gene_idx][1], sensors)
            if checkConditionalResult:
                # Update to the gene determined by jump
                current_loop_idx = current_loop[current_gene_idx][2]
                # Set new current gene based on the index
                current_loop = chrome[current_loop_idx]
                current_gene_idx = 0  # Reset loop index to 0 for the new gene

                #print("Jumping to: {}".format(current_loop_idx))
            else:
                # Move to next loop in the gene (max 15)
                current_gene_idx = ((current_gene_idx + 1) % GENES_PER_LOOP)
        else:
            # Convert from boolean to 1 or 0 for x-pilot inputs
            shoot: bool = current_loop[current_gene_idx][1]
            thrust: int = 1 if current_loop[current_gene_idx][2] else 0

            turnQuantity: int = int(
                (current_loop[current_gene_idx][3]) * 10)  # Scale up
            turnTarget: int = current_loop[current_gene_idx][4]

            #print("Action Gene:")
            #print("Shoot: {}".format(shoot))
            #print("Thrust: {}".format(thrust))
            #print("Turn Quantity: {}".format(turnQuantity))
            #print("Turn Target Num: {}".format(turnTarget))
            # print("-"*40)

            ai.thrust(thrust)
            ai.fireShot() if shoot else None  # ai.fireShot(shoot) # Shoot if shoot is true

            # Pick turn target based on numerical identifier from loop.
            # Examples from paper: nearestShip, oppsoiteClosestWall, most dangerous bullet etc
            match turnTarget:
                case 0:
                    # turn towards closest wall heading
                    angle: int = findMinWallAngle(headingFeelers)

                    if angle < 0:
                        ai.turn(-1*turnQuantity)
                    elif angle > 0:
                        ai.turn(turnQuantity)
                case 1:
                    # turn away from closest wall heading
                    angle: int = findMinWallAngle(headingFeelers)

                    if angle > 0:
                        ai.turn(-1*turnQuantity)
                    elif angle < 0:
                        ai.turn(turnQuantity)
                case 2:
                    # turn towards furthest wall heading
                    angle: int = findMaxWallAngle(headingFeelers)

                    if angle < 0:
                        ai.turn(-1*turnQuantity)
                    elif angle > 0:
                        ai.turn(turnQuantity)
                case 3:
                    # turn away from furthest wall heading
                    angle: int = findMaxWallAngle(headingFeelers)

                    if angle > 0:
                        ai.turn(-1*turnQuantity)
                    elif angle < 0:
                        ai.turn(turnQuantity)
                case 4:
                    # turn towards enemy ship
                    if ENEMY_DIST != None:
                        angleToEnemy: int = findAngle(
                            X, Y, ENEMY_X, ENEMY_Y, heading)

                        if angleToEnemy < 0:
                            ai.turn(-1*turnQuantity)
                        elif angleToEnemy > 0:
                            ai.turn(turnQuantity)

                case 5:
                    # turn away from enemy ship
                    if ENEMY_DIST != None:
                        angleToEnemy: int = findAngle(
                            X, Y, ENEMY_X, ENEMY_Y, heading)

                        if angleToEnemy > 0:
                            ai.turn(-1*turnQuantity)
                        else:
                            ai.turn(turnQuantity)

                case 6:
                    # turn towards bullet
                    if ai.shotDist(0) != -1:
                        SHOT_X: int = ai.shotX(0)
                        SHOT_Y: int = ai.shotY(0)
                        angleToShot: int = findAngle(X, Y, SHOT_X, SHOT_Y, heading)

                        if angleToShot < 0:
                            ai.turn(-1*turnQuantity)
                        elif angleToShot > 0:
                            ai.turn(turnQuantity)

                case 7:
                    # turn away from bullet
                    if ai.shotDist(0) != -1:
                        SHOT_X: int = ai.shotX(0)
                        SHOT_Y: int = ai.shotY(0)
                        angleToShot: int = findAngle(X, Y, SHOT_X, SHOT_Y, heading)

                        if angleToShot > 0:
                            ai.turn(-1*turnQuantity)
                        elif angleToShot < 0:
                            ai.turn(turnQuantity)

            # Move to next loop in the gene (max 15)
            current_gene_idx = ((current_gene_idx + 1) % GENES_PER_LOOP)

        # print("-"*20)

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
    bot_num: str = sys.argv[1]

    createDataFolder()
    global prev_score
    global score
    global started

    started = False
    score = 0
    prev_score = 0

    ai.start(
        AI_loop, ["-name", "Core Agent {}".format(bot_num), "-join", "localhost"])


if __name__ == "__main__":
    main()
