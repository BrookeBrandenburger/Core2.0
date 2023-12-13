import libpyAI as ai
import math
import random
import random
from os.path import exists

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
    chrome = readChrome(chromosome)
    current_loop_idx = 0 # Current Loop Number
    current_loop = chrome[current_loop_idx]
    current_gene_idx = 0 # Current gene Number within a given loop

def earnedKill(ai):
    global score
    global prev_score
    global chromosome
   
    filename = "test.txt" # TODO 
    # TODO
    # Score increment indicates a kill
    if score > prev_score:
        writeChromosomeToFile(chromosome, filename)
        ai.talk('New Chrome File -' + filename)

def died(ai):
    global score
    global prev_score
    global chromosome
    
    message = ai.scanMsg(0).split("-")
    # Score change and message with hyphen (indicating killed instead of wall collision)
    if score != prev_score and len(message) > 1:
        new_chromosome_file_name = message[1]

        new_chromosome = None
        with open(new_chromosome_file_name, 'r') as f:
            new_chromosome = eval(f.read())

        initializeAgent(new_chromosome)


def findAngle(X, ENEMY_X, ENEMY_DIST):  # Taking the X coordinates of agent and enemy
    hyp = ENEMY_DIST
    if ENEMY_X - X > 0:
        x_dist = ENEMY_X - X
    else:
        x_dist = X - ENEMY_X
    theta = int(math.degrees(math.acos(x_dist / hyp)))

    return theta
    
def checkConditional(conditional_index, sensors):
    speed = sensors[0]
    enemy_dist = sensors[1]
    wall_dist= sensors[2]
    closestBulletDistance = sensors[3]
    enemy_x = sensors[4]
    enemy_y = sensors[5]
    x = sensors[6]
    y = sensors[7]
    
    
    if enemy_dist == None:
        enemy_dist = -1
        enemy_dir = -1
        enemy_x = -1
        enemy_y = -1
        
    enemy_dir = getEnemyDirection(enemy_dist, enemy_x, enemy_y, x, y)
    
            

    # 16 conditionals Core 2.0 in Action
    conditional_list = ["speed > 6", "speed == 0",
                        "enemy_dist < 50", "enemy_dist > 200", 
                        "enemy_dist < 100 and enemy_dir == 1", 
                        "enemy_dist < 100 and enemy_dir == 2", 
                        #"True",
                        "enemy_dist < 100 and enemy_dir == 3",
                        "enemy_dist < 100 and enemy_dir == 4"
                         "wall_dist < 200", "wall_dist < 75", "wall_dist > 200" , "wall_dist < 150",
                        "closestBulletDistance < 100", "closestBulletDistance < 200", "closestBulletDistance <50",
                        "enemy_dist == -1"
                        ]
    
    
    result = eval(conditional_list[conditional_index])
    return result
    
def wallBetweenTarget(X, Y, ENEMY_X, ENEMY_Y):
    return ai.wallBetween(int(X), int(Y), int(ENEMY_X), int(ENEMY_Y)) != -1
    
def getEnemyDirection(Enemy_Dist, Enemy_X, Enemy_Y, X, Y):
    direction = -1
    
    theta = None
    wallPreEnemy = False
    shotTolerance = random.randint(-5,5)
    
    if Enemy_Dist != -1: 
        xDistToEnemy = Enemy_X - X
        yDistToEnemy = Enemy_Y - Y
        theta = findAngle(X, Enemy_X, Enemy_Dist)
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
	    
        GENES_PER_LOOP = 8
	
        #print("Chrome: {}".format(chrome))
        #print("Raw chrome values: {}".format(raw_chrome_values))
        print("Current gene: {}".format(current_loop))
        print("Current loop: {}".format(current_loop[current_gene_idx]))
        print("Current Gene index: {}".format(current_gene_idx))
        print("Current Loop Index: {}".format(current_loop_idx))
        print("-"*10)
        sensors = [speed, ENEMY_DIST, wall_dist, closestBulletDistance, ENEMY_X, ENEMY_Y, X, Y]

        # If current gene is a jump gene
        if current_loop[current_gene_idx][0] == False:

            # If the Jump Gene conditional is true
            checkConditionalResult = checkConditional(current_loop[current_gene_idx][1], sensors)
            if checkConditionalResult:
                current_loop_idx = current_loop[current_gene_idx][2] # Update to the gene determined by jump 
                current_loop = chrome[current_loop_idx] # Set new current gene based on the index
                current_gene_idx = 0 # Reset loop index to 0 for the new gene

                print("Jumping to: {}".format(current_loop_idx))
            else:
                current_gene_idx = ((current_gene_idx + 1) % GENES_PER_LOOP) # Move to next loop in the gene (max 15)
        else: 
            # Convert from boolean to 1 or 0 for x-pilot inputs
            shoot = current_loop[current_gene_idx][1] 
            thrust = 1 if current_loop[current_gene_idx][2] else 0
            
            turnQuantity = current_loop[current_gene_idx][3]
            turnTarget = current_loop[current_gene_idx][4]
            
            print("Action Gene:")
            print("Shoot: {}".format(shoot))
            print("Thrust: {}".format(thrust))
            print("Turn Quantity: {}".format(turnQuantity))
            print("Turn Target Num: {}".format(turnTarget))
            print("-"*40)

            ai.thrust(thrust)
            ai.fireShot() if shoot else None #ai.fireShot(shoot) # Shoot if shoot is true
          
            # Pick turn target based on numerical identifier from loop.
            #Examples from paper: nearestShip, oppsoiteClosestWall, most dangerous bullet etc
            # TODO: Implement turning target and utilize turn quantity
            match turnTarget:
                case 0:
                    pass
                case 1:
                    pass
                case 2:
                    ai.turnRight(1) # Place holder
                    pass
                case 3:
                    pass
                case 4:
                    pass
                case 5:
                    pass
                case 6:
                    pass
                case 7:
                    pass
            current_gene_idx = ((current_gene_idx + 1) % GENES_PER_LOOP) # Move to next loop in the gene (max 15)
         
        print("-"*20)
        print("Message: {}".format(ai.scanMsg(0)))
        
        # Kill/Death Tracking
        global score
        global prev_score
        earnedKill(ai) # Check for kill
        died() # If killed, get new chromosome

        # NOTE: Do we want to crossover with a random new chroomsome if we crash ourselves?
        prev_score = score
        score = ai.selfScore()



    except Exception as e:
        print("Exception")
        print(e)
        ai.quitAI()

def main():
    initializeAgent()

    ai.start(AI_loop, ["-name", "Core!", "-join", "localhost"])


if __name__ =="__main__":
    main()
