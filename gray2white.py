from PIL import Image
import numpy

def is_grayscale(pixel):
    return (pixel[0] ==pixel[1] and pixel[1] == pixel[2])

def gray2white(filename):
    img = Image.open(filename).crop((1371, 1227, 1861, 1717))
    pixels = img.load()
    imgList = []
    for i in range(img.width):
        for j in range(img.height):
            if is_grayscale(pixels[i,j]):
                imgList.extend((255, 255, 255))
                img.putpixel((i,j),(255, 255, 255))
            else:
                imgList.extend(pixels[i,j])
    img.save('output.png')
    return imgList

if __name__ =='__main__':
    count = 0
    for i in gray2white('CV1.png'):
        if i != 255:
            count += 1
    print(count)
    print(count/3)


