#!/usr/bin/env python3

from PIL import Image,ImageDraw,ImageFont
import argparse
import math
import json

with open('config.json', 'r') as data_file:
    config = json.load(data_file)

# constant setup
radius = 150
character_size = (53, 86)
character_position = (123, 90)
bg_color = (50, 130, 230)
character = "image/character.png"
arrow = "image/arrow.png"

def arrow_angle(vector):
    if vector[0] == 0 :
        if vector[1] > 0:
            return -math.pi / 2
        elif vector[1] == 0:
            return -1
        else:
            return math.pi / 2
    elif vector[0] > 0 :
        return math.atan(-vector[1] / vector[0])
    else:
        return math.atan(-vector[1] / vector[0]) + math.pi

def arrow_positoin(angle): # 修改時注意有座標轉換議題
    return [int(radius - 80 * math.cos(angle) - 50), int(radius + 80 * math.sin(angle) - 50)]

def centroid(filename, position_x, position_y):
    image = Image.open(filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
    width, height = image.size#xy
    pixels = image.load()
    count = 0
    x = 0
    y = 0

    # calculate centroid
    for i in range(width):
        for j in range(height):
            weight = color_weight(pixels[i, j])
            count += weight
            x += weight * i
            y += weight * j


    if count > 0:
        x /= count
        y /= count
    return x, y

def color_weight(color):
    # 背景或格線: 0
    if is_grayscale(color): return 0

    # 毛毛雨: 0.9
    if color[0] < 10 and color[1] <= 150 and color[0] < 10: #! what color?
        return 0.9

    # 多雲: 0.5
    if color[0] < 10 and color[1] <= 200 and color[0] < 10: #! what color?
        return 0.5

    #if pixels[0] > 100:
    return 1 #! check the logic

def is_grayscale(color):
    return color[0] == color[1] and color[0] == color[2]

def rain_dot(pixels,i,j):
    if pixels[i,j][0] > 150 or (pixels[i,j][0] < 10 and pixels[i,j][1] < 180 and pixels[i,j][2] < 10 ):
        return True
    return False

def rain_area(pixels, x, y):#True: In distance<35 ,more than 50% of pixels are raining.
    area_radius = 20
    count = 0
    if 0 > x or x > 300 or  0 >  y or y > 300: #x,y doesn't locate in image
        return False

    for i in range(300):
        for j in range(300):
            if math.sqrt((x - i) ** 2 + (y - j) ** 2) < area_radius and rain_dot(pixels,i,j) and not is_grayscale(pixels[i, j]):
                count += 1

    if count > 0.5 * math.pi * area_radius ** 2:
        return True
    else:
        return False

def moving_direction(pixels, after, before):
    if before == [0, 0]:#剛發展的雲 為0向量
        return before
    else:
        #!TODO: improve precision
        count_cloud = 0
        for i in range(radius * 2):
            for j in range(radius * 2):
                if pixels[i, j][0] > 80 and not is_grayscale(pixels[i, j]):
                    count_cloud += 1
        if count_cloud > 70000:
            return [before[0] - after[0], before[1] - after[1]]
        else:
            return [after[0] - before[0], after[1] - before[1]]

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('images', help='image filenames in YYYYmmDDHHMM format', nargs='*')
    parser.add_argument('-x', default=1675, help='x on the rader graph of CWB, NCKU is at (1675, 1475)')
    parser.add_argument('-y', default=1475, help='y on the rader graph of CWB, NCKU is at (1675, 1475)')
    args = parser.parse_args()

    before_filename = "image/CV1_3600_" + args.images[0] + ".png"
    after_filename  = "image/CV1_3600_" + args.images[1] + ".png"
    position_x = int(args.x)
    position_y = int(args.y)

    before = centroid(before_filename, position_x, position_y)
    after = centroid(after_filename, position_x, position_y)

    #may no rain
    if after[0] == 0:
        print(False) #no rain in image after

    else: #crop image in size of 300 px*300 px ,calculate simply
        base_im = Image.open(after_filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
        pixels = base_im.load() #calculate in pixels

        vector = moving_direction(pixels, after, before)
        #pixels[x,y] will come to center 10 minutes later
        x = radius - 2 * vector[0]
        y = radius - 2 * vector[1]

        if rain_area(pixels, x, y): #if pixels(x,y) locates in a area being raining, center will rain in 10 minutes.
            print (True)

            #draw image for user
            fnt = ImageFont.truetype('zh.ttf', 30)
            character_im = Image.open(character).resize(character_size)
            base_im.paste(character_im, character_position , mask = character_im)
            bg = Image.new("RGB", (400, 400), bg_color)
            angle = arrow_angle(vector)
            if angle >= 0:
                ImageDraw.Draw(bg).text((30,335), "雲飄來了，要下雨了喔~", font = fnt)
                arrow_im = Image.open(arrow).resize((100,100)).rotate(-90).rotate(math.degrees(angle))
                base_im.paste(arrow_im, arrow_positoin(angle), mask = arrow_im)
            else :#剛發展的雲
                ImageDraw.Draw(bg).text((30,335), "雲系發展中，要下雨了喔~", font = fnt)
            bg.paste(base_im, (50, 20))
            bg.save("pub/prediction_" + args.images[1] + ".png", format = "png")

        else :
            print (False)
