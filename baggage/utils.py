import math
import itertools
from baggage.models import Room, Bag, BAG_ADDED


def calculate_distance(name, ini_x, ini_y, end_x, end_y):
    return ((name, end_x, end_y), math.sqrt(pow(abs(end_x - ini_x), 2) + pow(abs(end_y - ini_y), 2)))


def nearest_available(x, y):
    return ''


def get_positions(size_x, size_y, door_x, door_y):
    return list(itertools.product(list(map(str, range(0, size_x))), list(map(str, range(0, size_y)))))


def get_positions_dist(size_x, size_y, door_x, door_y, name):
    positions = get_positions(size_x, size_y, door_x, door_y)
    return list(map(lambda x: calculate_distance(name, door_x, door_y, int(x[0]), int(x[1])), positions))


def get_all_positions(rooms):
    return dict(map(lambda room: (room.room, get_positions(room.row, room.col, room.door_row, room.door_col)), rooms))


def get_position(special):
    extra = 'SPECIAL'
    if not special:
        rooms = Room.objects.all()
        positions = []
        for room in rooms:
            positions.extend(get_positions_dist(room.row, room.col, room.door_row, room.door_col, room.room))
        positions_sort = sorted(positions, key=(lambda x: x[1]))
        i = 0
        while i < len(positions_sort):
            # I am not responsible for what will happen if you add more than 26 rows ;)
            row_char = chr(positions_sort[i][0][1] + 65)
            num_bags = Bag.objects.filter(status=BAG_ADDED, room=positions_sort[i][0][0],
                                          row=row_char, col=positions_sort[i][0][2]).count()
            if num_bags == 0:
                return (1, positions_sort[i][0][0], row_char, positions_sort[i][0][2])
            i += 1
        extra = 'EXTRA'
    i = 0
    while i < 10000:
        num_bags = Bag.objects.filter(status=BAG_ADDED, room=extra, row=0, col=i).count()
        if num_bags == 0:
            return (2, extra, 'EXTRA', i)
        i += 1
    return (0, '', 'ERROR', 0)
