# labyrinth-game
An online multiplayer maze game in python3 using pygame and tcp. The
maze is of chosen size and automatically and randomly generated using an algorithm.

## Goal
Be the first one to get to the middle of the maze and get the coin. Simple, right?

## Dependencies
- Python 3, not sure which exact version (3.6.5 works).<br/>
- pygame: `python3 -m pip install pygame`

## Usage
Make sure you have the dependencies:<br/>
- `python3 -m pip install pygame`<br/>
Clone this repository using this command: <br/>
`git clone https://github.com/mattiasahlsen/labyrinth-game.git`<br/>
`cd labyrinth-game`

Start the server. <br/>
`python3 server/server.py` or `make run-server`<br/>
Start the right amount of clients and connect to the server's IP.<br/>
`python3 client/client.py` or `make run-client`

You're good to go!

## Commands
- Server: `python3 server/server.py` or `make run-server`
- Client: `python3 client/client.py` or `make run-client`

## Other info
Currently using port 15000 so
it must be available.
