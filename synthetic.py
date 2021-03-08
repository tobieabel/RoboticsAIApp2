import numpy as np
from PIL import Image
import xmltodict
from random import randint, randrange
import os
#import cv2 - this is causing an error on deployment, maybe something about the version
import copy
from urllib.request import urlopen


def show_image(jpg,xml):
    im = np.array(Image.open(urlopen(jpg)).convert('L'))#have to use urlopen to convert the string into a url
    new_img = Image.fromarray(np.uint8(im))
    new_img.show()
    im_xml = urlopen(xml)  # again, opening XML doc from url requires urlopen, not the normal open() function
    data_dict = xmltodict.parse(im_xml.read())



    return data_dict