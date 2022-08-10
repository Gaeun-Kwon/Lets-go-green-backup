import PIL
from PIL import ImageDraw
from PIL import Image

import os
import datetime


uploaded_files= Image.open('C:/Users/ailee/Downloads/test/vegan/chip.JPG')

w,h = uploaded_files.size
print('height: ', h)
print('weight: ',w)
re_h = (600*h)/w
print('re_h: ',re_h)
uploaded_files = uploaded_files.resize((600,int(re_h)))

nowDate = datetime.datetime.now()
save_name = "assets/img/user/{}.jpg".format(nowDate.strftime("%Y%m%d%H%M"))
uploaded_files.save("static/"+save_name)

