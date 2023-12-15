import libpyAI as ai
import math
import random
import os
import sys
import traceback
from typing import Union, List, Any, Optional

from chromosome import readChrome, createDataFolder, crossover, mutate, generateChromosome, writeChromosomeToFile

class CoreAgent():
    # Agent initializer
    def __init__(self) -> None:
        # Properties
        self.MUT_RATE: int = 300


        # Positionals
        self.heading: float = float(ai.selfHeadingDeg())
        self.tracking: float = float(ai.selfTrackingDeg())

        self.headingFeelers: List[int] = []
        self.trackingFeelers: List[int] = []

        self.X: int = -1
        self.Y: int = -1
        self.heading: float = 90.0
        self.speed: float = -1

        # Genetic Data
        self.bin_chromosome: Optional[List[List[str]]] = None # Binary chromosome, originally called chromosome or raw_chrome_values
        self.dec_chromosome: Optional[List[List[Any]]] = None #Decoded chromosome 
        self.current_loop: Optional[List[List]] # Current loop in the chromosome 

        # Genetic Indices
        self.current_loop_idx: int = 0
        self.current_gene_idx: int = 0

        # Score Data
        self.score: int = 0
        self.prev_score: int = 0
        self.framesPostDeath: int = 0 

        # Enemy Data
        self.enemy_dist: float = -1
        self.enemy_dir: int = -1
        self.enemy_x: int = -1
        self.enemy_y: int = -1
        self.enemy_speed: float = -1
        self.enemy_heading: float = -1

        # Bullet Data
        self.closest_bullet_distance: float = -1

        self.initializeAgent()
        self.generateFeelers(10)
        print("Alive!")

    # AI LOOP
    def AI_Loop(self) -> None:
        self.updateAgentData()
        self.updateEnemyData()
        self.updateBulletData()
        self.updateScore()

        #print(self.score)
        #print(self.X)
        #print(self.Y)
        #print(self.enemy_speed)

    def updateScore(self) -> None:
        self.prev_score = self.score
        self.score = ai.selfScore()

    # Update agent's positions, data, etc:
    def updateAgentData(self) -> None:
        self.X = int(ai.selfX())
        self.Y = int(ai.selfY())
        self.speed = float(ai.selfSpeed())

    # Update enemy data
    def updateEnemyData(self) -> None:
        closest_ship_id: int = int(ai.closestShipId()) 

        if closest_ship_id != -1:
            self.enemy_dist = float(ai.enemyDistanceId(closest_ship_id))
            
            self.enemy_x = int(ai.screenEnemyXId(closest_ship_id))
            self.enemy_y = int(ai.screenEnemyYId(closest_ship_id))
            self.enemy_speed = float(ai.enemySpeedId(closest_ship_id))
            self.enemy_heading = float(ai.enemyHeadingDegId(closest_ship_id))

            self.enemy_dir = self.getEnemyDirection()
        else: 
            self.enemy_dist = -1
            
            self.enemy_x = -1
            self.enemy_y = -1
            self.enemy_speed = -1
            self.enemy_heading = -1

            self.enemy_dir = self.getEnemyDirection()
    # Update bullet data
    def updateBulletData(self) -> None:
        if ai.shotDist(0) > 0:
            self.closest_bullet_distance = float(ai.shotDist(0))
        else:
            self.closest_bullet_distance = -1

    # Create all needed wall feelers for the AI
    def generateFeelers(self, step: int) -> None: 
        # Tracking
        for angle in range(0, 360, step):
            self.trackingFeelers.append(ai.wallFeeler(500, int(self.tracking + angle)))

        # Heading
        for angle in range(0, 360, step):
            self.headingFeelers.append(ai.wallFeeler(500, int(self.heading + angle)))

        # Heading/Tracking individuals
        self.heading = float(ai.selfHeadingDeg())
        self.tracking = float(ai.selfTrackingDeg())

    # Sets all needed values for a new agent, by default creates a new chromosome, a chromosome can be passed in.

    def initializeAgent(self, input_chrome: List[List[str]] = generateChromosome()) -> None:
        self.bin_chromosome = input_chrome
        self.dec_chromosome = readChrome(self.bin_chromosome)

        print("Chromosome: {}".format(self.dec_chromosome))

        # Reset place in chromosome
        self.current_loop_idx = 0  # Current Loop Number
        self.current_loop = self.dec_chromosome[0]
        self.current_gene_idx = 0  # Current gene Number within a given loop


# Checks if a kill has been made, if yes -> write it to file and send the file name to chat

    def earnedKill(self) -> None:
        filename: str = "selChrome_0.txt"  # Baseline file name

        # Modify file ending for pre-existing files
        while os.path.exists(("data/" + filename)):
            # Get the number at end of file name
            index: Union[int, str] = int((filename.split("_")[1]).split(".")[0])
            index = str(index+1)
            filename = "selChrome_{}.txt".format(index)

        # Score increment indicates a kill
        if self.score > self.prev_score:
            writeChromosomeToFile(self.bin_chromosome, filename)
            ai.talk('New Chrome File -' + filename)  # Chat the file name

    # Checks if the agent has died, if yes and it was killed by another agent
    # finds the chromosome file, and initalizes it as its new chromosome

    def died(self) -> None:
        # Start frame counter after a negative score change
        if self.score < self.prev_score:
            self.framesPostDeath = 1
            #print("Score: {}".format(score))
            #print("Previous Score: {}".format(prev_score))

        if self.framesPostDeath >= 1 and self.framesPostDeath < 100:
            self.framesPostDeath += 1
        else:
            self.framesPostDeath = 0
        #print("Frames post Death: {}".format(framesPostDeath))

        # Score change and message with hyphen (indicating killed instead of wall collision)
        if (self.framesPostDeath != 0):
            message: str = ai.scanMsg(0)  # Get most recent chat message

            if "-" in message:  # Hyphen is only in our file messages from other agents
                self.framesPostDeath = 0
                print("Message: {}".format(message))

                if len(message) > 1:
                    print("Death and death message found")
                    # Extract filename from message
                    message = (message.split("-")[1]).split(" ")[0]
                    print("New Chrome filepath: {}".format(message))
                    new_chromosome_file_name: str = "data/" + message

                    new_chromosome: Union[None, List[List]] = None
                    with open(new_chromosome_file_name, 'r') as f:
                        new_chromosome = eval(f.read()) # TODO remove eval

                    # Evolution
                    #print("Transferred Chrome: {}".format(new_chromosome))
                    cross_over_child = crossover(self.bin_chromosome, new_chromosome)
                    #print("Crossover child: {}".format(cross_over_child))
                    mutated_child: List[List] = mutate(cross_over_child, self.MUT_RATE)
                    #print("Mutated child: {}".format(mutated_child))

                    # Check that the new chromosome is different than old, insanely low odds for it to be the same
                    # print("*"*50)
                    #print(mutated_child == chromosome)
                    # print("*"*50)

                    # Set new chromosome in place of old
                    self.initializeAgent(mutated_child)

    # Relative to us

    def findMinWallAngle(self, wallFeelers: List[int]) -> int:
        min_wall: int = min(wallFeelers)
        min_index: int = wallFeelers.index(min_wall)

        angle: int = int(10*min_index)

        if angle < 180:  # wall to the right
            return angle
        else:
            return angle - 360

    # Relative to us
    def findMaxWallAngle(self, wallFeelers: List[int]) -> int:
        max_wall: int = max(wallFeelers)
        max_index: int = wallFeelers.index(max_wall)

        angle: int = int(10*max_index)

        if angle < 180:  # wall to the right
            return angle
        else:
            return angle - 360

    # Relative to world internally, returns relative to us

    def findAngle(self) -> int:
        new_enemy_x: int = self.enemy_x - self.X
        new_enemy_y: int = self.enemy_y - self.Y

        enemy_angle: float
        # If positive, enemy to right
        # If negative, enemy to left
        try:
            enemy_angle = math.degrees(math.atan(new_enemy_y/new_enemy_x))
        except:
            enemy_angle = 0  # in the case of division by 0

        angleToEnemy: int = int(self.heading - enemy_angle)

        if angleToEnemy < 360 - angleToEnemy:  # enemy to the right
            return angleToEnemy
        else:
            return angleToEnemy - 360

    def checkConditional(self, conditional_index: int) -> bool: 
        min_wall_dist: int = min(self.headingFeelers)
        closestBulletDistance: float = -1 # TODO 

        # 16 conditionals Core 2.0 in Action
        conditional_List = [self.speed > 6, self.speed == 0,
                            self.enemy_dist < 50, self.enemy_dist > 200,
                            self.enemy_dist < 100 and self.enemy_dir == 1,
                            self.enemy_dist < 100 and self.enemy_dir == 2,
                            # True,
                            self.enemy_dist < 100 and self.enemy_dir == 3,
                            self.enemy_dist < 100 and self.enemy_dir == 4,
                            min_wall_dist < 200, min_wall_dist < 75, min_wall_dist > 300, min_wall_dist < 150,
                            closestBulletDistance < 100, closestBulletDistance < 200, closestBulletDistance <50,
                            self.enemy_dist == -1
                            ]

        result = conditional_List[conditional_index]
        return result


    def wallBetweenTarget(self) -> bool:
        return ai.wallBetween(int(self.X), int(self.Y), int(self.enemy_x), int(self.enemy_y)) != -1


    def getEnemyDirection(self) -> int:
        direction: int = -1

        theta: Union[float, None] = None
        wallPreEnemy: Union[bool, None] = False
        shotTolerance: int = random.randint(-5, 5)

        if self.enemy_dist != -1:
            xDistToEnemy = self.enemy_x - self.X
            yDistToEnemy = self.enemy_y - self.Y
            theta = self.findAngle()
            wallPreEnemy = self.wallBetweenTarget()

        else:
            xDistToEnemy = 0
            yDistToEnemy = 0

        if self.enemy_dist and xDistToEnemy > 0 and yDistToEnemy > 0 and not wallPreEnemy:  # Q1
            direction = 1
        elif self.enemy_dist and xDistToEnemy < 0 and yDistToEnemy > 0 and not wallPreEnemy:  # Q2
            direction = 2
        elif self.enemy_dist and xDistToEnemy < 0 and yDistToEnemy < 0 and not wallPreEnemy:  # Q3
            direction = 3
        elif self.enemy_dist and xDistToEnemy > 0 and yDistToEnemy < 0 and not wallPreEnemy:  # Q4
            direction = 4

        return direction


def AI_loop():
    try:
        global headingFeelers
        global trackingFeelers
        global started

        # get information
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
        enemy_x: Union[int, None] = None
        enemy_y: Union[int, None] = None
        ENEMY_HEADING: Union[float, None] = None

        if closestShipId != -1:
            ENEMY_SPEED = float(ai.enemySpeedId(closestShipId))
            ENEMY_DIST = float(ai.enemyDistanceId(closestShipId))
            enemy_x = int(ai.screenEnemyXId(closestShipId))
            enemy_y = int(ai.screenEnemyYId(closestShipId))
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
                   closestBulletDistance, enemy_x, enemy_y, X, Y, heading]

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
                            X, Y, enemy_x, enemy_y, heading)

                        if angleToEnemy < 0:
                            ai.turn(-1*turnQuantity)
                        elif angleToEnemy > 0:
                            ai.turn(turnQuantity)

                case 5:
                    # turn away from enemy ship
                    if ENEMY_DIST != None:
                        angleToEnemy: int = findAngle(
                            X, Y, enemy_x, enemy_y, heading)

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


def loop():
    global agent
    if agent is None:
        agent = CoreAgent()

    agent.AI_Loop()

def main():
    bot_num: str = "000"

    createDataFolder()
    global agent

    agent = None

    ai.start(
        loop, ["-name", "Core Agent {}".format(bot_num), "-join", "localhost"])


if __name__ == "__main__":
    main()
