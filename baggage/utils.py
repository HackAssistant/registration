import math
import itertools
from baggage.models import Room, Bag, BAG_ADDED
from escpos.printer import Usb
from escpos.escpos import EscposIO
from django.contrib.staticfiles import finders
import time
import datetime


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


def print_receipt(hacker, email, building, position, obj_type, color, desc, bag_id, time_ins, message):
    try:
        sp = datetime.datetime.fromtimestamp(time.time()).strftime('%d/%m/%Y %H:%M:%S')
        si = datetime.datetime.fromtimestamp(time_ins).strftime('%d/%m/%Y %H:%M:%S')
        p = Usb(0x0416, 0x5011)
        p2 = EscposIO(p)
        p.text("\n")
        p.image(finders.find("img/printer/header.gif"))
        p.text("\n")
        p.text("\n")
        p.image(finders.find("img/printer/title.gif"))
        p.text("\n")
        p2.writelines("Printed on: " + str(sp), align='center', font='b')
        p.text("\n")
        p.text("\n")
        p2.writelines("Location", align='center', font='a', text_type='bold', width=1)
        p2.writelines(building + "-" + position, align='center', font='a', text_type='bold', width=2, height=2)
        p.text("\n")
        p.text("\n")
        p2.writelines("Name: " + hacker, align='center', font='a', text_type='bold')
        p2.writelines("Email: " + email, align='center', font='a', text_type='bold')
        if obj_type:
            p2.writelines("Type: " + obj_type, align='center', font='a', text_type='bold')
        if color:
            p2.writelines("Color: " + color, align='center', font='a', text_type='bold')
        p.text("\n")
        p.text("\n")
        p2.writelines("Time: " + str(si), align='center', font='a')
        p.text("\n")
        p.text("\n")
        p.image(finders.find("img/printer/footer.gif"))
        p.cut()
    except:
        return 'Error! Couldn\'t print the receipt!'
    return 'Printing receipt...'
