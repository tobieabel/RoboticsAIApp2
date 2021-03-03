import numpy as np
from PIL import Image
import xmltodict
from random import randint, randrange
import os
import cv2
import copy
from urllib.request import urlopen


def show_image(jpg):
    im = np.array(Image.open(urlopen(jpg)).convert('L'))#have to use urlopen to convert the string into a url
    new_img = Image.fromarray(np.uint8(im))
    new_img.show()

    return 'Image converted to Greyscale'