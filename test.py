from PIL import Image,ImageDraw,ImageFont
from datetime import timedelta,datetime
from rain import centroid
import argparse
import json
if __name__ == '__main__':
    with open('config.json', 'r') as data_file:
        config = json.load(data_file)
    radius = 150
    parser = argparse.ArgumentParser()
    parser.add_argument("bigin", help ="info1:datetime of bigin image(YYYYmmDDHHMM),")
    parser.add_argument("end", help ="info2:datetime of end image(YYYYmmDDHHMM),")
    parser.add_argument("x", help ="info3:location x on rader graph of CWB (NCKU is at 1675,1475)")
    parser.add_argument("y", help ="info4:location -y on rader graph of CWB (NCKU is at 1675,1475)")
    args = parser.parse_args()
    x=int(args.x)
    y=int(args.y)
    
    begin = datetime.strptime(args.bigin, "%Y%m%d%H%M")
    end = datetime.strptime(args.end, "%Y%m%d%H%M")
    _10mins = timedelta(seconds=600)
    file_datetime = begin 
    
    fnt = ImageFont.truetype('zh.ttf', 10)
    font_color = 250
    base = config['path']+ end.strftime("%Y%m%d%H%M") + ".png"
    base_im = Image.open(base).crop((x - radius, y - radius, x + radius, y + radius))
    
    while (file_datetime < end) :
        stamp =  file_datetime.strftime("%Y%m%d%H%M")
        filename = config['path']+ stamp + ".png"
        centr =centroid ( filename , x , y  )
        if centr[0] != 0 :
            ImageDraw.Draw( base_im ).text( (centr[0]-3,centr[1]- 5 ),'@'+stamp, font=fnt ,fill = (font_color ,0 , 0 ) )
        if font_color > 0:
            font_color -= 10
        file_datetime = file_datetime +_10mins
        base_im.save('pub/'+end.strftime("%Y%m%d%H%M")+'.png')
    print (config['path_save']+'pub/'+end.strftime("%Y%m%d%H%M")+'.png')







