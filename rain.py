import Image
import ImageDraw
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("infom", help="before,after,location (x,-y) ")
args = parser.parse_args()
info=args.infom.split(",")
before_filename="image/CV1_3600_"+info[0]+".png"
after_filename="image/CV1_3600_"+info[1]+".png"
position_x=int(info[2])
position_y=int(info[3])

def centroid(filename):
    im=Image.open(filename)
    nim=im.crop((position_x-150,position_y-150,position_x+150,position_y+150))
    col,row = nim.size#xy
    data=[]#r,g,b,j,i
    pixels=nim.load()
    for i in range(row):
        for j in range(col):# no black or white rgb(a,a,a)
            if not(pixels[j,i][0]==pixels[j,i][1] and pixels[j,i][0]==pixels[j,i][2]):
                data.append(pixels[j,i]+(j,i)) #pixels[x,y]  #data r,g,b,j,i
    x_count=0
    x_total=0
    y_count=0
    y_total=0
    for i in range(len(data)):
        if data[i][0]>100:
            x_count+=1
            y_count+=1
            x_total+=data[i][3]
            y_total+=data[i][4]
    if x_count!=0 and y_count!=0:
        x_position=x_total/x_count
        y_position=y_total/y_count
        return [x_position,y_position] #centroid return centroid
    else:#if no rain  centroid false
        return False


#vector calculate
after=centroid(after_filename)
before=centroid(before_filename)
#may no rain
if after==False:
    rain = False
    #make image and print rain
    #im=Image.open(after_filename)
    #nim=im.crop((position_x-150,position_y-150,position_x+150,position_y+150))
    #draw=ImageDraw.Draw(nim)
    ###darw diamond shape
    #draw.polygon([(125,150),(150,125),(175,150),(150,175)],(255,255,255),(255,0,0))
    #del draw
    #nim.save("prediction1_"+info[1]+".png")
    print rain
    print ":no rain in image after.Weather turns well"
elif before == False:#no rain at before image
    im_a=Image.open(after_filename) #cloud growing at mid
    pixels_a=im_a.load()
    if pixels_a[position_x,position_y][0]>100:
        rain = True
        #make image and draw
        im=Image.open(after_filename)
        nim=im.crop((position_x-150,position_y-150,position_x+150,position_y+150))
        draw=ImageDraw.Draw(nim)
        ###darw diamond shape
        draw.polygon([(125,150),(150,125),(175,150),(150,175)],(255,0,0),(255,0,0))
        del draw
        nim.save("pub/prediction_"+info[1]+".png")
        print rain
        print ":rains are growing above just now"
        print "Prediction save as:@prediction_"+info[1]+".png@"
    else:
        rain = False
        #make image and print rain
        #im=Image.open(after_filename)
        #nim=im.crop((position_x-150,position_y-150,position_x+150,position_y+150))
        #nim.save("prediction1_"+info[1]+".png")
        print rain
        print ":rains are growing nearby just now."

else:
    vector=[(after[0]-before[0]),(after[1]-before[1])]
    ###open image
    location=[150,150]
    im=Image.open(after_filename)
    nim=im.crop((position_x-150,position_y-150,position_x+150,position_y+150))
    pixels=nim.load()
    ###cloudy ?
    count_cloud=0
    for i in range(300):
        for j in range(300):
            if pixels[j,i][0]>80 and not(pixels[j,i][0]==pixels[j,i][1] and pixels[j,i][0]==pixels[j,i][2]):
                count_cloud += 1
    if count_cloud < 40000:
        x=location[0]-2*vector[0]
        y=location[1]-2*vector[1]
    else:
        x=location[0]+2*vector[0]
        y=location[1]+2*vector[1]
    ###judgemanet
    rain = False
    ###Vector may out of range ,and it means rains are far away.\
    if x>0 and y>0:
        if pixels[x,y][0]>100 and not(
            pixels[x,y][0]==pixels[x,y][1] and pixels[x,y][0]==pixels[x,y][2]):
            rain=True
        #print
        if (rain):
            print rain
            print ":rains are coming!"
            #make image
            arrow=(location[0],location[1])
            root=(location[0]-2*vector[0],location[1]-2*vector[1])
            cen=[location[0]-2*vector[0]/4,location[1]-2*vector[1]/4]
            cen1=(cen[0]+2*vector[1]/8,cen[1]-2*vector[0]/8)
            cen2=(cen[0]-2*vector[1]/8,cen[1]+2*vector[0]/8)
            arrow1=(cen[0]+2*vector[1]/4,cen[1]-2*vector[0]/4)
            arrow2=(cen[0]-2*vector[1]/4,cen[1]+2*vector[0]/4)
            ###draw
            draw=ImageDraw.Draw(nim)
            draw.polygon([arrow,arrow1,cen1,root,cen2,arrow2],(0,0,0),(0,0,0))
            del draw
            nim.save("pub/prediction_"+info[1]+".png")
            print " Prediction saves as:pub/@prediction_"+info[1]+".png@"
        else :
            print False
"""
  arrow=(location[0],location[1])
  root=(location[0]-2*vector[0],location[1]-2*vector[1])
  cen=[location[0]-2*vector[0]/4,location[1]-2*vector[1]/4]
  cen1=(cen[0]+2*vector[1]/8,cen[1]-2*vector[0]/8)
  cen2=(cen[0]-2*vector[1]/8,cen[1]+2*vector[0]/8)
  arrow1=(cen[0]+2*vector[1]/4,cen[1]-2*vector[0]/4)
  arrow2=(cen[0]-2*vector[1]/4,cen[1]+2*vector[0]/4)
  ###draw
  draw=ImageDraw.Draw(nim)
  draw.polygon([arrow,arrow1,cen1,root,cen2,arrow2],(0,0,0),(0,0,0))
  del draw
  nim.save("image/prediction_"+info[1]+".png")
  print " Prediction saves as:image/prediction_"+info[1]+".png"
  """
# vi:et:ts=4:sw=4
