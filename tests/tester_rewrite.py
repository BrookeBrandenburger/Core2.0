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
        self.ai = ai

        # Positionals
        self.heading: float = float(ai.selfHeadingDeg())
        self.tracking: float = float(ai.selfTrackingDeg())

        self.headingFeelers: List[int] = []
        self.trackingFeelers: List[int] = []

        # Genetic Data
        self.chrome: Optional[List[List[Any]]] = None #Decoded chromosome 
        self.chromosome_bin: Optional[List[List[str]]] = None # Binary chromosome, originally called chromosome or raw_chrome_values
        self.current_loop: Optional[List[List]] # Current loop in the chromosome 

        # Genetic Indices
        self.current_loop_idx: int = 0
        self.current_gene_idx: int = 0

        # Score Data
        self.score: int = 0
        self.prev_score: int = 0
        self.framesPostDeath: int = 0 

        # Enemy Data

        self.initializeAgent()
        self.generateFeelers(10)
        print("Alive!")

    # Create all needed wall feelers for the AI
    def generateFeelers(self, step: int) -> None: 
        # Tracking
        for angle in range(0, 360, step):
            self.trackingFeelers.append(ai.wallFeeler(500, int(self.tracking + angle)))

        # Heading
        for angle in range(0, 360, step):
            self.headingFeelers.append(ai.wallFeeler(500, int(self.heading + angle)))

    # Sets all needed values for a new agent, by default creates a new chromosome, a chromosome can be passed in.

    def initializeAgent(self, input_chrome: List[List] = generateChromosome()) -> None:
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

    def loop(self):
        print("Loop")

def ai_loop():
    global agent
    if agent is None:
        agent = CoreAgent()

    agent.loop()


    #print(agent.trackingFeelers)

def main():
    bot_num: str = "0"

    createDataFolder()
    global agent
    agent = None

    ai.start(ai_loop, ["-name", "Core Agent {}".format(bot_num), "-join", "localhost"])


if __name__ == "__main__":
    main()