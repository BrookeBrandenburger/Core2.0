
# Brooke, Aaron, Melanie
# Program 3

import libpyAI as ai
import math
import random
import csv
from numpy.random import randint
import random
import os
import shutil

# GA Stuff
class Population():
    
    def __init__(self):
        # HyperParameters
        self.GENE_SIZE: int = 16 # first 8 for nearDanger, 2nd 8 for alertDistance
        self.POP_SIZE: int = 100
        #self.CHROM_LEN: int = 8
        

        self.CROSS_RATE: float = 0.999
        self.MUT_RATE: float = 0.001

        self.GENERATIONS: int = 20
        self.LOG_FREQ: int = 2 # Every x generations log best chrom.
        
        self.pop: list[int] = []
        self.pop = self.generateChroms(self.GENE_SIZE, self.POP_SIZE)
        
        # Persistent Data
        self.current_gene: int = 0
        self.current_gen: int = 0
        self.new_pop: list[list[int]] = []
        self.avgFit: int = 0
        self.fitness_list: list[int] = []
        self.avgFits: list[int] = []
        
        #try:
        #    shutil.rmtree("GA_Data/")
        #except:
        #    pass
        
        #os.mkdir("GA_Data/") 
        
    
    def save_pop(self, fitness: list[int], generation: int) -> None:
        with open("GA_Data/" + str(generation) + "_final_pop.csv", "w") as f:
            for entry in zip(self.pop, fitness, strict=True):
                f.write(str(entry) + ",\n")
    
    def save_best(self, fitness: list[int], generation):
        max_fit = max(fitness)

        best_index = fitness.index(max_fit)
        best_chrom = self.pop[best_index]
        
        with open("GA_Data/" + str(generation) + "_best.csv", "w") as f:
            f.write("Best chromosome: " + str(best_chrom) + "\n" + \
                   "Max fitness: " + str(max_fit))
           
    @staticmethod
    def convertToNum(bitstring: list[int]) -> int:
        num = "0b"
        for i in bitstring:
            num += str(i)
        return int(num, 2)
        
    @staticmethod
    def generateChroms(chromSize: int, popSize: int) -> list[int]:
        pop = [randint(0, 2, chromSize).tolist() for _ in range(popSize)]
        return pop

    def fitness(self, fit: int) -> int:

        return fit**2 # Fitness func based on the more 1's the higher the score
        #return fitness

        
    def selection(self, F: list[int]) -> list[list[int]]:
        chroms = []
        pop = self.pop
        maxFit = sum(F)
        
        for _ in range(self.POP_SIZE):
            pick = random.uniform(0, maxFit)
            current = 0
            for i in range(len(pop)):
                current += F[i]
                if current > pick:
                    chroms.append(pop[i])
                    break
        return chroms

    def crossover(self, parent1: list[int], parent2: list[int]) -> list[list[int]]:
        c1 = parent1.copy()
        c2 = parent2.copy()

        if random.uniform(0, 1) < self.CROSS_RATE:
            splitPoint = random.randint(1, len(c1)-2)
            c1 = parent1[:splitPoint] + parent2[splitPoint:]
            c2 = parent2[:splitPoint] + parent1[splitPoint:]
            
            # Debugging
            #print(parent1)
            #print(parent2)
            #print(splitPoint)
            #print(c1)
            #print(c2)
            #print("="*20)
        return [c1, c2]

    def mutate(self, parent: list[int]) -> list[int]:
        for i in range(len(parent)):
            if random.uniform(0, 1) < self.MUT_RATE:
                parent[i] = 1 - parent[i]

        return parent

    def run(self, file=False): # An input file can be specified, but must be named input.txt and be in the same directory as this script.
        # Data folder
        try:
            shutil.rmtree("GA_Data/")
        except:
            pass
        
        os.mkdir("GA_Data/")  
        
        avgFits = []
        fitness = [0]
        genCount = 0

        if file:
            # open file, read file,
            data = []
            lines = None
            with open("input.txt", "r") as f:
                lines = f.read().split("\n")
                if lines[-1] == "":
                    lines = lines[:-1]

            
            for line in lines:
                line = line.split(", ")
                chrom = []
                for bit in line:
                    bit = bit.replace("(", "")
                    bit = bit.replace("[", "")
                    bit = bit.replace(")", "")
                    bit = bit.replace("]", "")

                    try:
                        bit = int(bit)
                    except:
                        bit = -1
                    if bit == 0 or bit == 1:
                        chrom.append(int(bit))


                data.append(chrom)

            self.pop = data
            self.POP_SIZE = len(data) 
            self.GENE_SIZE = len(data[0])
        else:
            self.pop = self.generateChroms(self.GENE_SIZE, self.POP_SIZE)

        while max(fitness) != self.GENE_SIZE:
            newPop = []
            avgFit = 0
            fitness = [self.fitness(gen) for gen in self.pop] # Fitness values for each chromosome
            selection = self.selection(fitness)

            for i in range(0, len(selection), 2):
                crossed = self.crossover(selection[i], selection[i+1])
                newPop.append(self.mutate(crossed[0]))
                newPop.append(self.mutate(crossed[1]))

            avgFit = sum(fitness)/len(fitness)
            avgFits.append(avgFit)
            random.shuffle(newPop) # Prevents only potentially breeding with neighbor
            if genCount % self.LOG_FREQ == 0:
                self.save_best(fitness, genCount)
            
            self.pop = newPop
            genCount += 1
        
        print("Population size: " + str(self.POP_SIZE))
        print("Final fitness: " + str(max(fitness)))
        print("Final generation #: " + str(genCount))
        self.save_pop(fitness, genCount)
        return avgFits


# Shooting stuff from Aaron/Melanie program2

scores = []
frames = []

def wallBetweenTarget(X, Y, ENEMY_X, ENEMY_Y):
    return ai.wallBetween(int(X), int(Y), int(ENEMY_X), int(ENEMY_Y)) != -1


def findAngle(X, ENEMY_X, ENEMY_DIST):  # Taking the X coordinates of agent and enemy
    hyp = ENEMY_DIST
    if ENEMY_X - X > 0:
        x_dist = ENEMY_X - X
    else:
        x_dist = X - ENEMY_X
    theta = int(math.degrees(math.acos(x_dist / hyp)))

    return theta

# Data Collection


def collect_data(feelers: list[float], desiredOut: int):
    with open('trainingData.txt', 'a', newline='\n') as csvfile:
        feelers.append(desiredOut)
        writer = csv.writer(csvfile)
        # print(feelers)
        writer.writerow(feelers)

# Neural Net functions:

# Function to return given speed's membership value in "slow"


def heuristic_speed_slow(speed):
    slow_mv = 0.0
    if speed <= 0.25:
        slow_mv = 1
    elif speed >= 3:
        slow_mv = 0
    else:
        slow_mv = -0.36*speed + 1.09
    return slow_mv

# Function to return given speed's membership value in "medium"


def heuristic_speed_medium(speed):
    medium_mv = 0.0
    if speed >= 3.5 and speed <= 4:
        medium_mv = 1
    elif speed <= 2 or speed >= 5:
        medium_mv = 0
    elif speed >= 2 and speed <= 3.5:
        medium_mv = 0.67*speed + 1.33
    else:
        medium_mv = -1*speed + 5
    return medium_mv

# Function to return given speed's membership value in "fast/high"


def heuristic_speed_high(speed):
    high_mv = 0.0
    if speed >= 5.5:
        high_mv = 1
    elif speed <= 4:
        high_mv = 0
    else:
        high_mv = 0.67*speed + 2.66
    return high_mv

# Function to return given distance from wall's membership value in "low collision risk"


def heuristic_wall_low(distance):
    low_mv = 0.0
    if distance == 0:
        low_mv = 1
    elif distance >= 200:
        low_mv = 0
    else:
        low_mv = 0.005*distance + 1
    return low_mv

# Function to return given distance from wall's membership value in "medium collision risk"


def heuristic_wall_medium(distance):
    medium_mv = 0.0
    if distance == 200:
        medium_mv = 1
    elif distance <= 100 or distance >= 300:
        medium_mv = 0
    elif distance >= 100 and distance <= 200:
        medium_mv = 0.01*distance - 1
    else:
        medium_mv = -0.01*distance + 3
    return medium_mv

# Function to return given distance from wall's membership value in "high collision risk"


def heuristic_wall_high(distance):
    high_mv = 0.0
    if distance >= 400:
        high_mv = 1
    elif distance <= 300:
        high_mv = 0
    else:
        high_mv = 0.01*distance - 4
    return high_mv

def died():
    frames.append(0)
    fitness = len(frames)
    died = False
    score = int(ai.selfScore())
    
    #if fitness >= 275:
    #    ai.selfDestruct()
    #    frames.clear()
    #    died = True
    #    return died, fitness

    
    if len(scores) == 0:
        scores.append(score)
        scores.append(score)
        
    elif len(scores) == 2:
        scores[1] = score # sets score 1 to new score
        
        if scores[0] != scores[1]:
            frames.clear()
            died = True
            #
            
        scores[0] = scores[1]

    #print(scores)
    return died, fitness
    


P = Population()
def AI_loop():
    try:
        # Enemy infos
        # Enemy variables Setup
        closestShipId = int(ai.closestShipId())

        ENEMY_SPEED = None
        ENEMY_DIST = None
        # ENEMY_RELOADTIME = None
        ENEMY_X = None
        ENEMY_Y = None
        ENEMY_HEADING = None

        if closestShipId != -1:
            ENEMY_SPEED = float(ai.enemySpeedId(closestShipId))
            ENEMY_DIST = float(ai.enemyDistanceId(closestShipId))
            # ENEMY_RELOADTIME = int(ai.enemyReloadId(closestShipId))
            ENEMY_X = int(ai.screenEnemyXId(closestShipId))
            ENEMY_Y = int(ai.screenEnemyYId(closestShipId))
            ENEMY_HEADING = float(ai.enemyHeadingDegId(closestShipId))

        # release keys
        ai.thrust(0)
        ai.turnLeft(0)
        ai.turnRight(0)
        speedLimit = 7 # 7


        nearDanger = P.convertToNum(gene[:8]) # Value to train GA
        # distance for close bullets (distance units)
        shotDanger = 130
        # backup distance threshold
        alertDistance = P.convertToNum(gene[8:]) # Value to train GA
        # handicap
        ai.setTurnSpeedDeg(20)
        power = 20
        ai.setPower(power)
        #print("nearDanger: " + str(nearDanger))
        #print(alertDistance)
        # get information
        heading = int(ai.selfHeadingDeg())
        tracking = int(ai.selfTrackingDeg())
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

        # get distances
        if ai.enemyDistanceId(ai.closestShipId()) > 0:
            closestPlayerDistance = ai.enemyDistanceId(ai.closestShipId())
        else:
            closestPlayerDistance = math.inf

        if ai.shotDist(0) > 0:
            closestBulletDistance = ai.shotDist(0)
        else:
            closestBulletDistance = math.inf

        # shortest feeler
        feeler = min(feelers)
        # nearest object (player or bullet)
        distToNearestThreat = min(closestPlayerDistance, closestBulletDistance)

        # Calculating current speed, and that speed's memberhsip values in slow, medium, and fast/high
        currSpeed = ai.selfSpeed()
        speed_slow_mv = heuristic_speed_slow(currSpeed)
        speed_medium_mv = heuristic_speed_medium(currSpeed)
        speed_high_mv = heuristic_speed_high(currSpeed)

        # Setting the wall distance to the variable trackWall from above, and finding that distance's membership value in low, medium, and high collision risk
        wallDist = trackWall
        wall_risk_low_mv = heuristic_wall_high(wallDist)
        wall_risk_medium_mv = heuristic_wall_medium(wallDist)
        wall_risk_high_mv = heuristic_wall_low(wallDist)

        # Membership values for power in high or low, to be calculated using the rules below
        powerValueH = 0
        powerValueL = 0

        # Counter to be used in calculation of a weighted average
        countH = 0
        countL = 0

        # Slow speed, low collision risk -> higher power
        if speed_slow_mv > 0 and speed_medium_mv < 0.2 and wall_risk_low_mv > 0:
            powerValueH = powerValueH + 1
            powerValueL = powerValueL + 0
            countH += 1

        # Slow speed, medium collision risk -> higher power
        if speed_slow_mv > 0 and speed_medium_mv < 0.2 and wall_risk_low_mv == 0 and wall_risk_high_mv != 0 and wall_risk_medium_mv < 0.5:
            powerValueH = powerValueH + 0.75
            powerValueL = powerValueL + 0
            countH += 1

        # High speed, high collision risk -> lower power
        if speed_high_mv != 0 and speed_medium_mv < 0.5 and wall_risk_low_mv > 0 and wall_risk_medium_mv < 0.5:
            powerValueH = powerValueH + 0.20
            powerValueL = powerValueL + 0.70
            countL += 1

        # Medium speed, medium collision risk -> equally high and low power
        if speed_medium_mv != 0 and speed_slow_mv < 0.3 and speed_high_mv < 0.4 and wall_risk_medium_mv != 0 and wall_risk_low_mv < 0.5 and wall_risk_high_mv < 0.4:
            powerValueH = powerValueH + 0.50
            powerValueL = powerValueL + 0.50
            countH += 1
            countL += 1

        # High speed, low collision risk -> lower power
        if speed_high_mv != 0 and speed_medium_mv < 0.5 and wall_risk_low_mv > 0:
            powerValueH = powerValueH + 0.40
            powerValueL = powerValueL + 0.60
            countL += 1

        # High speed, medium collision risk -> lower power
        if speed_high_mv != 0 and speed_medium_mv < 0.5 and wall_risk_medium_mv != 0 and wall_risk_low_mv < 0.5 and wall_risk_high_mv < 0.4:
            ppowerValueH = powerValueH + 0.30
            powerValueL = powerValueL + 0.90
            countL += 1

        # Medium speed, high collision risk -> lower power
        if speed_medium_mv != 0 and speed_slow_mv < 0.3 and speed_high_mv < 0.4 and wall_risk_low_mv > 0 and wall_risk_medium_mv < 0.5:
            powerValueH = powerValueH + 0.01
            powerValueL = powerValueL + 0.80
            countL += 1

        # Slow speed, high collision risk -> equally high and low power
        if speed_slow_mv > 0 and speed_medium_mv < 0.2 and wall_risk_low_mv > 0 and wall_risk_medium_mv < 0.5:
            powerValueH = powerValueH + 0.50
            powerValueL = powerValueL + 0.50
            countH += 1
            countL += 1

        # Weighted average part
        if powerValueH > powerValueL:
            power = (powerValueH/countH)*5+25
        elif powerValueL > powerValueH:
            power = (powerValueL/countL)*5+20
        else:
            power = 20

        ai.setPower(power)

        # assign priority to nearest threat
        # if closest threat is a wall
        if feeler <= closestPlayerDistance and feeler <= closestBulletDistance:
            priority = 1
        #if closest threat is a bullet
            #elif closestBulletDistance <= feeler and closestBulletDistance <= closestPlayerDistance:
            #priority = 2
        # closest threat is a player
        elif closestPlayerDistance <= 200:
            priority = 3
        else:
            priority = 1

        # the closest threat is a wall
        if priority == 1:
            # finds difference the heading and the tracking
            head_track_diff = int(180 - abs(abs(heading - tracking) - 180))
            # thrusting
            if ai.selfSpeed() <= speedLimit:
                ai.thrust(1)
            elif trackWall < nearDanger and head_track_diff > 90:
                ai.thrust(1)
            elif rearWall < nearDanger and head_track_diff > 90:
                ai.thrust(1)

            #turning ### (production system) ###
            if trackWall < nearDanger and leftWall < rightWall:
                ai.turnRight(1)
            elif trackWall < nearDanger and rightWall < leftWall:
                ai.turnLeft(1)
            elif backLeftWall < nearDanger and rightWall > 60:
                ai.turnRight(1)
            elif backRightWall < nearDanger and leftWall > 60:
                ai.turnLeft(1)
            elif frontRightWall < nearDanger:
                ai.turnLeft(1)
            elif frontLeftWall < nearDanger:
                ai.turnRight(1)
            elif frontWall <= alertDistance and (frontLeftWall < frontRightWall) and ai.selfSpeed() > 1:
                ai.turnRight(1)
            elif frontWall <= alertDistance and (frontLeftWall > frontRightWall) and ai.selfSpeed() > 1:
                ai.turnLeft(1)
            elif leftWall <= alertDistance and ai.selfSpeed() > 1:
                ai.turnRight(1)
            elif rightWall <= alertDistance and ai.selfSpeed() > 1:
                ai.turnLeft(1)

        # the closest threat is a bullet
        elif priority == 2:
            p1, p2 = (ai.selfX(), ai.selfY()), (ai.shotX(0), ai.shotY(0))
            # get the angle between self and nearest shot, relative to horizontal
            dx = p1[0] - p2[0]
            dy = p2[1] - p1[1]
            m = -1 * (int(math.degrees(math.atan2(dy, dx))) + 180) % 360
            # measure the difference between 'm' and selfs heading
            m = ((m - ai.selfHeadingDeg()) + 180) % 360 - 180

            if m >= 0:
                ai.turnRight(1)
            else:
                ai.turnLeft(1)
            if ai.shotAlert(0) < shotDanger:
                ai.thrust(1)

        # the closest threat is a player
        elif priority == 3:
            p1, p2 = (ai.selfX(), ai.selfY()
                      ), (ai.screenEnemyX(0), ai.screenEnemyY(0))
            # get the angle between self and nearest enemy, relative to horizontal
            dx = p1[0] - p2[0]
            dy = p2[1] - p1[1]
            m = -1 * (int(math.degrees(math.atan2(dy, dx))) + 180) % 360
            # get the difference between m2 and selfs heading
            m = ((m - ai.selfHeadingDeg()) + 180) % 360 - 180

            if m <= 0:
                ai.turnRight(1)
                ai.fireShot()
            else:
                ai.turnLeft(1)
                ai.fireShot()
            if ai.selfHeadingDeg() <= (5 + m) and ai.selfHeadingDeg() >= (5 - m):
                ai.fireShot()

        ai.fireShot()
        dead = died()
        
        if False: #dead[0]
            fit = dead[1]
            
            P.current_gene += 1
            print("Completed Life: " + str(P.current_gene))

            P.fitness_list.append(P.fitness(fit))
            print(P.fitness_list)

            if P.current_gene == P.POP_SIZE:
                P.current_gen += 1
                P.current_gene = 0
                selection = P.selection(P.fitness_list)
                print("Generation complete: " + str(P.current_gen))

                for i in range(0, len(selection), 2):
                    crossed = P.crossover(selection[i], selection[i+1])
                    P.new_pop.append(P.mutate(crossed[0]))
                    P.new_pop.append(P.mutate(crossed[1]))

                P.avgFit = sum(P.fitness_list)/len(P.fitness_list)
                P.avgFits.append(P.avgFit)
                random.shuffle(P.new_pop)
                
                if P.current_gen % P.LOG_FREQ == 0:
                    P.save_best(P.fitness_list, P.current_gen)
                
                P.save_pop(P.fitness_list, P.current_gen)
                P.pop = P.new_pop

                # Resets
                P.fitness_list = []
                P.new_pop = []
                P.avgFit = 0
            #print(dead[1])

    
    except Exception as e:
        print("Exception")
        print(e)
        ai.quitAI()

ai.start(AI_loop, ["-name", "BAM!", "-join", "localhost"])
