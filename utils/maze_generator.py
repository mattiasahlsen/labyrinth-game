import json
bit_array = []
width = 80
max_players = 4
starting_locations = [
    (40, 1),
    (79, 40),
    (40, 79),
    (1, 40)
]

for y in range(width):
    for x in range(width):
        if y == 38 or y == 43:
            if x < 38 or x > 43:
                bit_array.append(1)
            else: bit_array.append(0)
        elif x == 38 or x == 43:
            if y < 38 or y > 43:
                bit_array.append(1)
            else: bit_array.append(0)
        else:
            bit_array.append(0)

f = open('maze.txt', 'w')

data = dict([('width', width), 
    ('max_players', max_players),
    ('starting_locations', starting_locations), 
    ('bit_array', bit_array)])

json.dump(data, f)