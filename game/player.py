class Player:
    def __init__(self, player_number, location):
        self.id = player_number
        self.x = location[0]
        self.y = location[1]
        self.local = False

    def move(self):
        self.x += self.vel[0]
        self.y += self.vel[1]

    def move_to(self, destination):
        self.x = destination[0]
        self.y = destination[1]
    
    def current_pos(self):
        return (self.x, self.y)

    def next_pos(self):
        return (self.x + self.vel[0], self.y + self.vel[1])

    def serializable(self):
        return dict([('id', self.id), ('x', self.x), ('y', self.y)])

class LocalPlayer(Player):
    def __init__(self, number, location):
        Player.__init__(self, number, location)
        self.vel = (0, 0)
        self.local = True
        self.illegal_move = False
