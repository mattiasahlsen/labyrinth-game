import json
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
