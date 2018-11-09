import json
from random import randint
from os import path

class Maze:
    def __init__(self, json_data=None):
        if not json_data:
            self.load_maze_from_file()
        else:
            self.from_json(json_data)

    def load_maze_from_file(self):
        file = open(path.dirname(path.realpath(__file__)) + '/maze.json', 'r')
        data = file.read()
        self.from_json(data)

    def as_json(self):
        data = dict([('width', self.width),
                     ('max_players', self.max_players),
                     ('starting_locations', self.starting_locations),
                     ('goal', self.goal),
                     ('bit_array', self.maze)])
        return json.dumps(data)

    def from_json(self, json_data):
        data = json.loads(json_data)
        self.width              = data['width']
        self.max_players        = data['max_players']
        self.starting_locations = data['starting_locations']
        self.goal               = data['goal']
        self.maze               = data['bit_array']

def random_maze(width=100, complexity=.1, density=.1, players=4):
    two_d_array = sub_maze(width, complexity, density)

    # Convert 2D array to 1D array
    bit_array = []
    for row in two_d_array:
        for bit in row:
            bit_array.append(bit)

    goal = goal_pos(bit_array, (width // 2) * 2 + 1)
    start_pos = starting_positions(two_d_array, players, goal)

    j = dict([
        ('width', (width // 2) * 2 + 1),
        ('max_players', players),
        ('starting_locations', start_pos),
        ('goal', goal),
        ('bit_array', bit_array)
    ])

    return Maze(json.dumps(j))

# sub_maze() returns a 2-d array of bits
def sub_maze(width, complexity, density):
    # Only odd shapes
    shape = ((width // 2) * 2 + 1, (width // 2) * 2 + 1)
    # Adjust complexity and density relative to maze size
    complexity = int(complexity * (5 * (shape[0] + shape[1]))) # number of components
    density    = int(density * ((shape[0] // 2) * (shape[1] // 2))) # size of components
    # Build actual maze
    Z = []
    for i in range(shape[0]):
        Z.append([])
        for j in range(shape[0]):
            Z[i].append(0)

    # Make aisles
    for i in range(density):
        x, y = randint(0, shape[1] // 2) * 2, randint(0, shape[0] // 2) * 2 # pick a random position
        Z[y][x] = 1
        for j in range(complexity):
            neighbours = []
            if x > 1:             neighbours.append((y, x - 2))
            if x < shape[1] - 2:  neighbours.append((y, x + 2))
            if y > 1:             neighbours.append((y - 2, x))
            if y < shape[0] - 2:  neighbours.append((y + 2, x))
            if len(neighbours):
                y_,x_ = neighbours[randint(0, len(neighbours) - 1)]
                if Z[y_][x_] == 0:
                    Z[y_][x_] = 1
                    Z[y_ + (y - y_) // 2][x_ + (x - x_) // 2] = 1
                    x, y = x_, y_
    return Z

def goal_pos(array, width):
    goal = (width // 2, width // 2)

    while array[goal[1] * width + goal[0]]:
        goal = (goal[0], goal[1] + 1)        

    return goal

def starting_positions(array, players, goal):
    positions = []

    position = goal
    for i in range(players):
        steps = 0
        while steps < len(array) * 100:
            vel = (randint(0, 2) - 1, randint(0, 2) - 1)

            while position[1] + vel[1] >= len(array) or position[1] + vel[1] < 0 or position[0] + vel[0] >= len(array) or position[0] + vel[0] < 0 or array[position[1] + vel[1]][position[0] + vel[0]]:
                vel = (randint(0, 2) - 1, randint(0, 2) - 1)
            position = (position[0] + vel[0], position[1] + vel[1])
            steps += 1
        positions.append(position)
    return positions
