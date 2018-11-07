import json

class Maze:
    def __init__(self, width, bit_array):
        self.width = width
        self.maze = bit_array
        if not bit_array or not width:
            self.load_maze_from_file()

    def load_maze_from_file(self):
        f = open('game/maze.txt', 'r')
        data = json.load(f)
        self.width = data[0]
        self.maze = data[1]    

    def as_json(self):
        return json.dumps((self.width, self.maze))
    
    def from_json(self, json_data):
        data = json.loads(json_data)
        self.width = data[0]
        self.maze = data[1]