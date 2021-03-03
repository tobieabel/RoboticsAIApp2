import numpy as np
from PIL import Image
import xmltodict
from random import randint, randrange
import os
import cv2
import copy

#save arrays and dictionaries as jpg and xml files, with unique names
def save_files(jpg,xml,filename,synth_type,data_type_list =False ,new_cordinates=None):
    file = Image.fromarray(np.uint8(jpg))
    file.save(os.path.join(jpg_Output,filename+synth_type+".jpg"))

    xml['annotation']['filename'] = filename+synth_type+".jpg"
    xml['annotation']['path'] = '/my-project-name/' + filename+synth_type+".jpg"
    if synth_type == 'Synth':
        new_cordinates_iter = 0
        if data_type_list:  # i.e data_type is a list so there are multiple balls
            for i in xml['annotation']['object']:
                i['bndbox']['ymin'] = str(new_cordinates[new_cordinates_iter]['ymin'])
                i['bndbox']['xmin'] = str(new_cordinates[new_cordinates_iter]['xmin'])
                i['bndbox']['ymax'] = str(new_cordinates[new_cordinates_iter]['ymax'])
                i['bndbox']['xmax'] = str(new_cordinates[new_cordinates_iter]['xmax'])
                new_cordinates_iter += 1
        else:  # i.e. there is just one ball
            xml['annotation']['object']['bndbox']['ymin'] = str(
                new_cordinates[new_cordinates_iter]['ymin'])
            xml['annotation']['object']['bndbox']['xmin'] = str(
                new_cordinates[new_cordinates_iter]['xmin'])
            xml['annotation']['object']['bndbox']['ymax'] = str(
                new_cordinates[new_cordinates_iter]['ymax'])
            xml['annotation']['object']['bndbox']['xmax'] = str(
                new_cordinates[new_cordinates_iter]['xmax'])

    output = xmltodict.unparse(xml, pretty=True)
    output1 = output[39:]  # remove first 39 characters, this is a header not on the original xml doc, but added by xmltodict function
    with open("/Users/tobieabel/Desktop/BallXML_synth/" + filename + synth_type + '.xml','w') as file:
        file.write(output1)

# Create Blurred images and xml files
def blur(list_of_im):
    # Create Blurred image
    for i in list_of_im:
        blur_im = cv2.GaussianBlur(i["nd_array"], (11, 11), 0)
        save_files(blur_im,i["data_dict"],i["name"],"Blur")

def bright(list_of_im):
    # Create Bright and Dull images
    for i in list_of_im:
        Bright_im = cv2.cvtColor(i["nd_array"], cv2.COLOR_BGR2HSV)  # convert to Color channels
        h1, s1, v1 = cv2.split(Bright_im)  # split to be used for bright images
        h2, s2, v2 = cv2.split(Bright_im)  # split to be used for dull images

        # increase value channel for bright images by 60, making sure not to go over the 255 limit
        # couldn't use np.clip here as you need to apply the change before clipping the values, and if applying the change
        # takes it over the 255 limit its automatically set to 0
        lim = 255 - 60
        v1[v1 > lim] = 255
        v1[v1 <= lim] += 60

        # decrease value channel for dull images by 60, making sure not to go below 0
        v2[v2 <= 60] = 0
        v2[v2 > 60] -= 60

        Bright_hsv = cv2.merge((h1, s1, v1))
        Bright_im = cv2.cvtColor(Bright_hsv, cv2.COLOR_HSV2BGR)  # convert back to RGB
        save_files(Bright_im,i["data_dict"],i["name"],"Bright")

        Dull_hsv = cv2.merge((h2, s2, v2))
        Dull_im = cv2.cvtColor(Dull_hsv, cv2.COLOR_HSV2BGR)
        save_files(Dull_im,i["data_dict"],i["name"],"Dull")

def noisy(list_of_im):
    # Create noisy image with "poisson-distributed" effect
    for i in list_of_im:
        unique_vals = np.unique(i["nd_array"])
        vals = len(unique_vals)
        vals = 2 ** np.ceil(np.log2(vals))
        noisy_im = np.random.poisson(i["nd_array"] * vals) / float(vals)
        save_files(noisy_im,i["data_dict"],i["name"],"Noisy")
        #noisy = Image.fromarray(np.uint8(noisy_im))
        #noisy.save("/Users/tobieabel/Desktop/Ball_synth/" + 'noisy.jpg')
        # create xml file


#get all image names from a folder and declare output folders
jpgsource = "/Users/tobieabel/Desktop/Ball"
xmlsource = "/Users/tobieabel/Desktop/BallXML"
jpg_Output = "/Users/tobieabel/Desktop/Ball_synth/"
xml_Output = "/Users/tobieabel/Desktop/BallXML_synth/"

#get list of filenames.  Need to sort the file names, otherwise they present in different order
jpgFiles = sorted([i for i in os.listdir(jpgsource)if i != ".DS_Store"])#weird .DS_Store hidden file sometimes in Mac folders
xmlFiles = sorted([i for i in os.listdir(xmlsource)if i != ".DS_Store"])

#loop through the list of jpg's and xmls files, and perform all transform logic
for i in range(len(jpgFiles)):
    im = np.array(Image.open(jpgsource + '/' + jpgFiles[i]))
    im_orig = np.copy(im)
    im_xml = open(xmlsource + '/' + xmlFiles[i])
    width, height, depth = im.shape
    randX = randint(30,70)* randrange(-1,3,2)# amount of pixels to move ball in x axis.  randrange ensures number could be negative or positive
    print(randX)
    randY = randint(30,70)* randrange(-1,3,2)#amount of pixels to move ball in y axis
    print(randY)

    #parse the xml file, and store the bounding box cordinates in a dictionary
    #then store the new ball position (existing position offset by rand number generated above) in a new dictionary
    data_dict = xmltodict.parse(im_xml.read())
    filename = data_dict['annotation']['path'].split('/')[2]
    filename_edited = 'synth' + filename
    xml_filename_edited = filename_edited[:-3] + "xml"
    jpgFilename = jpgFiles[i][:-4]
    jpgFilename_ed = jpgFilename + 'Synth'

    cordinates=[]
    new_cordinates = []
    id = 0 #initialise a counter for IDing each ball
    #need to check if the 'object' node is returning a list(because there are mutiple balls) or a dictionary (because there is only one ball)
    data_type = type(data_dict['annotation']['object'])
    data_type_list = False
    if data_type == type(cordinates):#i.e data_type is a list so there are multiple balls
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
        #no need to loop as there is only one ball, so object node is a dictionary
        dict = {}
        dict_new = {}  # dict_new will hold the amended coordinates once combined with a random number
        dict['id'] = id
        dict_new['id'] = id
        dict['name'] = data_dict['annotation']['object']['name']
        dict_new['name'] = data_dict['annotation']['object']['name']

        for k,v in data_dict['annotation']['object']['bndbox'].items():
                dict[k] = int(v)  # x and y cordinates of ball

                if k[0] == 'x':
                    dict_new[k] = int(v) + randX  # x cordinates of new position for ball
                else:
                    dict_new[k] = int(v) + randY  # y cordinates of new position for ball


        cordinates.append(dict)
        new_cordinates.append(dict_new)

    #loop through all new_cordinates and for any that are over or under the height/width limit, reduce both the max and min values to within the limit
    for i in new_cordinates:
        for k,v in i.items():
            if k == 'ymax' and v > width:#if ymax is greater than the image or width
                diff = v-width
                i['ymin'] -= diff
                i['ymax'] = width

            if k =='ymin' and v < 0:#if ymin is a negative
                diff = v * -1
                i['ymin'] = 0
                i['ymax'] += diff

            if k == 'xmax' and v > height:#if xmax is greater than image height
                diff = v - height
                i['xmin'] -= diff
                i['xmax'] = height

            if k == 'xmin' and v < 0:#if xmin is a negative
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
        #np_img_background = np.full(np_img_background.shape,np_average)
        im[cordinates[i]['ymin']:cordinates[i]['ymax'],cordinates[i]['xmin']:cordinates[i]['xmax'], :] = newbackground# could use np_average instead

    #save new synthetic image array to jpg and the new cordinates to a new xmlfile
    data_dict_edited = copy.deepcopy(data_dict)#copy() only copies the first level of dictionary, so need deep copy
    save_files(im,data_dict_edited, jpgFilename, 'Synth', data_type_list,new_cordinates)

    #create dict of np images along with their filename and xml data dict, for both the original image and any synthetic images created
    list_of_im = [{"name":jpgFilename,"nd_array":im_orig,"data_dict":data_dict},{"name":jpgFilename_ed,"nd_array":im,"data_dict":data_dict_edited}]
    #call blur function on all images, and pass paramters needed to save the new images and xml files
    blur(list_of_im)
    #call bright fucntion, creates both bright and dull images
    bright(list_of_im)
    #call noise function
    noisy(list_of_im)








