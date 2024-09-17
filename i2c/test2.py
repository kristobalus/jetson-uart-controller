
# i2c_address = int(10)
# print(i2c_address)

distance_max = 100
distance_min = 0


def normalize(value, min_value, max_value):
    value = min(max_value, value)
    return 1 - (value - min_value) / (max_value - min_value)


distance = 0
print(normalize(distance, distance_min, distance_max))

