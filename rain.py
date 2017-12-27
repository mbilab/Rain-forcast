import Image
import ImageDraw
import argparse
parser = argparse.ArgumentParser()
# YYYYmmdd
parser.add_argument("infom", help = "before,after,location (x,-y) ")
args = parser.parse_args()
info = args.infom.split(",")
before_filename = "image/CV1_3600_" + info[0] + ".png"
after_filename = "image/CV1_3600_" + info[1] + ".png"
position_x = int(info[2])
position_y = int(info[3])
radius = 150

def centroid(filename):
    image = Image.open(filename).crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
    width, height = image.size#xy
    pixels = image.load()
    count = 0
    x_pos = 0
    y_pos = 0
    for i in range(width):
        for j in range(height):# no black or white rgb(a,a,a)
            if (pixels[i, j][0] == pixels[i, j][1] and pixels[i, j][0] == pixels[i, j][2]) or pixels[i, j][0] <= 100:
                continue
            count += 1
            x_pos += i
            y_pos += j
    if count > 0:
        x_pos /= count
        y_pos /= count
    return [x_pos, y_pos] #centroid return centroid


#vector calculate
after = centroid(after_filename)
before = centroid(before_filename)
#may no rain
if after[0] == 0:
    print False
    print ":no rain in image after.Weather turns well"
elif before[0] == 0:#no rain at before image
    im_a = Image.open(after_filename) #cloud growing at mid
    pixels_a = im_a.load()
    if pixels_a[position_x, position_y][0] > 100:
        #make image and draw
        im = Image.open(after_filename)
        nim = im.crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
        draw = ImageDraw.Draw(nim)
        ###darw diamond shape
        draw.polygon([(radius - 25, radius), (radius, radius - 25), (radius + 25, radius), (radius, radius + 25)], (255, 0, 0), (255, 0, 0))
        del draw
        nim.save("pub/prediction_" + info[1] + ".png")
        print True
        print ":rains are growing above just now"
        print "Prediction save as:@prediction_" + info[1] + ".png@"
    else:
        #make image and print rain
        print False
        print ":rains are growing nearby just now."

else:
    vector = [after[0] - before[0], after[1] - before[1]]
    ###open image
    center = [radius, radius]
    im = Image.open(after_filename)
    nim = im.crop((position_x - radius, position_y - radius, position_x + radius, position_y + radius))
    pixels = nim.load()
    ###cloudy ?
    count_cloud = 0
    for i in range(300):
        for j in range(300):
            if pixels[i, j][0] > 80 and not(pixels[i, j][0] == pixels[i, j][1] and pixels[i, j][0] == pixels[i, j][2]):
                count_cloud += 1
    if count_cloud < 40000:
        x = center[0] - 2 * vector[0]
        y = center[1] - 2 * vector[1]
    else:
        x = center[0] + 2 * vector[0]
        y = center[1] + 2 * vector[1]
    ###Vector may out of range ,and it means rains are far away.\
    if x > 0 and y > 0:
        if pixels[x, y][0] > 100 and not(pixels[x, y][0] == pixels[x, y][1] and pixels[x, y][0] == pixels[x, y][2]):
            print True
            print ":rains are coming!"
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
            del draw
            nim.save("pub/prediction_" + info[1] + ".png")
            print " Prediction saves as:pub/@prediction_" + info[1] + ".png@"
        else :
            print False
# vi:et:ts=4:sw=4
