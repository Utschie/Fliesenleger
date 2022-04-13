import numpy as np
from PIL import Image as im
import matplotlib.pyplot as plt
import cv2

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )
def find_squares(contours):
    squares = []#make a void list,to collect the contours which match the condition
    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True) #compute the perimeter of the contour
        cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True) #Polygon approximation
        #if the approximated polygon has 4 sides,and area>1000 and a convex polygon
        if len(cnt) == 4 and cv2.contourArea(cnt) > 3e6 and cv2.isContourConvex(cnt):
            M = cv2.moments(cnt) #compute the moment of the contour
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])#compute the center
            cnt = cnt.reshape(-1, 2)
            max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in range(4)])
            if max_cos < 0.1:# if nearly right angle
                squares.append(cnt)
    return squares

def compute_center(contour):
    M = cv2.moments(i)  
    center_x = int(M["m10"] / M["m00"])
    center_y = int(M["m01"] / M["m00"])
    return center_x,center_y

def imgcor2boxcor(x,y):#transformation from coordinate on the image to coordinate of the physic world 
    box_x = np.trunc(((7227-y+1800)/3+1/6))/1000#这里是因为纵向是坐标0-7226共7227个像素格，所以到最低边像素中心是7226,然后在减去
    box_y = np.trunc(((4518-x)/3))/1000
    return box_x,box_y
#perspective transform
img = cv2.imread('/home/jsy/图片/left_eye_5k_正.png')#read original picture
img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)#from BGR to RGB
M = np.load('/home/jsy/图片/M_9037*7228.npy')#load the matrix for perspective transfomation
img = cv2.warpPerspective(img,M,(9037,7228))#project the image to a big picture, each pixel is 1mm 
gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)#Grayscale
ret, binary = cv2.threshold(gray,205,255,cv2.THRESH_BINARY)#Binarization，for this task when the thresh set between 200-210,with the best effect
contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
contours = find_squares(contours)
#compute the angle of the conotours with the horizon
angles = []
centers = []
w_h = []
for i in contours:
    rect = cv2.minAreaRect(i)#fit a rectangle with the minimal area,in ideal,this rectangle should be the contour self
    angles.append(np.minimum(np.absolute(rect[2]),np.absolute(90+rect[2])))
    #sins.append(np.absolute(np.sin(np.deg2rad(rect[2]))))#之所以用sin而不是角度是因为正对着时会出现0和-90两种数字
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
    x,y = compute_center(i)
    #if color on center is gray, then save it in a list
    if np.std(img[y][x])<0.1:#attention! Numpy index of a image is image[y][x],x is horizon,y is vertical
        next_contours.append(i)
        img_coordinate.append((x,y))
next_contours = np.int32(next_contours)
#frome image coordinate to coordinate relative to the center of the Fliesenleger
box_coordinate = []
for i in img_coordinate:
    box_x,box_y = imgcor2boxcor(i[0],i[1])
    box_coordinate.append([box_x,box_y,0.005,0.,0.,angle])

print('The next tile\'s Position on the image is:'+'   '+str(img_coordinate))
print('The next tile\'s Position related to the maschine is:'+'   '+str(box_coordinate))
for i in img_coordinate: 
    img = cv2.circle(img,i, 5, (255, 0, 0), -1)#draw the centers of the choosen contour
cv2.drawContours(img,next_contours,-1,(0,0,255),3)#draw the choosen contour 
img_contours = im.fromarray(img)
img_contours#show it
