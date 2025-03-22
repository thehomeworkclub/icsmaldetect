import json
import random
import decimal


normal_data = 5
all_data = []

for i in range(10000):
    adjusted_data = normal_data + float(decimal.Decimal(random.randrange(-100, 100))/100)
    is_normal = True
    if random.randint(1, 10) == 10:
        if random.randint(1, 2) == 1:
            adjusted_data = normal_data + float(decimal.Decimal(random.randrange(100, 300))/100)
        else:
            adjusted_data = normal_data + float(decimal.Decimal(random.randrange(-300, -100))/100)
        is_normal = False
    all_data.append(json.dumps({
        'data': adjusted_data,
        'is_normal': 1 if is_normal else 0
    }))

with open('data.json', 'w') as f:
    f.write('\n'.join(all_data))
