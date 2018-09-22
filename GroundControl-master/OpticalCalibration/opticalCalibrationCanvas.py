from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty, BooleanProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.texture                   import Texture
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from kivy.graphics.transformation            import Matrix
from kivy.clock                              import Clock
from kivy.uix.image                          import Image
from kivy.app                                import App
from kivy.uix.popup                          import Popup
from kivy.uix.label                          import Label
from UIElements.notificationPopup            import NotificationPopup
from Settings                                import maslowSettings
from functools                               import partial
from scipy.spatial                           import distance as dist
from imutils                                 import perspective
from imutils                                 import contours
import numpy                                 as np
import imutils
import cv2
import time
import re
import math
import sys
import global_variables

class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None

    def start(self, capture, fps=30):
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        Clock.unschedule_interval(self.update)
        self.capture = None

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture

    def getCapture(self):
        return self.capture.read()

#capture = None

class MeasuredImage(Image):
    def __init__(self, **kwargs):
        super(MeasuredImage, self).__init__(**kwargs)

    def update(self, frame):
        cv2.imwrite("measuredImage.png",frame)
        buf1 = cv2.flip(frame,0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.texture = image_texture

class OpticalCalibrationCanvas(GridLayout):

    capture = None
    cameraCount = 0
    refObj = None
    D = 0
    done = ObjectProperty(None)
    currentX, currentY = 0, 0
    calX = 0
    calY = 0
    matrixSize = (31, 15)
    calErrorsX = np.zeros(matrixSize)
    calErrorsY = np.zeros(matrixSize)


    presets = [ [ [-15 , 7] , [0, 0] ],
                [ [0, 7] , [15, 0] ],
                [ [-15 , 0] , [0, -7] ],
                [ [0, 0] , [15, -7] ],
                [ [-15, 7] , [15, -7] ],
                [ [-1, 1] , [1, -2] ],
                [ [-1, 1] , [1, -2] ],
                [ [-1, 2] , [2, -3] ],
                [ [-1, 2] , [2, -3] ],
               ]

    markerWidth = 0.5*25.4
    inAutoMode = False
    inAutoModeForFirstTime = True
    HomingScanDirection = 1
    HomingX = 0.0
    HomingY = 0.0
    HomingPosX = 0
    HomingPosY = 0
    HomingRange = 4
    HomingTLX = -2
    HomingTLY = +2
    HomingBRX = +2
    HomingBRY = -2
    counter =0

    #def initialize(self):

    def initialize(self):
        xyErrors = self.data.config.get('Computed Settings', 'xyErrorArray')
        self.calErrorsX, self.calErrorsY = maslowSettings.parseErrorArray(xyErrors, True)
        #print str(xErrors[2][0])

        # Work backwards to find a camera (assumes <= 2 cameras)
        for i in reversed(range(2)):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.cameraCount = i + 1
                break
            cap.release()

        print "Found %d cameras" % self.cameraCount
        self.ids.cameras.values = self.cameras()
        self.startCamera(self.cameraCount - 1)

        inAutoMode = False
        inAutoModeForFirstTime = True

    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        self.inAutoMode = False
        self.inAutoModeForFirstTime = True

    def startCamera(self, index):
        self.capture = cv2.VideoCapture(index)
        if self.capture.isOpened():
            self.ids.KivyCamera.start(self.capture)
        else:
            print "Failed to open camera"

    def cameras(self):
        return ["%d" % i for i in range(self.cameraCount)]

    def setCamera(self, val):
        self.capture.release()
        self.startCamera(int(val))

    def on_stop(self):
        self.capture.release()

    def on_UpdateTopLeftX(self,value=[0,False]):
        if (value[1]==False):
            try:
                _tlX=int(self.ids.topLeftX.text)
                self.ids.topLeftX.text = str(_tlX)
                self.HomingTLX = _tlX
            except:
                print "Value not int"
                self.ids.topLeftX.text = ""

    def on_UpdateTopLeftY(self,value=[0,False]):
        if (value[1]==False):
            try:
                _tlY=int(self.ids.topLeftY.text)
                self.ids.topLeftY.text = str(_tlY)
                self.HomingTLY = _tlY
            except:
                print "Value not int"
                self.ids.topLeftY.text = ""

    def on_UpdateBottomRightX(self,value=[0,False]):
        if (value[1]==False):
            try:
                _brX=int(self.ids.bottomRightX.text)
                self.ids.bottomRightX.text = str(_brX)
                self.HomingBRX = _brX
            except:
                print "Value not int"
                self.ids.bottomRightX.text = ""

    def on_UpdateBottomRightY(self,value=[0,False]):
        if (value[1]==False):
            try:
                _brY=int(self.ids.bottomRightY.text)
                self.ids.bottomRightY.text = str(_brY)
                self.HomingBRY = _brY
            except:
                print "Value not int"
                self.ids.bottomRightY.text = ""

    def on_Preset(self, preset):

        self.ids.topLeftX.text = str(self.presets[preset][0][0])
        self.ids.topLeftY.text = str(self.presets[preset][0][1])
        self.ids.bottomRightX.text = str(self.presets[preset][1][0])
        self.ids.bottomRightY.text = str(self.presets[preset][1][1])
        self.HomingTLX = self.presets[preset][0][0]
        self.HomingTLY = self.presets[preset][0][1]
        self.HomingBRX = self.presets[preset][1][0]
        self.HomingBRY = self.presets[preset][1][1]

    def midpoint(self, ptA, ptB):
        return ((ptA[0]+ptB[0])*0.5, (ptA[1]+ptB[1])*0.5)

    def do_Exit(self):
        if self.capture != None:
            self.capture.release()
            self.capture = None
            self.parent.parent.parent.dismiss()

    def translatePoint(self, xB, yB, xA, yA, angle):
        cosa = math.cos((angle)*3.141592/180.0)
        sina = math.sin((angle)*3.141592/180.0)
        xB -= xA
        yB -= yA
        _xB = xB*cosa - yB*sina
        _yB = xB*sina + yB*cosa
        xB = _xB+xA
        yB = _yB+yA
        return xB, yB

    def simplifyContour(self,c):
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

    def updateScreenValues(self):
        self.ids.OpticalCalibrationDistance.text = " pixels\mm: {:.3f}\n".format(self.D)#Cal Error({:.3f},{:.3f})\n".format(self.D, self.calX, self.calY)
        calX = 0
        calY = 0
        count = 0
<<<<<<< HEAD
        #print str(self.HomingTLX)+", "+str(self.HomingBRX)+", "+str(self.HomingTLY)+", "+str(self.HomingBRY)
        for y in range(self.HomingTLY, self.HomingBRY - 1, -1):
            for x in range(self.HomingTLX, self.HomingBRX + 1, +1):
                #if (abs(y)<=7)
                self.ids.OpticalCalibrationDistance.text += "[{:.2f},{:.2f}] ".format(self.calErrorsX[x+15][7-y], self.calErrorsY[x+15][7-y])
                calX += (self.calErrorsX[x+15][7-y]-self.calErrorsX[15][7]) ** 2.0
                calY += (self.calErrorsY[x+15][7-y]-self.calErrorsY[15][7]) ** 2.0
                count += 1
                #print count
=======
        for y in range(self.HomingTLY, self.HomingBRY - 1, -1):
            for x in range(self.HomingTLX, self.HomingBRX + 1, 1):
                if (abs(y)<=7):
                    self.ids.OpticalCalibrationDistance.text += "[{:.2f},{:.2f}] ".format(self.calErrorsX[x+15][7-y], self.calErrorsY[x+15][7-y])
                    calX += (self.calErrorsX[x+15][7-y]-self.calErrorsX[15][7]) ** 2.0
                    calY += (self.calErrorsY[x+15][7-y]-self.calErrorsY[15][7]) ** 2.0
                    count += 1
>>>>>>> 903eb9d488bf4fe8d2f6b96dce4ce5a2e58838b9
            self.ids.OpticalCalibrationDistance.text +="\n"
        calX = math.sqrt(calX/count)
        calY = math.sqrt(calY/count)
        self.ids.OpticalCalibrationDistance.text += "X,Y Offset RMS: {:.3f}, {:.3f}\n".format(calX,calY)


    def removeOutliersAndAverage(self, data):
        mean = np.mean(data)
        print "mean:"+str(mean)
        sd = np.std(data)
        print "sd:"+str(sd)
        tArray = [x for x in data if ( (x > mean-2.0*sd) and (x<mean+2.0*sd))]
        return np.average(tArray), np.std(tArray)


    def on_SaveAndSend(self):
        _str = ""
        _strcomma = ""
        for z in range(2):
            for y in range(15):
                for x in range(31):
                    if ((x==30) and (y==14) and (z==1)):
                        _strcomma = ""
                    else:
                        _strcomma = ","
                    if (z==0):
                        _str += str(int(self.calErrorsX[x][y]*1000))+_strcomma
                    else:
                        _str += str(int(self.calErrorsY[x][y]*1000))+_strcomma
        print _str
        App.get_running_app().data.config.set('Computed Settings', 'xyErrorArray', _str)

    def on_WipeController(self):
        self.data.gcode_queue.put("$RST=O ")

    def on_ReturnToCenter(self):
        print "Moving to:[0, 0]"
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G0 X0 Y0  ")
        self.data.gcode_queue.put("G91  ")

    def on_AutoHome(self):

        minX = self.HomingTLX
        maxX = self.HomingBRX
        minY = self.HomingTLY
        maxY = self.HomingBRY

        if self.inAutoMode == False:
            self.HomingX = 0.0
            self.HomingY = 0.0
            self.HomingPosX = minX
            self.HomingPosY = minY
            self.inAutoMode = True
        else:
            # note, the self.HomingX and self.HomingY are not reinitialzed here
            # The rationale is that the offset for the previous registration point is
            # probably a good starting point for this registration point..
            self.HomingPosX += self.HomingScanDirection
            if ((self.HomingPosX==maxX+1) or (self.HomingPosX==minX-1)):
                if self.HomingPosX == maxX+1:
                    self.HomingPosX = maxX
                else:
                    self.HomingPosX = minX
                self.HomingScanDirection *= -1
                self.HomingPosY -= 1
        if (self.HomingPosY!=maxY-1):
            self.HomeIn()
        else:
            self.inAutoMode = False
            print "Calibration Completed"
            self.printCalibrationErrorValue()




    def on_HomeToPos(self, posX, posY):
        self.HomingPosX = posX
        self.HomingPosY = posY
        self.HomeIn()

    def HomeIn(self):
        _posX = round(self.HomingPosX*3.0+self.HomingX/25.4,4)
        _posY = round(self.HomingPosY*3.0+self.HomingY/25.4,4)
        print "Moving to:[{}, {}]".format(_posX, _posY)
        self.data.units = "INCHES"
        self.data.gcode_queue.put("G20 ")
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G0 X"+str(_posX)+" Y"+str(_posY)+"  ")
        self.data.gcode_queue.put("G91  ")
        self.data.measureRequest = self.on_CenterOnSquare
        #request a measurement
        self.data.gcode_queue.put("B10 L")

    def on_CenterOnSquare(self, doCalibrate=False):
        print "Analyzing Images"
        dxList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        dyList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        diList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        print "here"
        for x in range(10):  #review 10 images
            #print x
            ret, image = self.ids.KivyCamera.getCapture()
            if ret:
                self.ids.MeasuredImage.update(image)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                edged = cv2.Canny(gray, 50, 100)
                edged = cv2.dilate(edged, None, iterations=1)
                edged = cv2.erode(edged, None, iterations=1)
                cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if imutils.is_cv2() else cnts[1]
                (cnts, _) = contours.sort_contours(cnts)
                colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0), (255, 0, 255))
                refObj = None
                height, width, channels = image.shape
                xA = int(width/2)
                yA = int(height/2)

                orig = image.copy()
                maxArea = 0
                for cTest in cnts:
                    if (cv2.contourArea(cTest)>maxArea):
                        maxArea = cv2.contourArea(cTest)
                        c = cTest
                if cv2.contourArea(c)>1000:
                    #approximate to a square (i.e., four contour segments)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 255, 0), 2)
                    #simplify the contour to get it as square as possible (i.e., remove the noise from the edges)
                    c=self.simplifyContour(c)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 0, 0), 2)
                    box = cv2.minAreaRect(c)
                    angle = box[-1]
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

                    if doCalibrate == True:
                        (tl, tr, br, bl) = box
                        (tlblX, tlblY) = self.midpoint(tl, bl)
                        (trbrX, trbrY) = self.midpoint(tr, br)

                        self.D = dist.euclidean((tlblX,tlblY),(trbrX,trbrY))/self.markerWidth
                        self.ids.OpticalCalibrationAutoMeasureButton.disabled = False
                        self.inAutoModeForFirstTime = True


                    cos = math.cos(angle*3.141592/180.0)
                    sin = math.sin(angle*3.141592/180.0)
                    if (_angle<30):
                        _angle = _angle *-1.0
                    print _angle
                    xB,yB = self.translatePoint(xB,yB,xA,yA,_angle)

                    #cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
                    cv2.circle(orig, (int(xA), int(yA)), 10, colors[0], 1)
                    cv2.line(orig, (xA, yA-15), (xA, yA+15), colors[0], 1)
                    cv2.line(orig, (xA-15, yA), (xA+15, yA), colors[0], 1)
                    cv2.circle(orig, (int(xB), int(yB)), 10, colors[3], 1)
                    cv2.line(orig, (int(xB), int(yB-15)), (int(xB), int(yB+15)), colors[3], 1)
                    cv2.line(orig, (int(xB-15), int(yB)), (int(xB+15), int(yB)), colors[3], 1)

                    Dist = dist.euclidean((xA, yA), (xB, yB)) / self.D
                    Dx = dist.euclidean((xA,0), (xB,0))/self.D
                    if (xA>xB):
                        Dx *= -1
                    Dy = dist.euclidean((0,yA), (0,yB))/self.D
                    if (yA<yB):
                        Dy *= -1
                    dxList[x] = Dx
                    dyList[x] = Dy
                    diList[x] = Dist
        print "Done Analyzing"
        if dxList.ndim != 0 :
            avgDx, stdDx = self.removeOutliersAndAverage(dxList)
            avgDy, stdDy = self.removeOutliersAndAverage(dyList)
            avgDi, stdDi = self.removeOutliersAndAverage(diList)
            cv2.putText(orig, "("+str(self.HomingPosX)+", "+str(self.HomingPosY)+")",(15, 15),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
            cv2.putText(orig, "Dx:{:.3f}, Dy:{:.3f}->Di:{:.3f}mm".format(Dx,Dy,Dist), (15, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
            self.ids.MeasuredImage.update(orig)
            self.HomingX += avgDx#-self.calX
            self.HomingY += avgDy#-self.calY
            print "testing location"
            if doCalibrate!=True:  #its either True because you pressed the calibrate button or its a distance from the measurement callback.
                if ((abs(avgDx)>=0.125) or (abs(avgDy)>=0.125)):
                    print "Adjusting Location"
                    self.HomeIn()
                else:
                    print "Averagedx="+str(avgDx)+", Averagedy="+str(avgDy)
                    print str(self.HomingPosX+15)+", "+str(7-self.HomingPosY)+", "+str(self.HomingX)
                    self.calErrorsX[self.HomingPosX+15][7-self.HomingPosY] = self.HomingX
                    self.calErrorsY[self.HomingPosX+15][7-self.HomingPosY] = self.HomingY
                    self.updateScreenValues()
                    if (self.inAutoMode):
                        self.on_AutoHome()
                    else:
                        print "Done"
            else:
                self.updateScreenValues()
        else:
            popup=Popup(title="Error", content = Label(text="Could not find square"), size_hint=(None,None), size=(400,400))
            popup.open()
