import json
bit_array = []
width = 80

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

data = (width, bit_array)
json.dump(data, f)