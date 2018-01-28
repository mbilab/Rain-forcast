from PIL import Image,ImageDraw,ImageFont
import argparse
import math 
# constant setup
radius = 150
character_height = ( 53 , 86 )
character_position = ( 123 , 90 )
bg_color = ( 50 , 130 , 230 )
character = "image/character.png"
arrow = "image/arrow.png"

def arrow_angle(vector):#正負部分為影像坐標與常用數學座標轉換
    if vector[0]==0 :
        if vector[1]>0:
            return -math.pi / 2
        else:
            return math.pi / 2
    elif vector[0] > 0 :
        return math.atan( -vector[1]/vector[0] )
    else:
        return math.atan( -vector[1]/vector[0] ) + math.pi

def arrow_positoin(angle):#修改時注意有座標轉換議題
    return [ int( 150 - 100 * math.cos(angle) - 50 ),int( 150 + 100 * math.sin(angle) - 50 )]

def is_grid_line_or_bg(px):
    return px[0] == px[1] and px[0] == px[2]

def centroid(filename, position_x, position_y):
    image = Image.open(filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
    width, height = image.size#xy
    pixels = image.load()
    count = 0
    x_pos = 0
    y_pos = 0

    # calculate centroid
    for i in range(width):
        for j in range(height):

            # ignore rgb(a,a,a) or which r < threshold
            if is_grid_line_or_bg(pixels[i, j]) or pixels[i, j][0] <= 100:
                continue

            count += 1
            x_pos += i
            y_pos += j

    if count > 0:
        x_pos /= count
        y_pos /= count

    return [x_pos, y_pos]

def rain_area(pixels, x, y):##True: in distance<35 80% spot >100
    area_radius = 25
    count = 0
    for i in range(300):
        for j in range(300):
            if math.sqrt((x - i) ** 2 + (y - j) ** 2) < area_radius and pixels[i, j][0] > 100 and not is_grid_line_or_bg(pixels[i, j]):
                count += 1
    if count > 0.6 * math.pi * area_radius ** 2:
        return True
    else:
        return False


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("info1", help ="info1:datetime of before image(YYYYmmDDHHMM),")
    parser.add_argument("info2", help ="info2:datetime of after image(YYYYmmDDHHMM),")
    parser.add_argument("info3", help ="info3:location x on rader graph of CWB (NCKU is at 1675,1475)")
    parser.add_argument("info4", help ="info4:location -y on rader graph of CWB (NCKU is at 1675,1475)")
    args = parser.parse_args()

    before_filename = "image/CV1_3600_" + args.info1 + ".png"
    after_filename  = "image/CV1_3600_" + args.info2 + ".png"
    position_x = int(args.info3)
    position_y = int(args.info4)

    before  = centroid( before_filename, position_x, position_y)
    after = centroid( after_filename, position_x, position_y)


    #may no rain
    if after[0] == 0:
        print(False)
        print(":no rain in image after.Weather turns well")

    elif before[0] == 0: #no rain at before image #cloud growing at mid
        nim = Image.open(after_filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
        pixels = nim.load()
        if rain_area(pixels,150,150):
            #make image and draw

            ###draw 
            base_im = Image.open(after_filename,'r').crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
            character_im = Image.open(character,'r').resize( character_height )
            base_im.paste(character_im, character_position ,mask = character_im)
            bg = Image.new( "RGB", (400,400) ,bg_color)
            fnt = ImageFont.truetype('zh.ttf', 30)
            ImageDraw.Draw( bg ).text( (30,335), "雲系發展中，要下雨了喔~", font=fnt )
            bg.paste(base_im,(50,20))
            bg.save("pub/prediction_" + args.info2 + ".png", format = "png")

            print (True)
            print (":rains are growing above just now")
            print ("Prediction save as:@prediction_" + args.info2 + ".png@")
            print ("centroid of before image:",before)
            print ("centroid of after image :", after)
        else:
            #make image and print rain
            print (False)
            print (":rains are growing nearby just now.")
            print ("centroid of before image:",before)
            print ("centroid of after image :", after)

    else:
        vector = [after[0] - before[0], after[1] - before[1]]
        ###cloudy ?
        center = [radius, radius]
        nim = Image.open(after_filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
        pixels = nim.load()
        count_cloud = 0
        for i in range(radius * 2):
            for j in range(radius * 2):
                if pixels[i, j][0] > 80 and not(pixels[i, j][0] == pixels[i, j][1] and pixels[i, j][0] == pixels[i, j][2]):
                    count_cloud += 1
        if count_cloud > 40000:
            vector =[- vector[0],-vector[1]]

        ###find cloud
        x = center[0] - 2 * vector[0]
        y = center[1] - 2 * vector[1]

        ### Vector may out of range ,and it means rains are far away.
        if 0 <= x and x <300 and  0 <=  y and y < 300:
            if  rain_area(pixels,x,y):
                print (True)
                print (":rains are coming!")
                print ("Prediction save as:@prediction_" + args.info2 + ".png@")
                print ("centroid of before image:",before)
                print ("centroid of after image :", after)

                #draw
                angle = arrow_angle(vector) 
                fnt = ImageFont.truetype('zh.ttf', 30)
                bg = Image.new( "RGB", (400,400) ,bg_color)
                ImageDraw.Draw( bg ).text( (30,335), "雲飄來了，要下雨了喔~", font=fnt )
                base_im = Image.open(after_filename,'r').crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
                character_im = Image.open(character,'r').resize( character_height )
                arrow_im = Image.open(arrow,'r').resize((100,100) ).rotate(-90).rotate(math.degrees(angle))
                base_im.paste(arrow_im, arrow_positoin(angle) , mask = arrow_im)
                base_im.paste(character_im, character_position , mask = character_im)
                bg.paste(base_im,(50,20))
                bg.save("pub/prediction_" + args.info2 + ".png", format = "png")

            else :
                print (False)
                print ("centroid of before image:",before)
                print ("centroid of after image :", after)
        else:
            print (False)
            print ("centroid of before image:",before)
            print ("centroid of after image :", after)
# vi:et:ts=4:sw=4
