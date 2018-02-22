#!/usr/bin/env python3

import argparse
import json
import math
from PIL import Image, ImageDraw, ImageFont

with open('config.json', 'r') as data_file:
    config = json.load(data_file)

# constant setup
arrow_path = './image/arrow.png'
character_path = './image/character.png'
font_path = './zh.ttf'
output_path = config['path_save']

def arrow_angle(wd): # {{{ wd: wind direction
    if 0 == wd[0]:
        if wd[1] > 0:
            return -math.pi / 2
        elif 0 == wd[1]:
            return -1
        else:
            return math.pi / 2
    elif wd[0] > 0 :
        return math.atan(-wd[1] / wd[0])
    else:
        return math.atan(-wd[1] / wd[0]) + math.pi
# }}}

def arrow_positoin(image, angle): # 修改時注意有座標轉換議題
    x = image.size[0] / 2
    y = image.size[1] / 2
    return int(x - 80 * math.cos(angle) - 50), int(y + 80 * math.sin(angle) - 50)

def centroid(image): # {{{
    count = 0; x = 0; y= 0
    pixels = image.load()

    for j in range(image.size[1]):
        for i in range(image.size[0]):
            weight = color_weight(pixels[i, j])
            count += weight
            x += weight * i
            y += weight * j

    if count > 0:
        x /= count
        y /= count

    return x, y
# }}}

def color_weight(color): # {{{
    if is_grayscale(color): return 0 # 背景或格線
    if color[0] < 100 and color[2] > 200: return 0 # blue

    if color[0] < 10 and color[2] < 10:
        if color[1] <= 150: return 0.9 # dark green (毛毛雨)
        if color[1] <= 200: return 0.5 # green (多雲)
        if color[1] > 200: return 0 # light green(一點雲)

    return 1
# }}}

def draw(last_image, wd, path): # {{{ wd: window direction
    #! since there are so many constants, do we need character_path, character_size... ?
    character = Image.open(character_path).resize((53, 86))
    font = ImageFont.truetype(font_path, 30)
    last_image.paste(character, (123, 90), mask=character)
    image = Image.new('RGB', (400, 400), (50, 130, 230))
    angle = arrow_angle(wd)
    if angle >= 0:
        ImageDraw.Draw(image).text((30, 335), '雲飄來了，要下雨了喔~', font=font)
        arrow = Image.open(arrow_path).resize((100, 100)).rotate(-90).rotate(math.degrees(angle))
        last_image.paste(arrow, arrow_positoin(last_image, angle), mask=arrow)
    else: # new rain: rain in the last image without wind
        ImageDraw.Draw(image).text((30, 335), '雲系發展中，要下雨了喔~', font=font)
    image.paste(last_image, (50, 20))
    image.save(path, format='png')
# }}}

def is_grayscale(color):
    return color[0] == color[1] and color[0] == color[2]

def rain_at(image, x, y, radius=20): # {{{
    if 0 > x or x > image.size[0] or 0 > y or y > image.size[1]:
        return False # (x, y) doesn't locate in image, i.e. wind is too strong to predict

    count = 0
    pixels = image.load()
    radius_square = radius * radius

    for j in range(image.size[1]):
        for i in range(image.size[0]):
            if (x - i) ** 2 + (y - j) ** 2 > radius_square: continue
            if color_weight(pixels[i, j]):
                count += 1
    # True if more than 50% nearby pixels is raining
    return count > 0.5 * math.pi * radius_square
# }}}

def wind_direction(centroids, image): # {{{
    if (0, 0) == centroids[-2]: # new rain in the last image (rain in images[-1] but not in images[-2])
        return 0, 0 # the wind direction is (0, 0)

    #! TODO: improve logic
    count = 0
    pixels = image.load()
    for j in range(image.size[1]):
        for i in range(image.size[0]):
            if pixels[i, j][0] > 80 and not is_grayscale(pixels[i, j]):
                count += 1
    if count > 70000:
        return centroids[-2][0] - centroids[-1][0], centroids[-2][1] - centroids[-1][1]

    return centroids[-1][0] - centroids[-2][0], centroids[-1][1] - centroids[-2][1]
# }}}

if '__main__' == __name__:

    parser = argparse.ArgumentParser()

    parser.add_argument('images', help='image filenames in YYYYmmDDHHMM format', nargs='*')
    parser.add_argument('-d', default=10, dest='duration', help='duration from the last image to prediction (default: 10, unit: minute)', type=float)
    parser.add_argument('-r', default=150, dest='radius', help='radius on the rader graph of CWB (default: 150)', type=int)
    parser.add_argument('-x', default=1675, help='x on the rader graph of CWB, NCKU is at (1675, 1475)', type=int)
    parser.add_argument('-y', default=1475, help='y on the rader graph of CWB, NCKU is at (1675, 1475)', type=int)
    args = parser.parse_args()

    if len(args.images) < 2:
        print('please specify at least 2 images')
        exit()

    area = (args.x - args.radius, args.y - args.radius, args.x + args.radius, args.y + args.radius)
    images = [Image.open('image/CV1_3600_%s.png' % v).crop(area) for v in args.images]
    centroids = [centroid(v) for v in images]

    if [0, 0] == centroids[-1]:
        print(False) # no rain in images[-1]
    else:
        wd = wind_direction(centroids, images[-1])
        # (args.radius, args.radius) is the center of images[-1]
        # (args.radius - wd[0], args.radius - wd[1]) will be the center 10 minutes later
        center = [args.radius - v * args.duration / 10 for v in wd]
        if rain_at(images[-1], *center):
            # (args.x, args.y) will rain in 10 minutes
            print(True)
            draw(images[-1], wd, '%s/prediction_%s.png' % (output_path, args.images[1]))
        else:
            print(False)
