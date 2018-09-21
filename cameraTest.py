from scipy.spatial                           import distance as dist
from imutils                                 import perspective
from imutils                                 import contours
import numpy                                 as np
import glob
import imutils
import cv2
import time
import re
import math


refObj = None
D = 0
currentX, currentY = 0, 0
calX = 0
calY = 0

markerWidth         = 0.5*25.4
counter =0

#def initialize(self):

def midpoint(ptA, ptB):
    return ((ptA[0]+ptB[0])*0.5, (ptA[1]+ptB[1])*0.5)

def removeOutliersAndAverage(data):
    mean = np.mean(data)
    sd = np.std(data)
    tArray = [x for x in data if ( (x > mean-2.0*sd) and (x<mean+2.0*sd))]
    return np.average(tArray), np.std(tArray)

def translatePoint(xB, yB, xA, yA, angle):
    cosa = math.cos((angle)*3.141592/180.0)
    sina = math.sin((angle)*3.141592/180.0)
    xB -= xA
    yB -= yA
    _xB = xB*cosa - yB*sina
    _yB = xB*sina + yB*cosa
    xB = _xB+xA
    yB = _yB+yA
    return xB, yB

def simplifyContour(c):
    tolerance = 0.01
    while True:
        _c = cv2.approxPolyDP(c, tolerance*cv2.arcLength(c,True), True)
        if len(_c)<=4 or tolerance<0.5:
            break
        tolerance += 0.01
    if len(_c)<4:# went too small.. now lower the tolerance until four points or more are reached
        while True:
            tolerance -= 0.01
            _c = cv2.approxPolyDP(c, tolerance*cv2.arcLength(c,True), True)
            if len(_c)>=4 or tolerance <= 0.1:
                break
#    print "len:"+str(len(c))+", tolerance:"+str(tolerance)
    return _c #_c is the smallest approximation we can find with four our more


files = []

file = "testImages\image2-1.png"

averageDx = np.empty([],dtype=float)
averageDy = np.empty([],dtype=float)
averageDi = np.empty([],dtype=float)
testCount = 0
outFile = open("cameraValues.csv","w")
cv2.namedWindow("image",0)

for file in glob.glob("testImages\*.png"):
#file = "testImages/image2-1.png"
    if (True):
        print file
        image = cv2.imread(file)
        #cv2.imshow("Image", image)

        #cv2.waitKey(0)
        if True:
            #cv2.imwrite("image"+str(self.counter)+"-"+str(x)+".png",image)
            #self.counter += 1
            #height, width, channels = image.shape
            #cropDistance = 0#75
            #image = image[cropDistance:height-cropDistance, cropDistance:width-cropDistance]
            height, width, channels = image.shape
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #gray = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(gray, 175, 200)
            #cv2.imshow("Canny", edged)
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)
            cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if imutils.is_cv2() else cnts[1]
            (cnts, _) = contours.sort_contours(cnts)
            colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0), (255, 0, 255))
            refObj = None

            xA = int(width/2)
            yA = int(height/2)

            #orig = edged.copy()
            #orig = cv2.cvtColor(orig, cv2.COLOR_GRAY2BGR)
            orig = image.copy()
            print "found "+str(len(cnts))+" contours"
            maxArea = 0
            for cTest in cnts:
                if (cv2.contourArea(cTest)>maxArea):
                    maxArea = cv2.contourArea(cTest)
                    c = cTest
            #if True: #for c in cnts:

            if cv2.contourArea(c) > 100:
                #continue
                cv2.drawContours(orig, [c.astype("int")], -1, (255, 255, 0), 2)
                #print "len:"+str(len(c))
                #simplify the contour to get it as square as possible (i.e., remove the noise from the edges)
                c=simplifyContour(c)

                cv2.drawContours(orig, [c.astype("int")], -1, (255, 0, 0), 2)
                print cv2.contourArea(c)
                box = cv2.minAreaRect(c)

                angle = box[-1]
                print angle
                if (abs(angle+90)<30):
                    _angle = angle+90
                else:
                    _angle = angle
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

                M = cv2.getRotationMatrix2D((xA,yA),_angle,1)
                orig = cv2.warpAffine(orig,M,(width,height))


                xB = np.average(box[:, 0])
                yB = np.average(box[:, 1])
                (tl, tr, br, bl) = box
                (tlblX, tlblY) = midpoint(tl, bl)
                (trbrX, trbrY) = midpoint(tr, br)
                D = dist.euclidean((tlblX,tlblY),(trbrX,trbrY))/markerWidth
                print "Distance = "+str(D)
                cos = math.cos(angle*3.141592/180.0)
                sin = math.sin(angle*3.141592/180.0)
                if (_angle<30):
                    _angle = _angle *-1.0
                print _angle
                print xB
                print yB
                xB,yB = translatePoint(xB,yB,xA,yA,_angle)
                print xB
                print yB
                #cv2.line(orig, (int(xB-15), int(yB)-15))
                cv2.circle(orig, (int(xA), int(yA)), 10, colors[0], 1)
                cv2.line(orig, (xA, yA-15), (xA, yA+15), colors[0], 1)
                cv2.line(orig, (xA-15, yA), (xA+15, yA), colors[0], 1)
                cv2.circle(orig, (int(xB), int(yB)), 10, colors[3], 1)
                cv2.line(orig, (int(xB), int(yB-15)), (int(xB), int(yB+15)), colors[3], 1)
                cv2.line(orig, (int(xB-15), int(yB)), (int(xB+15), int(yB)), colors[3], 1)
                #cv2.line(orig, (int(xB)-15, int(yB)), (int(xB)+15, int(yB)), colors[3], 1)

                #cv2.line(orig, (xA, yA), (int(xB), int(yB)), colors[0], 2)
                Dist = dist.euclidean((xA, yA), (xB, yB)) / D
                Dx = dist.euclidean((xA,0), (xB,0))/D
                if (xA>xB):
                    Dx *= -1.0
                Dy = dist.euclidean((0,yA), (0,yB))/D
                if (yA<yB):
                    Dy *= -1.0
                (mX, mY) = midpoint((xA, yA), (xB, yB))
                cv2.putText(orig, file, (15, 15),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                #cv2.putText(orig, "{:.0f}, {:.0f}".format(box[0,0],box[0,1]), (box[0,0], box[0,1]),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                #cv2.putText(orig, "{:.0f}, {:.0f}".format(box[1,0],box[1,1]), (box[1,0], box[1,1]),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                #cv2.putText(orig, "{:.0f}, {:.0f}".format(box[2,0],box[2,1]), (box[2,0], box[2,1]),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                #cv2.putText(orig, "{:.0f}, {:.0f}".format(box[3,0],box[3,1]), (box[3,0], box[3,1]),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                #cv2.putText(orig, "{:.3f}, {:.3f}".format(xB,yB,0.0), (int(mX), int(mY - 40)),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                cv2.putText(orig, "Dx:{:.3f}, Dy:{:.3f}->Di:{:.3f}mm".format(Dx,Dy,Dist), (15, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                outFile.write("{:.3f}, {:.3f}, {:.3f}\n".format(Dx,Dy,Dist))
                if True:#(Dist>0.25):
                    cv2.imshow("image", orig)
                    #cv2.waitKey(0)
                    #cv2.destroyAllWindows()
                    if (testCount == 15):
                        Dx = 19995.0
                    testCount += 1
                    averageDx = np.append(averageDx, [Dx])
                    averageDy = np.append(averageDy, [Dy])
                    averageDi = np.append(averageDi, [Dist])



avgDx, stdDx = removeOutliersAndAverage(averageDx)
avgDy, stdDy = removeOutliersAndAverage(averageDy)
avgDi, stdDi = removeOutliersAndAverage(averageDi)
print "AverageDx:"+str(avgDx)+" at "+str(stdDx)+" sd"
print "AverageDy:"+str(avgDy)+" at "+str(stdDy)+" sd"
print "AverageDi:"+str(avgDi)+" at "+str(stdDi)+" sd"
outFile.close()
