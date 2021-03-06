import numpy as np
from PIL import Image as im
import cv2
from ament_index_python.packages import get_package_share_directory

class Recognizer_small(object):
    def __init__(self,world):
        if world == 'world_1':
            self.tile_area = [3e6,4e6]
        elif world == 'world_2':
            self.tile_area = [1.4e6,2e6]
    
    def angle_cos(self,p0, p1, p2):
        d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
        return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )
    
    def find_squares(self,contours):
        squares = []#make a void list,to collect the contours which match the condition
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, True) #compute the perimeter of the contour
            cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True) #Polygon approximation
            #if the approximated polygon has 4 sides,and area>1000 and a convex polygon
            if len(cnt) == 4 and cv2.contourArea(cnt) > self.tile_area[0] and cv2.contourArea(cnt)<self.tile_area[1] and cv2.isContourConvex(cnt):
                cnt = cnt.reshape(-1, 2)
                max_cos = np.max([self.angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in range(4)])
                if max_cos < 0.1:# if nearly right angle
                    squares.append(cnt)
        return squares

    def compute_center(self,contour):
        M = cv2.moments(contour)  
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        return center_x,center_y

    def imgcor2boxcor(self,x,y):#transformation from coordinate on the image to coordinate of the physic world 
        box_x = ((7227.-y+1800)/3)/1000
        box_y = ((4518.-x)/3)/1000
        return box_x,box_y
    def durch_translation(self,img):
        #perspective transform
        M = np.load(get_package_share_directory('joy_control')+'/M_9037*7228.npy')#load the matrix for perspective transfomation
        img = cv2.warpPerspective(img,M,(9037,7228))#project the image to a big picture, each pixel is 1mm 
        gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)#Grayscale
        _, binary = cv2.threshold(gray,205,255,cv2.THRESH_BINARY)#Binarization???for this task when the thresh set between 200-210,with the best effect
        contours,_ = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        contours = self.find_squares(contours)
        #compute the angle of the conotours with the horizon
        angles = []
        for i in contours:
            rect = cv2.minAreaRect(i)#fit a rectangle with the minimal area,in ideal,this rectangle should be the contour self
            angles.append(np.minimum(np.absolute(rect[2]),np.absolute(90+rect[2])))
            #sins.append(np.absolute(np.sin(np.deg2rad(rect[2]))))#????????????sin?????????????????????????????????????????????0???-90????????????
        angle = np.mean(angles)#
        cos = np.cos(np.deg2rad(angle))
        sin = np.sin(np.deg2rad(angle))
        #compute how much it should translate,603 is the sollwert(603mm is the distance zwischen tiles)
        tx = 1809*cos#compute translation distance along X-axis
        ty = 1809*sin#compute translation distance along Y-axis
        #compute new contours after translation, if beyond the image, throw it
        new_contours = [] 
        for i in range(len(contours)):
            a_contour = contours[i]+np.array([tx,ty])
            if a_contour[a_contour>7227].size>0:
                pass
            else:
                new_contours.append(a_contour)

        new_contours = np.int32(new_contours)

        #compare all new contour with feature of ground, if the color of a contours'center is gray, that means there is no tile
        next_contours = []
        img_coordinate = []
        for i in new_contours:
            x,y = self.compute_center(i)
            #if color on center is gray, then save it in a list
            if np.std(img[y][x])<0.1:#attention! Numpy index of a image is image[y][x],x is horizon,y is vertical
                next_contours.append(i)
                img_coordinate.append((x,y))
        next_contours = np.int32(next_contours)
        #frome image coordinate to coordinate relative to the center of the Fliesenleger
        box_coordinate = []
        for i in img_coordinate:
            box_x,box_y = self.imgcor2boxcor(i[0],i[1])
            box_coordinate.append([box_x,box_y,-0.845,0.,0.,angle])

        for i in img_coordinate: 
            img = cv2.circle(img,i, 5, (255, 0, 0), -1)#draw the centers of the choosen contour
        cv2.drawContours(img,next_contours,-1,(0,0,255),3)#draw the choosen contour 
        self.img_contours = im.fromarray(img)
        
        return box_coordinate



class Recognizer_middle(object):
    def __init__(self,world):
        if world == 'world_1':
            self.tile_area = [8.5e6,1.5e7]
        elif world == 'world_2':
            self.tile_area = [4.25e6,7.5e6]
    
    def angle_cos(self,p0, p1, p2):
        d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
        return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )
    
    def find_squares(self,contours):
        squares = []#make a void list,to collect the contours which match the condition
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, True) #compute the perimeter of the contour
            cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True) #Polygon approximation
            #if the approximated polygon has 4 sides,and area>1000 and a convex polygon
            if len(cnt) == 4 and cv2.contourArea(cnt) > self.tile_area[0] and cv2.contourArea(cnt)<self.tile_area[1] and cv2.isContourConvex(cnt):
                cnt = cnt.reshape(-1, 2)
                max_cos = np.max([self.angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in range(4)])
                if max_cos < 0.1:# if nearly right angle
                    squares.append(cnt)
        return squares

    def compute_center(self,contour):
        M = cv2.moments(contour)  
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        return center_x,center_y

    def imgcor2boxcor(self,x,y):#transformation from coordinate on the image to coordinate of the physic world 
        box_x = ((12045-y+3000)/5)/1000
        box_y = ((7530-x)/5)/1000
        return box_x,box_y
    def durch_translation(self,img):
        M = np.load(get_package_share_directory('joy_control')+'/M_15061*12046.npy')#load the matrix for perspective transfomation
        img = cv2.warpPerspective(img,M,(15061,12046))#project the image to a big picture, each pixel is 1mm 
        gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)#Grayscale
        _, binary = cv2.threshold(gray,205,255,cv2.THRESH_BINARY)#Binarization???for this task when the thresh set between 200-210,with the best effect
        contours, _ = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        contours = self.find_squares(contours)
        #compute the angle of the conotours with the horizon
        angles = []
        for i in contours:
            rect = cv2.minAreaRect(i)#fit a rectangle with the minimal area,in ideal,this rectangle should be the contour self
            angles.append(np.minimum(np.absolute(rect[2]),np.absolute(90+rect[2])))
            #sins.append(np.absolute(np.sin(np.deg2rad(rect[2]))))#????????????sin?????????????????????????????????????????????0???-90????????????
        angle = np.mean(angles)#
        cos = np.cos(np.deg2rad(angle))
        sin = np.sin(np.deg2rad(angle))
        #compute how much it should translate,603 is the sollwert(603mm is the distance zwischen tiles)
        tx = 3015*cos#compute translation distance along X-axis
        ty = 3015*sin#compute translation distance along Y-axis
        #compute new contours after translation, if beyond the image, throw it
        new_contours = [] 
        for i in range(len(contours)):
            a_contour = contours[i]+np.array([tx,ty])
            if a_contour[a_contour>12045].size>0:
                pass
            else:
                new_contours.append(a_contour)

        new_contours = np.int32(new_contours)

        #compare all new contour with feature of ground, if the color of a contours'center is gray, that means there is no tile
        next_contours = []
        img_coordinate = []
        for i in new_contours:
            x,y = self.compute_center(i)
            #if color on center is gray, then save it in a list
            if np.std(img[y][x])<0.1:#attention! Numpy index of a image is image[y][x],x is horizon,y is vertical
                next_contours.append(i)
                img_coordinate.append((x,y))
        next_contours = np.int32(next_contours)
        #frome image coordinate to coordinate relative to the center of the Fliesenleger
        box_coordinate = []
        for i in img_coordinate:
            box_x,box_y = self.imgcor2boxcor(i[0],i[1])
            box_coordinate.append([box_x,box_y,-0.845,0.,0.,angle])

        for i in img_coordinate: 
            img = cv2.circle(img,i, 5, (255, 0, 0), -1)#draw the centers of the choosen contour
        cv2.drawContours(img,next_contours,-1,(0,0,255),3)#draw the choosen contour 
        self.img_contours = im.fromarray(img)
        
        return box_coordinate


class Recognizer_big(object):
    def __init__(self,world):
        if world == 'world_1':
            self.tile_area = [3.4e7,4e7]
        elif world == 'world_2':
            self.tile_area = [1.7e7,2e7]
    
    def angle_cos(self,p0, p1, p2):
        d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
        return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )
    
    def find_squares(self,contours):
        squares = []#make a void list,to collect the contours which match the condition
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, True) #compute the perimeter of the contour
            cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True) #Polygon approximation
            #if the approximated polygon has 4 sides,and area>1000 and a convex polygon
            if len(cnt) == 4 and cv2.contourArea(cnt) > self.tile_area[0] and cv2.contourArea(cnt)<self.tile_area[1] and cv2.isContourConvex(cnt):
                #M = cv2.moments(cnt) #compute the moment of the contour
                #cx = int(M['m10']/M['m00'])
                #cy = int(M['m01']/M['m00'])#compute the center
                cnt = cnt.reshape(-1, 2)
                max_cos = np.max([self.angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in range(4)])
                if max_cos < 0.1:# if nearly right angle
                    squares.append(cnt)
        return squares

    def compute_center(self,contour):
        M = cv2.moments(contour)  
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        return center_x,center_y

    def imgcor2boxcor(self,x,y):#transformation from coordinate on the image to coordinate of the physic world 
        box_x = ((24090-y+6000)/10)/1000
        box_y = ((15060-x)/10)/1000
        return box_x,box_y
    def durch_translation(self,img):
        #perspective transform
        M = np.load(get_package_share_directory('joy_control')+'/M_30121*24091.npy')#load the matrix for perspective transfomation
        img = cv2.warpPerspective(img,M,(30121,24091))#project the image to a big picture, each pixel is 1mm 
        gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)#Grayscale
        _, binary = cv2.threshold(gray,205,255,cv2.THRESH_BINARY)#Binarization???for this task when the thresh set between 200-210,with the best effect
        contours,_ = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        contours = self.find_squares(contours)
        #compute the angle of the conotours with the horizon
        angles = []
        #centers = []
        #w_h = []
        for i in contours:
            rect = cv2.minAreaRect(i)#fit a rectangle with the minimal area,in ideal,this rectangle should be the contour self
            angles.append(np.minimum(np.absolute(rect[2]),np.absolute(90+rect[2])))
            #sins.append(np.absolute(np.sin(np.deg2rad(rect[2]))))#????????????sin?????????????????????????????????????????????0???-90????????????
        angle = np.mean(angles)#
        cos = np.cos(np.deg2rad(angle))
        sin = np.sin(np.deg2rad(angle))
        #compute how much it should translate,603 is the sollwert(603mm is the distance zwischen tiles)
        tx = 6030*cos#compute translation distance along X-axis
        ty = 6030*sin#compute translation distance along Y-axis
        #compute new contours after translation, if beyond the image, throw it
        new_contours = [] 
        for i in range(len(contours)):
            a_contour = contours[i]+np.array([tx,ty])
            if a_contour[a_contour>24090].size>0:
                pass
            else:
                new_contours.append(a_contour)

        new_contours = np.int32(new_contours)

        #compare all new contour with feature of ground, if the color of a contours'center is gray, that means there is no tile
        next_contours = []
        img_coordinate = []
        for i in new_contours:
            x,y = self.compute_center(i)
            #if color on center is gray, then save it in a list
            if np.std(img[y][x])<0.1:#attention! Numpy index of a image is image[y][x],x is horizon,y is vertical
                next_contours.append(i)
                img_coordinate.append((x,y))
        next_contours = np.int32(next_contours)
        #frome image coordinate to coordinate relative to the center of the Fliesenleger
        box_coordinate = []
        for i in img_coordinate:
            box_x,box_y = self.imgcor2boxcor(i[0],i[1])
            box_coordinate.append([box_x,box_y,-0.845,0.,0.,angle])

        for i in img_coordinate: 
            img = cv2.circle(img,i, 5, (255, 0, 0), -1)#draw the centers of the choosen contour
        cv2.drawContours(img,next_contours,-1,(0,0,255),3)#draw the choosen contour 
        self.img_contours = im.fromarray(img)
        
        return box_coordinate