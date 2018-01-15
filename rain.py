import Image
import ImageDraw
import argparse
import math 
# constant setup
radius = 150

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

    # FIXME: Need a more detail description(fixed)
    parser.add_argument("infom", help =
        "Please keyin 4 parses as follow format, par1,par2,par3,par4."
        "par1:datetime of before image(YYYYmmDDHHMM),"
        "par2:datetime of after image(YYYYmmDDHHMM),"
        "par3,par4:location (x,-y) on rader graph of CWB (NCKU is at 1675,1475)"
    )
    args = parser.parse_args()
    info = args.infom.split(",")

    before_filename = "image/CV1_3600_" + info[0] + ".png"
    after_filename  = "image/CV1_3600_" + info[1] + ".png"
    position_x = int(info[2])
    position_y = int(info[3])

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
            draw = ImageDraw.Draw(nim)

            ###darw diamond shape
            draw.polygon( \
                [ \
                    (radius - 25, radius), \
                    (radius, radius - 25), \
                    (radius + 25, radius), \
                    (radius, radius + 25) \
                ], \
                (255, 0, 0), \
                (255, 0, 0) \
            )

            nim.save("pub/prediction_" + info[1] + ".png")
            print (True)
            print (":rains are growing above just now")
            print ("Prediction save as:@prediction_" + info[1] + ".png@")
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

        ###open image
        center = [radius, radius]
        nim = Image.open(after_filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
        pixels = nim.load()

        ###cloudy ?
        count_cloud = 0
        for i in range(radius * 2):
            for j in range(radius * 2):
                if pixels[i, j][0] > 80 and not(pixels[i, j][0] == pixels[i, j][1] and pixels[i, j][0] == pixels[i, j][2]):
                    count_cloud += 1

        if count_cloud < 40000:
            x = center[0] - 2 * vector[0]
            y = center[1] - 2 * vector[1]
        else:
            x = center[0] + 2 * vector[0]
            y = center[1] + 2 * vector[1]

        ### Vector may out of range ,and it means rains are far away.
        if 0 <= x and x <300 and  0 <=  y and y < 300:
            if  rain_area(pixels,x,y):
                print (True)
                print (":rains are coming!")
                print ("centroid of before image:",before)
                print ("centroid of after image :", after)

                #make image
                arrow = (center[0], center[1])
                root = (center[0] - 2 * vector[0], center[1] - 2 * vector[1])
                cen = [center[0] - 2 * vector[0] / 4, center[1] - 2 * vector[1] / 4]
                cen1 = (cen[0] + 2 * vector[1] / 8, cen[1] - 2 * vector[0] / 8)
                cen2 = (cen[0] - 2 * vector[1] / 8, cen[1] + 2 * vector[0] / 8)
                arrow1 = (cen[0] + 2 * vector[1] / 4, cen[1] - 2 * vector[0] / 4)
                arrow2 = (cen[0] - 2 * vector[1] / 4, cen[1] + 2 * vector[0] / 4)

                ###draw
                draw = ImageDraw.Draw(nim)
                draw.polygon([arrow, arrow1, cen1, root, cen2, arrow2], (0, 0, 0), (0, 0, 0))
                nim.save("pub/prediction_" + info[1] + ".png")
                print (" Prediction saves as:pub/@prediction_" + info[1] + ".png@")

            else :
                print (False)
                print ("centroid of before image:",before)
                print ("centroid of after image :", after)
        else:
            print (False)
            print ("centroid of before image:",before)
            print ("centroid of after image :", after)
# vi:et:ts=4:sw=4
