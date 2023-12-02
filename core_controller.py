import libpyAI as ai
import math
import random
import csv
from numpy.random import randint
import random
import os
import shutil

from chromosome import *

def checkConditional(conditional_index):
	speed = 10 # TODO :  Make real speed later # true
	enemy_dist = 50 # true
	wall_dist = 300 # false
	bulletDanger = 200 #false
	
	
	enemy_dir = getEnemyDirection(Enemy_Dist, Enemy_X, Enemy_Y, X, Y)
	
	if ai.shotDist(0) > 0:
		closestBulletDistance = ai.shotDist(0)
	else:
 		closestBulletDistance = math.inf
            
    if enemy_dist == None:
    	enemy_dist = -1
	# 16 conditionals 
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
	#print(conditional_list[conditional_index])
	#print(result)
	return result
	
def wallBetweenTarget(X, Y, ENEMY_X, ENEMY_Y):
    return ai.wallBetween(int(X), int(Y), int(ENEMY_X), int(ENEMY_Y)) != -1
    
def getEnemyDirection(Enemy_Dist, Enemy_X, Enemy_Y, X, Y):
	direction = -1
	
	theta = None
	wallPreEnemy = False
	shotTolerance = random.randint(-5,5)
	
	if Enemy_Dist: 
		xDistToEnemy = Enemy_X - X
		yDistToEnemy = Enemy_Y - Y
		theta = findAngle(X, Enemy_X, Enemy_DIST)
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
	
		if checkConditional(conditional_index):
			# gene = chrome[conditional_index]
			# TODO GoTo loop_number
			pass
			#print("Loop num: {}".format(loop_number))
		
	except Exception as e:
		print("Exception")
		print(e)
		ai.quitAI()

print(checkConditional(2))
ai.start(AI_loop, ["-name", "Core!", "-join", "localhost"])
