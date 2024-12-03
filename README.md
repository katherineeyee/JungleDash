# Jungle Dash

## Overview

Jungle Dash, is an easy-to-learn, single player 2D continuous platformer game developed using Python and its Arcade library. The game is centered around a monkey running through a jungle while collecting bananas and avoiding obstacles. The objective of Jungle Dash is to collect as many bananas as possible to improve the score and the monkey’s health, while avoiding the different obstacles coming towards the monkey at various times, which will damage the monkey’s health. Once the monkey’s health is drained completely, the game will end and can be restarted once again.

## Features

### Monkey

The monkey is the main character that the player controls.
The monkey’s default state will be a running state, but the player can use the spacebar to make the monkey jump.
The monkey’s states consist of running, jumping, crashing, and surfing, based on the player’s actions and interactions within the game.

### Bananas

The bananas are scattered throughout the jungle and come in three types:
Regular Banana: Adds ten points to the player's score and three points to the monkey’s health.
Special/Rainbow Banana: Doubles the number of points to the score and the monkey’s health for each banana collected for five seconds. The monkey’s surfing state is also activated.
Shield Bananas: Protects the monkey from taking any damage to its health even if it encounters an obstacle for five seconds.

### Obstacles

The game includes two main types of obstacles:
Jungle Plants: Located on ground level and of varying heights, these will decrease the monkey's health by twenty points
Flying Birds: Located above ground level and varying vertical positions, these will decrease the monkey's health by twenty points

### Floating Platforms

Floating platforms appear in different vertical positions and allow the monkey to jump to higher platform areas to collect additional bananas. If the monkey is underneath a platform and jumps, the platform will be broken. If the monkey jumps another time, the platform will be destroyed completely, the monkey can collect the bananas above the platform.

### Game Environment

The jungle setting includes a jungle background, moving clouds, and a camera that follows the monkey. The speed of the game increases slowly as the monkey is able to survive for longer. The player can monitor the monkey’s health by the health bar and the game score and duration.

## Instructions to Run Jungle Dash

### System Requirements

`Python 3.7` or higher

Required Modules: arcade

### Setup and Installation

Download and install Python

Install the Arcade library using the following command
`pip install arcade`

Download the game files, including the assets folder

### Running the Game

Navigate to the directory containing the game files in a terminal or command prompt

Execute the following command:
`python main.py`

### Game Controls

`SPACE`: Jump

`UP/DOWN` Arrow Keys: Navigate vertically during power-up surfing mode.

`ESC`: Exit the game

### How to Play

Objective:
Collect as many bananas as possible while avoiding obstacles. Power-ups can help you achieve higher scores or avoid damage.

Health and Score:
Health decreases upon collision with obstacles.
Collect bananas to regain health and increase your score.

End Condition:
The game ends when the monkey's health bar is fully depleted.
