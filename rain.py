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
        elif vector[1]==0:
            return -1
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

def rain_dot(pixels,i,j):
    if pixels[i,j][0]>150 or (pixels[i,j][0] <10 and pixels[i,j][1]<180 and pixels[i,j][2]<10 ):
        return True

def rain_area(pixels, x, y):##True: in distance<35 80% spot >100
    area_radius = 20
    count = 0
    if 0 > x or x > 300 or  0 >  y or y > 301:
        return False
    for i in range(300):
        for j in range(300):
            if math.sqrt((x - i) ** 2 + (y - j) ** 2) < area_radius and rain_dot(pixels,i,j) and not is_grid_line_or_bg(pixels[i, j]):
                count += 1
    if count > 0.5 * math.pi * area_radius ** 2:
        return True
    else:
        return False

def Vector(pixels,after,before):
    if(before==[0,0]):
        return before
    else:
        count_cloud = 0
        for i in range(radius * 2):
            for j in range(radius * 2):
                if pixels[i, j][0] > 80 and not(pixels[i, j][0] == pixels[i, j][1] and pixels[i, j][0] == pixels[i, j][2]):
                    count_cloud += 1
        if count_cloud > 40000:
            return [befor[0] - after[0], before[1] - after[1]]
        else:
            return [after[0] - before[0], after[1] - before[1]]

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("brgin", help ="info1:datetime of before image(YYYYmmDDHHMM),")
    parser.add_argument("end", help ="info2:datetime of after image(YYYYmmDDHHMM),")
    parser.add_argument("x", help ="info3:location x on rader graph of CWB (NCKU is at 1675,1475)")
    parser.add_argument("y", help ="info4:location -y on rader graph of CWB (NCKU is at 1675,1475)")
    args = parser.parse_args()

    before_filename = "image/CV1_3600_" + args.brgin + ".png"
    after_filename  = "image/CV1_3600_" + args.end + ".png"
    position_x = int(args.x)
    position_y = int(args.y)

    before  = centroid( before_filename, position_x, position_y)
    after = centroid( after_filename, position_x, position_y)


    #may no rain
    if after[0] == 0:
        print(False) #no rain in image after



    else:
        base_im = Image.open(after_filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
        pixels = base_im.load()

        vector=Vector(pixels,after, before)
        ###find cloud
        x = radius - 2 * vector[0]
        y = radius - 2 * vector[1]

        ### Vector may out of range ,and it means rains are far away.
        if rain_area(pixels,x,y):
            print (True)
            print ("centroid of before image:",before)
            print ("centroid of after image :", after)
     
            #draw
            fnt = ImageFont.truetype('zh.ttf', 30)
            bg = Image.new( "RGB", (400,400) ,bg_color)
            character_im = Image.open(character).resize( character_height )
            base_im.paste(character_im, character_position , mask = character_im)
            angle = arrow_angle(vector) 
            if angle>=0:
                ImageDraw.Draw( bg ).text( (30,335), "雲飄來了，要下雨了喔~", font=fnt )
                arrow_im = Image.open(arrow).resize((100,100) ).rotate(-90).rotate(math.degrees(angle))
                base_im.paste(arrow_im, arrow_positoin(angle) , mask = arrow_im)
            else :
                ###draw 
                ImageDraw.Draw( bg ).text( (30,335), "雲系發展中，要下雨了喔~", font=fnt )
            bg.paste(base_im,(50,20))
            bg.save("pub/prediction_" + args.end + ".png", format = "png")
     
     
        else :
            print (False)
            print ("centroid of before image:",before)
            print ("centroid of after image :", after)
# vi:et:ts=4:sw=4
