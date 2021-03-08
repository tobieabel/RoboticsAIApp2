import numpy as np
from PIL import Image
import xmltodict
from random import randint, randrange
import os
#import cv2 - this is causing an error on deployment, maybe something about the version
import copy
from urllib.request import urlopen


def show_image(jpg,xml):
    im = np.array(Image.open(urlopen(jpg)))#have to use urlopen to convert the string into a url
    im_orig = np.copy(im)
    width, height, depth = im.shape
    randX = randint(30, 70) * randrange(-1, 3, 2)
    randY = randint(30, 70) * randrange(-1, 3, 2)

    im_xml = urlopen(xml)  # again, opening XML doc from url requires urlopen, not the normal open() function
    data_dict = xmltodict.parse(im_xml.read())
    filename = data_dict['annotation']['path'].split('/')[2]
    filename_edited = 'synth' + filename
    xml_filename_edited = filename_edited[:-3] + "xml"

    cordinates = []
    new_cordinates = []
    id = 0  # initialise a counter for IDing each ball
    # need to check if the 'object' node is returning a list(because there are mutiple balls) or a dictionary (because there is only one ball)
    data_type = type(data_dict['annotation']['object'])
    data_type_list = False
    if data_type == type(cordinates):  # i.e data_type is a list so there are multiple balls
        data_type_list = True
        for i in (data_dict['annotation']['object']):  # loop through all object nodes and save within a unique ID, and object label
            dict = {}
            dict_new = {}  # dict_new will hold the amended coordinates once combined with a random number
            dict['id'] = id
            dict_new['id'] = id
            dict['name'] = i['name']
            dict_new['name'] = i['name']

            for k, v in i['bndbox'].items():  # loop through all bbox nodes for each saved object
                dict[k] = int(v)  # x and y cordinates of ball

                if k[0] == 'x':
                    dict_new[k] = int(v) + randX  # x cordinates of new position for ball
                else:
                    dict_new[k] = int(v) + randY  # y cordinates of new position for ball
            cordinates.append(dict)
            new_cordinates.append(dict_new)
            id += 1
    else:
        # no need to loop as there is only one ball, so object node is a dictionary
        dict = {}
        dict_new = {}  # dict_new will hold the amended coordinates once combined with a random number
        dict['id'] = id
        dict_new['id'] = id
        dict['name'] = data_dict['annotation']['object']['name']
        dict_new['name'] = data_dict['annotation']['object']['name']

        for k, v in data_dict['annotation']['object']['bndbox'].items():
            dict[k] = int(v)  # x and y cordinates of ball

            if k[0] == 'x':
                dict_new[k] = int(v) + randX  # x cordinates of new position for ball
            else:
                dict_new[k] = int(v) + randY  # y cordinates of new position for ball

        cordinates.append(dict)
        new_cordinates.append(dict_new)

    # loop through all new_cordinates and for any that are over or under the height/width limit, reduce both the max and min values to within the limit
    for i in new_cordinates:
        for k, v in i.items():
            if k == 'ymax' and v > width:  # if ymax is greater than the image or width
                diff = v - width
                i['ymin'] -= diff
                i['ymax'] = width

            if k == 'ymin' and v < 0:  # if ymin is a negative
                diff = v * -1
                i['ymin'] = 0
                i['ymax'] += diff

            if k == 'xmax' and v > height:  # if xmax is greater than image height
                diff = v - height
                i['xmin'] -= diff
                i['xmax'] = height

            if k == 'xmin' and v < 0:  # if xmin is a negative
                diff = v * -1
                i['xmin'] = 0
                i['xmax'] += diff

    for i in range (len(cordinates)):#loop though both the cordinate and new_cordainte lists and for each ball cut and paste the ball/background

        #cut out current ball position, paste it in new rand position, and replace ball with either the background from the rand cooridaintes, or with an average background value
        np_img_ball = im[cordinates[i]['ymin']:cordinates[i]['ymax'],cordinates[i]['xmin']:cordinates[i]['xmax'], :]#image of ball
        np_img_background = im[new_cordinates[i]['ymin']:new_cordinates[i]['ymax'],new_cordinates[i]['xmin']:new_cordinates[i]['xmax'], :]#image of background where ball will go
        newbackground = np_img_background.copy()
        np_average = int(np.average(np_img_background))#get average background pixel colour from image

        #paste ball picture onto background section of original image
        im[new_cordinates[i]['ymin']:new_cordinates[i]['ymax'], new_cordinates[i]['xmin']:new_cordinates[i]['xmax'], :] = np_img_ball

        #back fill original cordinates with background
        #np_img_background = np.full(np_img_background.shape,np_average) #uncomment this section to use the average background instead
        im[cordinates[i]['ymin']:cordinates[i]['ymax'],cordinates[i]['xmin']:cordinates[i]['xmax'], :] = newbackground# could use np_average instead

        #new_im = Image.fromarray((im))
        #new_im.show()


    return data_dict

#result=show_image('https://storage.googleapis.com/roboticsaiapp_upload2/labels/Orangeball180731.jpg','https://storage.googleapis.com/roboticsaiapp_upload2/labels/Orangeball180731.xml') # for testing locally