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
        
		sensors = [speed, ENEMY_DIST, wall_dist, closestBulletDistance, ENEMY_X, ENEMY_Y, X, Y]
		
		if current_chrome[0][0] == False: # jump gene
			if checkConditional(current_chrome[0][1], sensors): # TODO Del
				current_chrome = raw_chrome_values[current_chrome[0][2]]
				break # TODO - does this work?
			else:
				# do actions
				pass
		

	except Exception as e:
		print("Exception")
		print(e)
		ai.quitAI()
# Chomosome Controllers! #[[loop1], [loop2]]
chrome =  [['000001111', '101111001', '110101101', '100111000'], ['001111001', '100111000']]
raw_chrome_values = readChrome(chrome)
current_chrome = raw_chrome_values[0]
ai.start(AI_loop, ["-name", "Core!", "-join", "localhost"])
