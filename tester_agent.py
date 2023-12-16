import libpyAI as ai
import math
import random
import os
import sys
import traceback
from typing import Union, List, Any, Optional
import shutil
from chromosome import Evolver


class CoreAgent():
    # Agent initializer
    def __init__(self, bot_name: str) -> None:
        # Properties
        self.MUT_RATE: int = 300
        self.GENES_PER_LOOP: int = 8
        self.bot_name = bot_name

        # Positionals
        self.heading: float = float(ai.selfHeadingDeg())
        self.tracking: float = float(ai.selfTrackingDeg())

        self.headingFeelers: List[int] = []
        self.trackingFeelers: List[int] = []

        self.X: int = -1
        self.Y: int = -1
        self.heading: float = 90.0
        self.speed: float = -1

        # X-Pilot Settings
        ai.setTurnSpeed(20.0)
        ai.setPower(8)

        # Genetic Data
        self.bin_chromosome: Optional[List[List[str]]] = None  # Binary chromosome, originally called chromosome or raw_chrome_values
        self.dec_chromosome: Optional[List[List[Any]]] = None  #Decoded chromosome 
        self.current_loop: Optional[List[List]] = None  # Current loop in the chromosome 

        # Genetic Indices
        self.current_loop_idx: int = 0
        self.current_gene_idx: int = 0

        # Score Data
        self.score: int = 0
        self.prev_score: int = 0
        self.framesPostDeath: int = 0 
        self.feed_history: List[str] = [''*5] # Only stores server messages relevant to agent
        self.last_death: List[str] = ["null", "null"]
        self.last_kill: List[str] = ["null", "null"]
        self.frames_post_pause = 0
        self.feed_pause = False
        self.prior_death = ["null", "null"]
        self.crossover_completed = False
        self.self_destructed = False

        # Enemy Data
        self.enemy_dist: float = -1
        self.enemy_dir: int = -1
        self.enemy_x: int = -1
        self.enemy_y: int = -1
        self.enemy_speed: float = -1
        self.enemy_heading: float = -1

        # Bullet Data
        self.closest_bullet_distance: float = -1
        self.shot_x: int = -1
        self.shot_y: int = -1
        self.angle_to_shot: int = -1

        #self.createTracebackFolder()
        self.initializeCGA()
        self.generateFeelers(10)
        print("Alive!")

        self.frames_dead: int = 0
    @classmethod
    def createTracebackFolder(cls):
        # Data folder
        try:
            shutil.rmtree("tracebacks/")
        except:
            pass

        os.mkdir("tracebacks/")

    # AI LOOP
    def AI_Loop(self) -> None:
        try:
            if ai.selfAlive() == 1:  # Alive
                self.frames_dead = 0
                self.updateAgentData()
                self.updateEnemyData()
                self.updateBulletData()
                self.updateScore()
                
                #self.processServerFeed()
                #self.wasKilled()
                self.crossover_completed = False
                self.self_destructed = False
                
                # if self.frames_post_pause < 200 and self.feed_pause:
                #     self.frames_post_pause += 1
                # else:
                #     self.frames_post_pause = 0
                #     self.feed_pause = 0
                gene: List[Any] = self.current_loop[self.current_gene_idx]
                #print("Gene: {}".format(gene))
                if Evolver.isJumpGene(gene):   # If gene is a jump gene
                    if self.checkConditional(gene[1]):  # If the conditional is true
                        # Jump
                        self.current_loop_idx = gene[2]
                        self.current_loop = self.dec_chromosome[self.current_loop_idx]
                        self.current_gene_idx = 0
        
                        # TODO : Make this check repeat so we always execute an action in any given frame
                        return  # End current iteration to start at new cycle
                    else:  # The conditional is not true
                        self.incrementGeneIndex()
                gene = self.current_loop[self.current_gene_idx]

                # Action gene
                ActionGene(gene, self)
                self.incrementGeneIndex()

            else:  # Dead
                self.processServerFeed()
                self.frames_dead += 1
                if self.frames_dead >= 5:
                    
                    self.wasKilled()

                    self.frames_dead = -2000

        except Exception as e:
            print("Exception")
            print(str(e))
            traceback.print_exc()

            traceback_str = traceback.format_exc()

            # Write the traceback to file
            with open("tracebacks/traceback_{}.txt".format(bot_name), "w") as file:
                file.write(traceback_str)
                file.write(str(self.bin_chromosome))
                file.write(str(self.dec_chromosome))
                file.write(str(self.current_loop))

            ai.quitAI()

    def incrementGeneIndex(self) -> int:
        self.current_gene_idx = ((self.current_gene_idx + 1) % self.GENES_PER_LOOP)
        return self.current_gene_idx

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
            
            self.angle_to_enemy = int(self.findAngle())
            self.enemy_dir = self.getEnemyDirection()
        else: 
            self.enemy_dist = -1
            
            self.enemy_x = -1
            self.enemy_y = -1
            self.enemy_speed = -1
            self.enemy_heading = -1

            self.angle_to_enemy = -1
            self.enemy_dir = -1

    # Update bullet data
    def updateBulletData(self) -> None:
        if ai.shotDist(0) > 0:
            self.closest_bullet_distance = float(ai.shotDist(0))
            self.shot_x = ai.shotX(0)
            self.shot_y = ai.shotY(0)
            self.angle_to_shot = self.findAngle("bullet")

        else:
            self.closest_bullet_distance = -1
            self.shot_x = -1
            self.shot_y = -1
            self.angle_to_shot = -1

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

    def initializeCGA(self, input_chrome: List[List[str]] = Evolver.generateChromosome()) -> None:
        self.bin_chromosome = input_chrome
        self.dec_chromosome = Evolver.readChrome(self.bin_chromosome)

        print("Chromosome: {}".format(self.bin_chromosome))

        # Reset kills/death record
        self.last_kill = ["null", "null"]
        self.last_death = ["null", "null"]

        # Reset place in chromosome
        self.current_loop_idx = 0  # Current Loop Number
        self.current_loop = self.dec_chromosome[0]
        self.current_gene_idx = 0  # Current gene Number within a given loop
        Evolver.writeChromosomeToFile(self.bin_chromosome, "{}.txt".format(self.bot_name))  # noqa: E501

    # Checks if a kill has been made, if yes -> write it to file and send the file name to chat

    # Returns a kill, in the format of [killer, victim]
    def processServerFeed(self) -> None:
        self.feed_history = []
        #sleep(0.1)
        for i in range(5):
            serverMessage = ai.scanGameMsg(i)
            #print(serverMessage)
            if self.bot_name in serverMessage and "ratio" not in serverMessage and "crashed" not in serverMessage and "entered" not in serverMessage:
                self.feed_history.append(serverMessage)

        #print(self.feed_history)
        killer = "null"
        victim = "null"
        #print(self.feed_history)
        for message in self.feed_history:
            if "killed" in message:
                victim = message.split(" was")[0]
                killer = message.split("from ")[-1][:-1]  # remove period from end
                break
            elif "smashed" in message:
                #  print("Self destructed")
                self.last_death = [killer,  victim]
                return

        # reset to nones on ai.self alive is false
        output = [killer, victim]
        #if "null" not in output:
        #    print(output)
        if killer == self.bot_name:
            self.last_kill = output
        elif victim == self.bot_name:
            self.last_death = output

    #def earnedKill()
    def earnedKill(self) -> None:
        filename: str = "{}.txt".format(bot_name)  # Baseline file name

        # Modify file ending for pre-existing files
        while os.path.exists(("data/" + filename)):
            # Get the number at end of file name
            index: Union[int, str] = int((filename.split("_")[1]).split(".")[0])
            index = str(index+1)
            filename = "selChrome_{}.txt".format(index)

        # Score increment indicates a kill
        if self.score > self.prev_score:
            Evolver.writeChromosomeToFile(self.bin_chromosome, filename)
            ai.talk('New Chrome File -' + filename)  # Chat the file name

    # Checks if the agent has died, if yes and it was killed by another agent
    # finds the chromosome file, and initalizes it as its new chromosome

    def startFeedPause(self) -> None:
        self.feed_pause = True
        self.frames_post_pause = 0

    def wasKilled(self) -> None:
        print(self.last_death)
        if "null" in self.last_death: 
            return
        #  print(self.last_death)

        if (ai.selfAlive() == 0) and self.crossover_completed is False:  # If dead
            # We've been killed by an another agent.
            new_chromosome_file_name: str = "data/" + "{}.txt".format(self.last_death[0])

            new_chromosome: Union[None, List[List]] = None
            with open(new_chromosome_file_name, 'r') as f:
                new_chromosome = eval(f.read())  # TODO remove eval

            # Evolution
            cross_over_child = Evolver.crossover(self.bin_chromosome, new_chromosome)
            print("Crossover_child: {}".format(cross_over_child))
            mutated_child: List[List] = Evolver.mutate(cross_over_child, self.MUT_RATE)
            print("Mutated_child: {}".format(mutated_child))
            # Set new chromosome in place of old
            self.initializeCGA(mutated_child)

            self.crossover_completed = True
            self.self_destructed = False
        
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
    # No parameters for enemy version
    def findAngle(self, param=None) -> int:
        if param is None:
            new_enemy_x: int = self.enemy_x - self.X
            new_enemy_y: int = self.enemy_y - self.Y
        else:
            new_enemy_x: int = self.shot_x - self.X
            new_enemy_y: int = self.shot_y - self.Y

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

        # 16 conditionals Core 2.0 in Action
        conditional_List = [self.speed > 6, self.speed == 0,
                            self.enemy_dist < 50, self.enemy_dist > 200,
                            self.enemy_dist < 100 and self.enemy_dir == 1,
                            self.enemy_dist < 100 and self.enemy_dir == 2,
                            # True,
                            self.enemy_dist < 100 and self.enemy_dir == 3,
                            self.enemy_dist < 100 and self.enemy_dir == 4,
                            min_wall_dist < 200, min_wall_dist < 75, min_wall_dist > 300, min_wall_dist < 150,
                            self.closest_bullet_distance < 100, self.closest_bullet_distance < 200, self.closest_bullet_distance <50,
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
            return -1

        if self.enemy_dist and xDistToEnemy > 0 and yDistToEnemy > 0 and not wallPreEnemy:  # Q1
            direction = 1
        elif self.enemy_dist and xDistToEnemy < 0 and yDistToEnemy > 0 and not wallPreEnemy:  # Q2
            direction = 2
        elif self.enemy_dist and xDistToEnemy < 0 and yDistToEnemy < 0 and not wallPreEnemy:  # Q3
            direction = 3
        elif self.enemy_dist and xDistToEnemy > 0 and yDistToEnemy < 0 and not wallPreEnemy:  # Q4
            direction = 4

        return direction


class ActionGene():
    def __init__(self, gene: List[Any], agent: CoreAgent) -> None:
        if gene[0] == False:  # Indicates jump gene
            print(gene)
            print("Unexpected action gene found")
            return None

        self.agent: CoreAgent = agent # Parent agent

        self.shoot: bool = gene[1]
        self.thrust: int = (1 if gene[2] else 0)
        self.turn_quantity: int = int((gene[3] + 3) * 2) # Ranges from 6-20 in steps of 3.
        self.turn_target: int = gene[4]

        self.act()

    def turn(self) -> None:
        # Pick turn target based on numerical identifier from loop.
        # Examples from paper: nearestShip, oppsoiteClosestWall, most dangerous bullet etc
        match self.turn_target:
            case 0:
                # turn towards closest wall heading
                angle: int = agent.findMinWallAngle(agent.headingFeelers)

                if angle < 0:
                    ai.turn(-1*self.turn_quantity)
                elif angle > 0:
                    ai.turn(self.turn_quantity)
            case 1:
                # turn away from closest wall heading
                angle: int = agent.findMinWallAngle(agent.headingFeelers)

                if angle > 0:
                    ai.turn(-1*self.turn_quantity)
                elif angle < 0:
                    ai.turn(self.turn_quantity)
            case 2:
                # turn towards furthest wall heading
                angle: int = agent.findMaxWallAngle(agent.headingFeelers)

                if angle < 0:
                    ai.turn(-1*self.turn_quantity)
                elif angle > 0:
                    ai.turn(self.turn_quantity)
            case 3:
                # turn away from furthest wall heading
                angle: int = agent.findMaxWallAngle(agent.headingFeelers)

                if angle > 0:
                    ai.turn(-1*self.turn_quantity)
                elif angle < 0:
                    ai.turn(self.turn_quantity)
            case 4:
                # turn towards enemy ship
                if agent.enemy_dist != None:

                    if agent.angle_to_enemy < 0:
                        ai.turn(-1*self.turn_quantity)
                    elif agent.angle_to_enemy > 0:
                        ai.turn(self.turn_quantity)

            case 5:
                # turn away from enemy ship
                if agent.enemy_dist != None:

                    if agent.angle_to_enemy > 0:
                        ai.turn(-1*self.turn_quantity)
                    else:
                        ai.turn(self.turn_quantity)

            case 6:
                # turn towards bullet
                if agent.shot_x != -1:
                    if agent.angle_to_shot < 0:
                        ai.turn(-1*self.turn_quantity)
                    elif agent.angle_to_shot > 0:
                        ai.turn(self.turn_quantity)

            case 7:
                # turn away from bullet
                if agent.shot_x != -1:
                    if agent.angle_to_shot > 0:
                        ai.turn(-1*self.turn_quantity)
                    elif agent.angle_to_shot < 0:
                        ai.turn(self.turn_quantity)

    def act(self) -> None:
        ai.thrust(self.thrust)
        ai.fireShot() if self.shoot else None
        self.turn()


def loop():
    global agent
    global bot_name
    if agent is None:
        agent = CoreAgent(bot_name)

    agent.AI_Loop()
    #agent.wasKilled()

def main():
    global bot_name
    bot_name = "Core_Agent_{}".format(sys.argv[1])

    global agent

    agent = None

    ai.start(
        loop, ["-name", bot_name, "-join", "localhost"])


if __name__ == "__main__":
    main()
