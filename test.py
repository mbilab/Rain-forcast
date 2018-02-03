from PIL import Image,ImageDraw,ImageFont
from datetime import timedelta,datetime
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("bigin", help ="info1:datetime of bigin image(YYYYmmDDHHMM),")
    parser.add_argument("end", help ="info2:datetime of end image(YYYYmmDDHHMM),")
    parser.add_argument("x", help ="info3:location x on rader graph of CWB (NCKU is at 1675,1475)")
    parser.add_argument("y", help ="info4:location -y on rader graph of CWB (NCKU is at 1675,1475)")
    args = parser.parse_args()

    begin = datetime.strptime(args.bigin, "%Y%m%d%H%M")
    end = datetime.strptime(args.end, "%Y%m%d%H%M")
    _10mins = timedelta(seconds=600)

    file1_time = begin
    file2_time = begin + _10mins

    while (file1_time < end) :
        file1 = file1_time.strftime("%Y%m%d%H%M")
        file2 = file2_time.strftime("%Y%m%d%H%M")
        cmd ="python3 rain.py "+file1+" "+file2 +" "+args.x+" "+args.y +" --test"
        os.system(cmd)
        file1_time = file1_time +_10mins
        file2_time = file2_time +_10mins

