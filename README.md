# labyrinth-game
An online multiplayer maze game in python3 using pygame and tcp. The
maze is automatically and randomly generated using a depth-first search algorithm, https://en.wikipedia.org/wiki/Maze_generation_algorithm#Depth-first_search

## Goal
Be the first one to get to the middle of the maze and get the coin. Simple, right?

## Dependencies
- Python 3
- pygame: `python3 -m pip install pygame`

## Usage
Make sure you have the dependencies:

`python3 -m pip install pygame`

Clone the repository:

`git clone https://github.com/mattiasahlsen/labyrinth-game.git`<br/>
`cd labyrinth-game`

Start the server.

`python3 server/server.py` or `make run-server`

Start the right amount of clients and connect to the server's IP.

`python3 client/client.py` or `make run-client`

You're good to go!

## Commands
- Server: `python3 server/server.py` or `make run-server`
- Client: `python3 client/client.py` or `make run-client`

## Other info
Currently using port 15000 so
it must be available.
