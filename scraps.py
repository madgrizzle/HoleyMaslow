
    def on_MoveandMeasure(self, doCalibrate, _posX, _posY):
        if _posX != None:
            #move to posX, posY.. put in absolute mode
            self.currentX = _posX#+15
            self.currentY = _posY#7-_posY
            print "_posX="+str(_posX)+", _posY="+str(_posY)
            posX = _posX*3.0
            posY = _posY*3.0
            #posX=self.calPositionsX[posX]
            #posY=self.calPositionsY[posY]
            print "posX="+str(posX)+", _posY="+str(posY)
            if posY >= -18 and posY <= 18  and posX >= -42 and posX <= 42:
                print "Moving to:[{}, {}]".format(posX,posY)
                self.data.units = "INCHES"
                self.data.gcode_queue.put("G20 ")
                self.data.gcode_queue.put("G90  ")
                self.data.gcode_queue.put("G0 X"+str(posX)+" Y"+str(posY)+"  ")
                self.data.gcode_queue.put("G91  ")
                if doCalibrate:
                    self.data.measureRequest = self.on_MeasureandCalibrate
                else:
                    self.data.measureRequest = self.on_MeasureOnly
                #request a measurement
                self.data.gcode_queue.put("B10 L")

    def on_AutoMeasure(self):
        self.inAutoMode = True
        if (self.inAutoModeForFirstTime==True):
            self.currentX=-1
            self.currentY=1
            self.inAutoModeForFirstTime=False
        else:
            self.currentX += 1
            if (self.currentX==2):
                self.currentX = -1
                self.currentY -= 1
        if (self.currentY!=-2):
            self.on_MoveandMeasure(False, self.currentX, self.currentY)
        else:
            self.inAutoMode = False

    def on_MeasureandCalibrate(self, dist):
        print "MeasureandCalibrate"
        time.sleep(2)
        self.on_Measure(True)

    def on_MeasureOnly(self, dist):
        print "MeasureOnly"
        timer = time.time()+5
        while time.time()<timer:
            dummy = 5
        self.on_Measure(False)

    def on_Measure(self, doCalibrate):
        print "here at measure"
        self.counter += 1
        dxList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        dyList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        mxList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        myList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        diList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        for x in range(10):
            ret, image = self.ids.KivyCamera.getCapture()
            if ret:
                #cv2.imwrite("image"+str(self.counter)+"-"+str(x)+".png",image)
                #self.counter += 1
                self.ids.MeasuredImage.update(image)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                edged = cv2.Canny(gray, 50, 100)  #50, 100
                edged = cv2.dilate(edged, None, iterations=1)
                edged = cv2.erode(edged, None, iterations=1)
                #cv2.imshow("Canny", edged)
                #cv2.waitKey(0)
                cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if imutils.is_cv2() else cnts[1]
                (cnts, _) = contours.sort_contours(cnts)
                colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0), (255, 0, 255))
                refObj = None
                height, width, channels = image.shape
                xA = int(width/2)
                yA = int(height/2)

                orig = image.copy()
                #orig = edged.copy()
                #orig = cv2.cvtColor(orig, cv2.COLOR_GRAY2BGR)
                #find max contours
                maxArea = 0
                for cTest in cnts:
                    if (cv2.contourArea(cTest)>maxArea):
                        maxArea = cv2.contourArea(cTest)
                        c = cTest
                #make sure contour is large enough
                if cv2.contourArea(c)>100:
                    #approximate to a square (i.e., four contour segments)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 255, 0), 2)
                    c = self.simplifyContour(c)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 0, 0), 2)
                    # compute the rotated bounding box of the contour
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

                    if doCalibrate:
                        (tl, tr, br, bl) = box
                        (tlblX, tlblY) = self.midpoint(tl, bl)
                        (trbrX, trbrY) = self.midpoint(tr, br)

                        self.D = dist.euclidean((tlblX,tlblY),(trbrX,trbrY))/self.markerWidth
                        #self.ids.OpticalCalibrationMeasureButton.disabled = False
                        self.ids.OpticalCalibrationAutoMeasureButton.disabled = False
                        self.ids.OpticalCalibrationDistance.text = "pixels/mm: {:.3f}".format(self.D)
                        self.inAutoModeForFirstTime = True

                    #cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

                    cos = math.cos(angle*3.141592/180.0)
                    sin = math.sin(angle*3.141592/180.0)
                    if (_angle<30):
                        _angle = _angle *-1.0
                    xB,yB = self.translatePoint(xB,yB,xA,yA,_angle)

                    cv2.circle(orig, (int(xA), int(yA)), 10, colors[0], 1)
                    cv2.line(orig, (xA, yA-15), (xA, yA+15), colors[0], 1)
                    cv2.line(orig, (xA-15, yA), (xA+15, yA), colors[0], 1)
                    cv2.circle(orig, (int(xB), int(yB)), 10, colors[3], 1)
                    cv2.line(orig, (int(xB), int(yB-15)), (int(xB), int(yB+15)), colors[3], 1)
                    cv2.line(orig, (int(xB-15), int(yB)), (int(xB+15), int(yB)), colors[3], 1)

                    Dist = dist.euclidean((xA, yA), (xB, yB)) / self.D
                    Dx = dist.euclidean((xA,0), (xB,0))/self.D
                    if (xA>xB):
                        Dx *= -1.0
                    Dy = dist.euclidean((0,yA), (0,yB))/self.D
                    if (yA<yB):
                        Dy *= -1.0
                    (mX, mY) = self.midpoint((xA, yA), (xB, yB))
                    dxList[x] = Dx
                    dyList[x] = Dy
                    mxList[x] = mX
                    myList[x] = mY
                    diList[x] = Dist
                    self.ids.MeasuredImage.update(orig)
        #print "--dxList--"
        #print dxList
        #print "--dyList--"
        #print dyList
        #print "--mxList--"
        #print mxList
        #print "--myList--"
        #print myList

        if dxList.ndim != 0 :
            avgDx, stdDx = self.removeOutliersAndAverage(dxList)
            avgDy, stdDy = self.removeOutliersAndAverage(dyList)
            avgMx, stdMx = self.removeOutliersAndAverage(mxList)
            avgMy, stdMy = self.removeOutliersAndAverage(myList)
            avgDi, stdDi = self.removeOutliersAndAverage(diList)
            print "AvgMx:"+str(avgMx)+", AvgMy:"+str(avgMy)
            print "AvgDx:"+str(avgDx)+", AvgDy:"+str(avgDy)
            print "AvgDi:"+str(avgDi)
            #cv2.putText(orig, "{:.3f}, {:.3f}->{:.3f}, {:.3f}mm".format(avgDx,avgDy,avgDi,stdDi), (int(avgMx-20), int(avgMy - 10)),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
            cv2.putText(orig, "Dx:{:.3f}, Dy:{:.3f}->Di:{:.3f}mm".format(avgDx,avgDy,avgDi), (15, 15),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
            if doCalibrate:
                print "At calX,calY"
                self.calX=avgDx
                self.calY=avgDy
            else:
                self.calErrorsX[self.currentX+15][7-self.currentY] = avgDx#-self.calX
                self.calErrorsY[self.currentX+15][7-self.currentY] = avgDy#-self.calY

            self.ids.OpticalCalibrationDistance.text = "Pixel\mm: {:.3f}\nCal Error({:.3f},{:.3f})\n".format(self.D, self.calX, self.calY)
            self.ids.OpticalCalibrationDistance.text += "[{:.3f},{:.3f}] [{:.3f},{:.3f}] [{:.3f},{:.3f}]\n".format(self.calErrorsX[14][6], self.calErrorsY[14][6], self.calErrorsX[15][6], self.calErrorsY[15][6], self.calErrorsX[16][6], self.calErrorsY[16][6])
            self.ids.OpticalCalibrationDistance.text += "[{:.3f},{:.3f}] [{:.3f},{:.3f}] [{:.3f},{:.3f}]\n".format(self.calErrorsX[14][7], self.calErrorsY[14][7], self.calErrorsX[15][7], self.calErrorsY[15][7], self.calErrorsX[16][7], self.calErrorsY[16][7])
            self.ids.OpticalCalibrationDistance.text += "[{:.3f},{:.3f}] [{:.3f},{:.3f}] [{:.3f},{:.3f}]\n".format(self.calErrorsX[14][8], self.calErrorsY[14][8], self.calErrorsX[15][8], self.calErrorsY[15][8], self.calErrorsX[16][8], self.calErrorsY[16][8])

            print "Updating MeasuredImage"
            #cv2.imshow("Image", orig)
            self.ids.MeasuredImage.update(orig)
            if (self.inAutoMode):
                self.on_AutoMeasure()
        else:
            popup=Popup(title="Error", content = Label(text="Could not find square"), size_hint=(None,None), size=(400,400))
            popup.open()





################################


                Label:
                    text: "Move To:"
                Label:
                Label:
                Button:
                    text: "[-1,+1]"
                    #on_release: root.on_MoveandMeasure(False,-1,1)
                    on_release: root.on_HomeToPos(-1,1)
                Button:
                    text: "[0,+1]"
                    #on_release: root.on_MoveandMeasure(False,0,1)
                    on_release: root.on_HomeToPos(0,1)
                Button:
                    text: "[+1,+1]"
                    #on_release: root.on_MoveandMeasure(False,1,1)
                    on_release: root.on_HomeToPos(1,1)

                Button:
                    text: "[-1,0]"
                    #on_release: root.on_MoveandMeasure(False,-1,0)
                    on_release: root.on_HomeToPos(-1,0)
                Button:
                    text: "[0,0]"
                    #on_release: root.on_MoveandMeasure(False,0,0)
                    on_release: root.on_HomeToPos(0,0)
                Button:
                    text: "[+1,0]"
                    #on_release: root.on_MoveandMeasure(False,1,0)
                    on_release: root.on_HomeToPos(1,0)

                Button:
                    text: "[-1,-1]"
                    #on_release: root.on_MoveandMeasure(False,-1,-1)
                    on_release: root.on_HomeToPos(-1,-1)
                Button:
                    text: "[0,-1]"
                    #on_release: root.on_MoveandMeasure(False,0,-1)
                    on_release: root.on_HomeToPos(0,-1)
                Button:
                    text: "[+1,-1]"
                    #on_release: root.on_MoveandMeasure(False,1,-1)
                    on_release: root.on_HomeToPos(1,-1)


#########################
def on_oldAutoHome(self):

    minX = self.HomingRange*-1
    if (minX<-7):
        minY=7
    else:
        minY=minX*-1
    maxX = self.HomingRange
    maxY = minY * -1

    if self.inAutoMode == False:
        self.HomingX = 0.0
        self.HomingY = 0.0
        self.HomingPosX = 0
        self.HomingPosY = 0
        self.HomingPosX=minX
        self.HomingPosY=minY
        self.inAutoMode = True
    else:
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
