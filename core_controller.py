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
	conditional_list = ["speed > 6", "enemy_dist < 100", "wall_dist < 200", "bulletDanger < 50"]
	
	result = eval(conditional_list[conditional_index])
	#print(conditional_list[conditional_index])
	#print(result)
	return result
	
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
