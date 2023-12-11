import libpyAI as ai
import math
import random
import csv
from numpy.random import randint
import random
import os
import shutil

from chromosome import *

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
        ai.setTurnSpeedDeg(20)
        power = 20
        ai.setPower(power)
        
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

        global current_gene_idx
        global chrome
        global current_gene
        global current_loop_idx

        print("Chrome: {}".format(chrome))
        print("Raw chrome values: {}".format(raw_chrome_values))
        print("Current gene: {}".format(current_gene))
        print("Current loop: {}".format(current_gene[current_loop_idx]))
        print("-"*20)

        sensors = [speed, ENEMY_DIST, wall_dist, closestBulletDistance, ENEMY_X, ENEMY_Y, X, Y]

        # If current gene is a jump gene
        if current_gene[current_loop_idx][0] == False:
            print("Jump Gene!")

            # If the Jump Gene conditional is true
            checkConditionalResult = checkConditional(current_gene[current_loop_idx][1], sensors)
            print(checkConditionalResult)
            if checkConditionalResult:
                current_gene_idx = current_gene[current_loop_idx][2] # Update to the gene determined by jump 
                current_gene = chrome[current_gene_idx] # Set new current gene based on the index
                current_loop_idx = 0 # Reset loop index to 0 for the new gene

                print("Jumping to: {}".format(current_gene_idx))
            else:
                current_loop_idx = ((current_loop_idx + 1) % 16) # Move to next loop in the gene (max 15)
        else: 
            # Convert from boolean to 1 or 0 for x-pilot inputs
            shoot = current_gene[current_loop_idx][1] 
            thrust = 1 if current_gene[current_loop_idx][2] else 0
            
            turnQuantity = current_gene[current_loop_idx][3]
            turnTarget = current_gene[current_loop_idx][4]
            
            print("Action Gene:")
            print("Shoot: {}".format(shoot))
            print("Thrust: {}".format(thrust))
            print("Turn Quantity: {}".format(turnQuantity))
            print("Turn Target Num: {}".format(turnTarget))
            print("-"*20)

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
            current_loop_idx = ((current_loop_idx + 1) % 16) # Move to next loop in the gene (max 15)
 

            

    except Exception as e:
        print("Exception")
        print(e)
        ai.quitAI()

def main():
    # Chomosome Controllers! #[[loop1], [loop2]]
    global chrome
    global raw_chrome_values
    global current_gene
    global current_gene_idx
    global current_loop_idx

    raw_chrome_values =  [['100001110', '001111001', '010101101', '000111000'], ['101111001', '000111000']]
    chrome = readChrome(raw_chrome_values)
    current_gene_idx = 0 # Gene refers to loop index
    current_gene = chrome[current_gene_idx]
    current_loop_idx = 0 # 

    ai.start(AI_loop, ["-name", "Core!", "-join", "localhost"])

if __name__ =="__main__":
    main()
