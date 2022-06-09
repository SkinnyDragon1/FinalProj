import json

with open("map.json", "r") as f:
    json_list = json.loads(f.read())

for block in json_list:
    y1 = block[1]
    y2 = block[3]

    block[1] = y1 - 100
    block[3] = y2 - 100

with open("map.json", "w") as f:
    f.write(json.dumps(json_list))
