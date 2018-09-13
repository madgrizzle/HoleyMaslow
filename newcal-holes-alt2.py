import math
import random

def CalculateMaximumError(error):
	if (math.fabs(error) < 0.3):
		errorReturn = 0.3*0.3
	else:
		errorReturn = error*error
	return errorReturn

def CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, targetX, targetY, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, oldSag):
	leftMotorDistanceTarget = math.sqrt(math.pow(leftMotorX - targetX,2) + math.pow(leftMotorY - targetY ,2))
	rightMotorDistanceTarget = math.sqrt(math.pow(rightMotorX - targetX,2) + math.pow(rightMotorY - targetY ,2))
	#Calculate the chain angles from horizontal, based on if the chain connects to the sled from the top or bottom of the sprocket
	if chainOverSprocket == 1:
		leftChainAngleTarget = (math.asin((leftMotorY - targetY) / leftMotorDistanceTarget) + math.asin(sprocketRadius/leftMotorDistanceTarget))
		rightChainAngleTarget = (math.asin((rightMotorY - targetY) / rightMotorDistanceTarget) + math.asin(sprocketRadius/rightMotorDistanceTarget))

		leftChainAroundSprocketTarget = sprocketRadius * leftChainAngleTarget
		rightChainAroundSprocketTarget = sprocketRadius * rightChainAngleTarget

	else:
		leftChainAngleTarget = (math.asin((leftMotorY - targetY) / leftMotorDistanceTarget) - math.asin(sprocketRadius/leftMotorDistanceTarget))
		rightChainAngleTarget = (math.asin((rightMotorY - targetY) / rightMotorDistanceTarget) - math.asin(sprocketRadius/rightMotorDistanceTarget))

		leftChainAroundSprocketTarget = sprocketRadius * (3.14159 - leftChainAngleTarget)
		rightChainAroundSprocketTarget = sprocketRadius * (3.14159 - rightChainAngleTarget)

	#Calculate the straight chain length from the sprocket to the bit
	leftChainStraightTarget = math.sqrt(math.pow(leftMotorDistanceTarget,2) - math.pow(sprocketRadius,2))
	rightChainStraightTarget = math.sqrt(math.pow(rightMotorDistanceTarget,2) - math.pow(sprocketRadius,2))

	#Correct the straight chain lengths to account for chain sag
	if (oldSag == False):
		leftChainSag = (1 + ((chainSagCorrection / 1000000000000) * math.pow(math.cos(leftChainAngleTarget),2) * math.pow(leftChainStraightTarget,2) * math.pow((math.tan(rightChainAngleTarget) * math.cos(leftChainAngleTarget)) + math.sin(leftChainAngleTarget),2)))
		rightChainSag = (1 + ((chainSagCorrection / 1000000000000) * math.pow(math.cos(rightChainAngleTarget),2) * math.pow(rightChainStraightTarget,2) * math.pow((math.tan(leftChainAngleTarget) * math.cos(rightChainAngleTarget)) + math.sin(rightChainAngleTarget),2)))
		#Calculate total chain lengths accounting for sprocket geometry and chain sag
		LChainLengthTarget = (leftChainAroundSprocketTarget + leftChainStraightTarget*leftChainSag*leftChainTolerance)-rotationRadius
		RChainLengthTarget = (rightChainAroundSprocketTarget + rightChainStraightTarget*rightChainSag*rightChainTolerance)-rotationRadius
		if (False):
			print "--Original--"
			print "Lchains (straight, sag, delta): "+str(leftChainStraightTarget)+", "+str(leftChainSag*leftChainStraightTarget)+", "+str((leftChainSag*leftChainStraightTarget)-leftChainStraightTarget)
			print "Rchains (straight, sag, delta): "+str(rightChainStraightTarget)+", "+str(rightChainSag*rightChainStraightTarget)+", "+str((rightChainSag*rightChainStraightTarget)-rightChainStraightTarget)
			originalLeftDelta = (leftChainSag*leftChainStraightTarget)-leftChainStraightTarget
			originalRightDelta = (rightChainSag*rightChainStraightTarget)-rightChainStraightTarget
	else:
		leftForce = chainSagCorrection/((targetX-leftMotorX)/(leftMotorY-targetY)+(rightMotorX-targetX)/(rightMotorY-targetY))*math.sqrt(math.pow(((rightMotorX-targetX)/(rightMotorY-targetY)),2)*math.pow(((targetX-leftMotorX)/(leftMotorY-targetY)),2)+math.pow(((rightMotorX-targetX)/(rightMotorY-targetY)),2))
		rightForce =chainSagCorrection/((targetX-leftMotorX)/(leftMotorY-targetY)+(rightMotorX-targetX)/(rightMotorY-targetY))*math.sqrt(math.pow(((rightMotorX-targetX)/(rightMotorY-targetY)),2)*math.pow(((targetX-leftMotorX)/(leftMotorY-targetY)),2)+math.pow(((targetX-leftMotorX)/(leftMotorY-targetY)),2))
		hl = math.cos(leftChainAngleTarget)*leftChainStraightTarget*0.00328084
		hr = math.cos(rightChainAngleTarget)*rightChainStraightTarget*0.00328084
		vl = math.sin(leftChainAngleTarget)*leftChainStraightTarget*0.00328084
		vr = math.sin(rightChainAngleTarget)*rightChainStraightTarget*0.00328084
		al = math.cos(leftChainAngleTarget)*leftForce/(0.09)
		ar = math.cos(rightChainAngleTarget)*rightForce/(0.09)
		leftChainSag = math.sqrt( math.pow((2*al*math.sinh(hl/(2*al))),2)+vl*vl)/0.00328084
		rightChainSag = math.sqrt( math.pow((2*ar*math.sinh(hr/(2*ar))),2)+vr*vr)/0.00328084
		LChainLengthTarget = (leftChainAroundSprocketTarget + leftChainSag*leftChainTolerance)-rotationRadius
		RChainLengthTarget = (rightChainAroundSprocketTarget + rightChainSag*rightChainTolerance)-rotationRadius

		if (False):
			print "--New--"
			print "MotorSeparation: "+str(rightMotorX-leftMotorX)
			print "MotorHeight: "+str(leftMotorY)
			print "chainSag: "+str(chainSagCorrection)
			print "targetX,Y: "+str(targetX)+", "+str(targetY)
			print "chainStraightL,R: "+str(leftChainStraightTarget)+", "+str(rightChainStraightTarget)
			print "ForcesL,R: "+str(leftForce)+", "+str(rightForce)
			print "anglesL,R: "+str(leftChainAngleTarget*180.0/3.141592)+", "+str(rightChainAngleTarget*180.0/3.141592)
			print "hl, hr: "+str(hl)+", "+str(hr)
			print "vl, vr: "+str(vl)+", "+str(vr)
			print "al, ar: "+str(al)+", "+str(ar)
			print "Lchains (straight, sag, delta): "+str(leftChainStraightTarget)+", "+str(leftChainSag)+", "+str(leftChainSag-leftChainStraightTarget)
			print "Rchains (straight, sag, delta): "+str(rightChainStraightTarget)+", "+str(rightChainSag)+", "+str(rightChainSag-rightChainStraightTarget)
			print "%DifferenceL,R: "+str(((leftChainSag-leftChainStraightTarget)-originalLeftDelta)/originalLeftDelta*100.0)+"%, "+str(((rightChainSag-rightChainStraightTarget)-originalRightDelta)/originalRightDelta*100.0)+"%"
			print "finals: "+str(LChainLengthTarget)+", "+str(RChainLengthTarget)
			x=raw_input()
	return LChainLengthTarget, RChainLengthTarget

def CalculateCoordinates(dH0H1, dH0H2, dH0H3, dH0H4, dH1H2, dH1H4, dH2H3, dH3H4, dH0M5, dH2M5 ):
	#Calculate x,y coordinates for each hole
	H0x = 0
	H0y = 0
	M5x = 0
	M5y = dH0M5
	H2y = (dH0M5*dH0M5+dH0H2*dH0H2-dH2M5*dH2M5)/(2*dH0M5)*-1.0
	H2x = math.sqrt( (dH0M5+dH0H2+dH2M5) * (dH0M5+dH0H2-dH2M5) * (dH0M5-dH0H2+dH2M5) * (-dH0M5+dH0H2+dH2M5) )/(2*dH0M5)*-1.0
	#print "H2x:"+str(H2x)+", H2y:"+str(H2y)

	H3y = (dH0M5*dH0M5+dH0H3*dH0H3-(dH2H3-dH2M5)*(dH2H3-dH2M5))/(2*dH0M5)*-1.0
	H3x = math.sqrt( (dH0M5+dH0H3+(dH2H3-dH2M5)) * (dH0M5+dH0H3-(dH2H3-dH2M5)) * (dH0M5-dH0H3+(dH2H3-dH2M5)) * (-dH0M5+dH0H3+(dH2H3-dH2M5)) )/(2*dH0M5)
	#print "H3x:"+str(H3x)+", H3y:"+str(H3y)

	theta = math.atan2(H3y,H3x*-1.0)
	#print "Theta:"+str(theta)
	rH4x = (dH0H3*dH0H3-dH3H4*dH3H4+dH0H4*dH0H4)/(2*dH0H3)
	rH4y = math.sqrt( (dH0H3+dH3H4+dH0H4) * (dH0H3+dH3H4-dH0H4) *(dH0H3-dH3H4+dH0H4) * (-dH0H3+dH3H4+dH0H4) )/(2*dH0H3)
	#print "rH4x:"+str(rH4x)+", rH4y:"+str(rH4y)

	H4x = ((rH4x*math.cos(-theta))-(rH4y*math.sin(-theta)))*-1.0
	H4y = ((rH4x*math.sin(-theta))+(rH4y*math.cos(-theta)))*-1.0
	#print "H4x:"+str(H4x)+", H4y:"+str(H4y)
	# Calculate the actual chain lengths for each cut location

	theta = math.atan2(H2y,H2x)
	#print "Theta:"+str(theta)
	rH1x = (dH0H2*dH0H2-dH1H2*dH1H2+dH0H1*dH0H1)/(2*dH0H2)
	rH1y = math.sqrt( (dH0H2+dH1H2+dH0H1) * (dH0H2+dH1H2-dH0H1) *(dH0H2-dH1H2+dH0H1) * (-dH0H2+dH1H2+dH0H1) )/(2*dH0H2)
	#print "rH1x:"+str(rH1x)+", rH1y:"+str(rH1y)

	H1x = ((rH1x*math.cos(-theta))-(rH1y*math.sin(-theta)))
	H1y = ((rH1x*math.sin(-theta))+(rH1y*math.cos(-theta)))*-1.0
	return H0x, H0y, H1x, H1y, H2x, H2y, H3x, H3y, H4x, H4y

def IterateCoordinates(_dH0H1, _dH0H2, _dH0H3, _dH0H4, _dH1H2, _dH1H4, _dH2H3, _dH3H4, _dH0M5, _dH2M5 ):
	errorMagnitude = 999999.0
	previousErrorMagnitude = 9999999.0
	errorImprovementInterval = 0.0
	previousdH0M5 = _dH0M5
	previousdH2M5 = _dH2M5
	direction = 1.0
	noImprovementCounter = 0
	while (math.fabs(errorMagnitude) > 0.1 and noImprovementCounter<1000):
		adjustValue = random.randint(1,2)
		randValue = random.randint(0,1)
		if (randValue == 0):
			direction = -1.0;
		else:
			direction = 1.0;
		if (errorImprovementInterval == -99999):
			_dH0M5 += 436
		else:
			_dH0M5 += errorImprovementInterval*direction
			#if (adjustValue == 1):
			#	_dH0M5 += errorImprovementInterval*direction
			#else:
			#	_dH2M5 += 0.01*direction
		try:
			#print str(dH0M5)
			#print str(_dH0M5)+", "+str(_dH2M5)
			#x=raw_input()
			_H0x, _H0y, _H1x, _H1y, _H2x, _H2y, _H3x, _H3y, _H4x, _H4y = CalculateCoordinates(_dH0H1, _dH0H2, _dH0H3, _dH0H4, _dH1H2, _dH1H4, _dH2H3, _dH3H4, _dH0M5, _dH2M5)

		except:
			errorImprovementInterval = -99999
			#x=raw_input()
		else:
			dH1H4errorMagnitude = _dH1H4 - math.sqrt( math.pow(_H1x-_H4x,2)+math.pow(_H1y-_H4y,2))
			dH2H3errorMagnitude = _dH2H3 - math.sqrt( math.pow(_H2x-_H3x,2)+math.pow(_H2y-_H3y,2))
			#dH0H1errorMagnitude = _dH0H1 - math.sqrt( math.pow(_H0x-_H1x,2)+math.pow(_H0y-_H1y,2))
			errorMagnitude = math.sqrt(dH1H4errorMagnitude*dH1H4errorMagnitude+dH2H3errorMagnitude*dH2H3errorMagnitude)#+dH0H1errorMagnitude*dH0H1errorMagnitude)
			#print str(previousErrorMagnitude)+", "+str(errorMagnitude)+", "+str(dH0M5)
			print str(previousErrorMagnitude)+", "+str(errorMagnitude)+", "+str(_dH0M5)+", "+str(_dH2M5)+", "+str(dH1H4errorMagnitude)+", "+str(dH2H3errorMagnitude)#+", "+str(dH0H1errorMagnitude)
			#x=raw_input()
			if (errorMagnitude>previousErrorMagnitude):
				_dH0M5 = previousdH0M5
				_dH2M5 = previousdH2M5
				noImprovementCounter += 1
			else:
				#print str(previousErrorMagnitude)+", "+str(errorMagnitude)+", "+str(_dH0M5)+", "+str(_dH2M5)+", "+str(dH1H4errorMagnitude)+", "+str(dH2H3errorMagnitude)
				previousErrorMagnitude = errorMagnitude
				errorImprovementInterval = errorMagnitude*0.1
				previousdH0M5 = _dH0M5
				previousdH2M5 = _dH2M5
				noImprovementCounter = 0
				#x=raw_input()
	return _H0x, _H0y, _H1x, _H1y, _H2x, _H2y, _H3x, _H3y, _H4x, _H4y


###Start of Process###

# adjust based upon machine settings
workspaceHeight = 1219.2
workspaceWidth = 2438.4
gearTeeth = 10
chainPitch = 6.35
holePattern = 0 # 0 = wide holes, 1 = 12-foot holes   3=both sets of holes
# adjust in the event the hole pattern is changed
if (holePattern == 0):
	aH1x = (workspaceWidth/2.0-254.0)*-1.0
	aH1y = (workspaceHeight/2.0-254.0)
	aH2x = aH1x
	aH2y = aH1y*-1.0
	aH3x = aH1x*-1.0
	aH3y = aH2y
	aH4x = aH3x
	aH4y = aH1y
if (holePattern == 1):
	aH1x = -304.8
	aH1y = 304.8
	aH2x = aH1x
	aH2y = aH1y*-1.0
	aH3x = aH1x*-1.0
	aH3y = aH2y
	aH4x = aH3x
	aH4y = aH1y
if (holePattern == 3):
	aH1x = (workspaceWidth/2.0-254.0)*-1.0
	aH1y = (workspaceHeight/2.0-254.0)
	aH2x = aH1x
	aH2y = aH1y*-1.0
	aH3x = aH1x*-1.0
	aH3y = aH2y
	aH4x = aH3x
	aH4y = aH1y
	aH5x = -304.8
	aH5y = 304.8
	aH6x = aH5x
	aH6y = aH5y*-1.0
	aH7x = aH5x*-1.0
	aH7y = aH6y
	aH8x = aH7x
	aH8y = aH5y

if (holePattern == 0):
	aX = workspaceWidth/2.0-254
	aY = workspaceHeight/2.0-254.0
	aHx = [0.0, aX*-1.0, aX*-1.0 , aX, aX]
	aHy = [0.0, aY, aY*-1.0, aY*-1.0, aY]
if (holePattern == 1):
	aX = 304.8
	aY = 304.8
	aHx = [0.0, aX*-1.0, aX*-1.0 , aX, aX]
	aHy = [0.0, aY, aY*-1.0, aY*-1.0, aY]
if (holePattern == 3):
	aX = workspaceWidth/2.0-254
	aY = workspaceHeight/2.0-254.0
	aX5 = 304.8
	aY5 = 304.8
	aHx = [0.0, aX*-1.0, aX*-1.0 , aX, aX, aX5*-1.0, aX5*-1.0 , aX5, aX5]
	aHy = [0.0, aY, aY*-1.0, aY*-1.0, aY, aY5, aY5*-1.0, aY5*-1.0, aY5]

#measured distances of hole pattern
##---CHANGE THESE TO WHAT YOU MEASURED---##
##---USE MILLIMETERS ONLY---##
##---My tape measure was off by 101 mm so the -101.0 adjust for it---##
##---CHANGE IT BECAUSE YOURS IS LIKELY DIFFERENT---###
sensitivity = 1.0
dH0H1 = 1070.0-40.0
dH0H2 = 1071.5-40.0
dH0H3 = 1070.0-40.0
dH0H4 = 1070.0-40.0
dH1H2 = 752.0-40.0
dH1H4 = 1975.0-40.0
dH2H3 = 1974.5-40.0
dH3H4 = 751.0-40.0
dH0M5 = 1.0 #356.192 #1.0
#dH2M5 = 1004.75 - 40.0 - sensitivity#1004.75-40.0
dH2M5 = 968.0 #dH2H3 / 2.0

dH0H5 = 469.0-40.0
dH0H6 = 471.5-40.0
dH0H7 = 470.5-40.0
dH0H8 = 470.0-40.0
dH5H6 = 647.0-40.0
dH5H8 = 651.0-40.0
dH6H7 = 650.0-40.0
dH7H8 = 647.5-40.0
dH0M9 = 1.0#100.0-40.0 #350.0-40.0
#dH6M9 = 342.75-40.0 + sensitivity#342.75-40.0
dH6M9 = dH6H7 / 2.0

if (holePattern==1):
	dH0H1 = dH0H5
	dH0H2 = dH0H6
	dH0H3 = dH0H7
	dH0H4 = dH0H8
	dH1H2 = dH5H6
	dH1H4 = dH5H8
	dH2H3 = dH6H7
	dH3H4 = dH7H8
	dH0M5 = dH0M9
	dH2M5 = dH6M9

#optimization parameters.. this really does affect how well you can arrive at a solution and how good of a solution it is
acceptableTolerance = .05
numberOfIterations = 10000000  # reduced number of iterations
motorYcoordCorrectionScale = 0.01
motorXcoordCorrectionScale = 0.05
chainSagCorrectionCorrectionScale = 0.01
motorSpacingCorrectionScale = 0.001
rotationRadiusCorrectionScale = 0.01
chainCompensationCorrectionScale = 0.001

#optional adjustments
adjustMotorYcoord = True  # this allows raising lowering of top beam
adjustMotorTilt = True  # this allows tilting of top beam
adjustMotorXcoord = True  # this allows shifting of top beam
adjustMotorSpacingInterval = 1 #0 means never, 1 means always, 100 means every 100 times there's no improvement
adjustRotationalRadiusInterval = 1 #0 means never, 1 means always, 100 means every 100 times there's no improvement
adjustChainCompensationInterval = 1 #0 means never, 1 means always, 100 means every 100 times there's no improvement
adjustChainSagInterval = 1
NewChainSag = True
#parameters used during calibration cut.. currently assumes motors are level and 0,0 is centered
##---CHANGE THESE TO MATCH YOUR MACHINE WHEN YOU RAN THE HOLE PATTERN---##
motorSpacing = 3581.481
desiredMotorSpacing = motorSpacing #this allows you to change from motor spacing you cut with and make it a fixed value
motorYoffset = 478.26
motorTilt = 0
rotationRadius = 132.75
chainSagCorrection = 30.0
chainOverSprocket = 1
leftChainTolerance = 1.0-(0.0/100.0) # can't use current values .. value must be less than or equal to 1
rightChainTolerance =1.0-(0.0/100.0) # can't use current values .. value must be less than or equal to 1
desiredRotationalRadius = 132.75 #rotationRadius #this allows you to change from rotation radius you cut with and make it a fixed value

deltaChainTolerance = rightChainTolerance-leftChainTolerance
print str(deltaChainTolerance)
dH6M9 *= (1+deltaChainTolerance)
dH2M5 *= (1+deltaChainTolerance)
print str(dH2M5)+", "+str(dH2M5*(1+deltaChainTolerance))
print str(dH6M9)+", "+str(dH6M9*(1+deltaChainTolerance))
x=raw_input("press enter") #pause for review
# Gather current machine parameters
sprocketRadius = (gearTeeth*chainPitch / 2.0 / 3.14159) # + chainPitch/math.sin(3.14159 / gearTeeth)/2.0)/2.0 # new way to calculate.. needs validation
leftMotorX = math.cos(motorTilt*3.141592/180.0)*motorSpacing/-2.0
leftMotorY = math.sin(motorTilt*3.141592/180.0)*motorSpacing/-2.0 + motorYoffset+workspaceHeight/2.0
rightMotorX = math.cos(motorTilt*3.141592/180.0)*motorSpacing+leftMotorX
rightMotorY = math.sin(motorTilt*3.141592/180.0)*motorSpacing/2.0 + motorYoffset +workspaceHeight/2.0

leftMotorXEst = desiredMotorSpacing/-2.0#leftMotorX-(desiredMotorSpacing-motorSpacing)/2.0 #adjusts motor x based upon change in motor spacing
leftMotorYEst = leftMotorY+(rightMotorY-leftMotorY)/2.0
rightMotorXEst = desiredMotorSpacing/2.0#rightMotorX+(desiredMotorSpacing-motorSpacing)/2.0
rightMotorYEst = rightMotorY-(rightMotorY-leftMotorY)/2.0#rightMotorY
leftChainToleranceEst = 1.0#leftChainTolerance
rightChainToleranceEst = 1.0#rightChainTolerance
rotationRadiusEst = desiredRotationalRadius  # Not affected by chain compensation
chainSagCorrectionEst= 25.62#chainSagCorrection

iterativeSolvedH0M5= False

#calculate coordinates of the holes based upon distance measurements
if (iterativeSolvedH0M5):
	H0x, H0y, H1x, H1y, H2x, H2y, H3x, H3y, H4x, H4y = IterateCoordinates(dH0H1, dH0H2, dH0H3, dH0H4, dH1H2, dH1H4, dH2H3, dH3H4, dH0M5, dH2M5)
	if (holePattern == 3):
		H0x, H0y, H5x, H5y, H6x, H6y, H7x, H7y, H8x, H8y = IterateCoordinates(dH0H5, dH0H6, dH0H7, dH0H8, dH5H6, dH5H8, dH6H7, dH7H8, dH0M9, dH6M9)
	if (holePattern != 3):
		Hx = [H0x, H1x, H2x, H3x, H4x]
		Hy = [H0y, H1y, H2y, H3y, H4y]
	else:
		Hx = [H0x, H1x, H2x, H3x, H4x, H5x, H6x, H7x, H8x]
		Hy = [H0y, H1y, H2y, H3y, H4y, H5y, H6y, H7y, H8y]

else:
	H0x, H0y, H1x, H1y, H2x, H2y, H3x, H3y, H4x, H4y = CalculateCoordinates(dH0H1, dH0H2, dH0H3, dH0H4, dH1H2, dH1H4, dH2H3, dH3H4, dH0M5, dH2M5)
	if (holePattern == 3):
		H0x, H0y, H5x, H5y, H6x, H6y, H7x, H7y, H8x, H8y = CalculateCoordinates(dH0H5, dH0H6, dH0H7, dH0H8, dH5H6, dH5H8, dH6H7, dH7H8, dH0M9, dH6M9)
	if (holePattern != 3):
		Hx = [H0x, H1x, H2x, H3x, H4x]
		Hy = [H0y, H1y, H2y, H3y, H4y]
	else:
		Hx = [H0x, H1x, H2x, H3x, H4x, H5x, H6x, H7x, H8x]
		Hy = [H0y, H1y, H2y, H3y, H4y, H5y, H6y, H7y, H8y]

holeCount = len(aHx)
print "Desired:"
for x in range(holeCount):
	print "aHx["+str(x)+"]:"+str(aHx[x])+", aHy["+str(x)+"]:"+str(aHy[x])
print "Actual:"
for x in range(len(Hx)):
	print "Hx["+str(x)+"]:"+str(Hx[x])+", Hy["+str(x)+"]:"+str(Hy[x])
print "Delta:"
for x in range(len(Hx)):
	print "Hx["+str(x)+"]:"+str(aHx[x]-Hx[x])+", Hy["+str(x)+"]:"+str(aHy[x]-Hy[x])

print "H1 to H4 Slope: "+str(math.atan((Hy[4]-Hy[1])/(Hx[4]-Hx[1]))*180.0/3.141592)
print "H2 to H3 Slope: "+str(math.atan((Hy[3]-Hy[2])/(Hx[3]-Hx[2]))*180.0/3.141592)
if (holePattern == 3):
	print "H5 to H8 Slope: "+str(math.atan((Hy[8]-Hy[5])/(Hx[8]-Hx[5]))*180.0/3.141592)
	print "H6 to H7 Slope: "+str(math.atan((Hy[7]-Hy[6])/(Hx[7]-Hx[6]))*180.0/3.141592)

print "H1 to H2 Slope: "+str(math.atan((Hy[2]-Hy[1])/(Hx[2]-Hx[1]))*180.0/3.141592)
print "H4 to H3 Slope: "+str(math.atan((Hy[3]-Hy[4])/(Hx[3]-Hx[4]))*180.0/3.141592)
if (holePattern == 3):
	print "H5 to H6 Slope: "+str(math.atan((Hy[6]-Hy[5])/(Hx[6]-Hx[5]))*180.0/3.141592)
	print "H7 to H8 Slope: "+str(math.atan((Hy[7]-Hy[8])/(Hx[7]-Hx[8]))*180.0/3.141592)

print "dH1H4: "+str(math.sqrt(math.pow(Hx[4]-Hx[1],2)+math.pow(Hy[4]-Hy[1],2)))+", Error: "+str(dH1H4-(math.sqrt(math.pow(Hx[4]-Hx[1],2)+math.pow(Hy[4]-Hy[1],2))))
print "dH2H3: "+str(math.sqrt(math.pow(Hx[3]-Hx[2],2)+math.pow(Hy[3]-Hy[2],2)))+", Error: "+str(dH2H3-(math.sqrt(math.pow(Hx[3]-Hx[2],2)+math.pow(Hy[3]-Hy[2],2))))
if (holePattern == 3):
	print "dH5H8: "+str(math.sqrt(math.pow(Hx[5]-Hx[8],2)+math.pow(Hy[5]-Hy[8],2)))+", Error: "+str(dH5H8-(math.sqrt(math.pow(Hx[5]-Hx[8],2)+math.pow(Hy[5]-Hy[8],2))))
	print "dH6H7: "+str(math.sqrt(math.pow(Hx[6]-Hx[7],2)+math.pow(Hy[6]-Hy[7],2)))+", Error: "+str(dH6H7-(math.sqrt(math.pow(Hx[6]-Hx[7],2)+math.pow(Hy[6]-Hy[7],2))))


x=raw_input("press enter") #pause for review #pause for review

# Calculate the chain lengths for each hole location based upon inputted model
LChainLengthHole = []
RChainLengthHole = []

for x in range(holeCount):
	LH, RH = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aHx[x], aHy[x], chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False)
	LChainLengthHole.insert(x,LH)
	RChainLengthHole.insert(x,RH)

print "Machine parameters:"
print "Rotation Disk Radius: " + str(rotationRadius) + ", Chain Sag Correction Value: " + str(chainSagCorrection)
print "leftMotorX: "+str(leftMotorX) + ", leftMotorY: "+str(leftMotorY)+", rightMotorX: "+str(rightMotorX)+", rightMotorY:"+str(rightMotorY)
for x in range(len(RChainLengthHole)):
	print "LHole"+str(x)+": "+str(LChainLengthHole[x])+", RHole1"+str(x)+": "+str(RChainLengthHole[x])

x=raw_input("press enter") #pause for review

LChainErrorHole = []
RChainErrorHole = []
LChainLengthHoleEst = []
RChainLengthHoleEst = []
bestLChainErrorHole = []
bestRChainErrorHole = []
for x in range(holeCount):
	LChainErrorHole.insert(x,0.0)
	RChainErrorHole.insert(x,0.0)
	LChainLengthHoleEst.insert(x,0.0)
	RChainLengthHoleEst.insert(x,0.0)
	bestLChainErrorHole.insert(x,99999999.9)
	bestRChainErrorHole.insert(x,99999999.9)

previousErrorMagnitude = 99999999999999.9
bestErrorMagnitude = 99999999.9
reportCounter = 0
noImprovementCounter = 0
scaleMultiplierCounter = 1.0
adjustMotorSpacingCounter = 0
adjustRotationalRadiusCounter = 0
adjustChainCompensationCounter = 0
adjustChainSagCounter = 0
adjustMotorSpacing = False # just initializing these variables
adjustRotationalRadius = False # just initializing these variables
adjustChainCompensation = False # just initializing these variables
adjustChainSag = False # just initializing these variables
scaleMultiplier = 1.0
n = 0
print "Iterating for new machine parameters"

# Iterate until error tolerance is achieved or maximum number of iterations occurs
errorMagnitude = 999999.9
previousErrorMagnitude = 9999999.9
bestErrorMagnitude = 9999999.9
while(errorMagnitude > acceptableTolerance and n < numberOfIterations):
	n += 1
	# calculate chain lengths based upon estimated parameters and actual hole locations
	errorMagnitude = 0.0
	for x in range(holeCount):
		LCEst, RCEst = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, Hx[x], Hy[x], chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, NewChainSag)
		LChainLengthHoleEst[x]=LCEst
		RChainLengthHoleEst[x]=RCEst
		LChainErrorHole[x]=LChainLengthHoleEst[x]-LChainLengthHole[x]
		RChainErrorHole[x]=RChainLengthHoleEst[x]-RChainLengthHole[x]
		if (x!=0):
			errorMagnitude += CalculateMaximumError(LChainErrorHole[x])
			errorMagnitude += CalculateMaximumError(RChainErrorHole[x])

	errorMagnitude = math.sqrt(errorMagnitude/float(holeCount-1))

	if (errorMagnitude >= previousErrorMagnitude):
		errorMagnitude = previousErrorMagnitude
		leftMotorXEst = previousleftMotorXEst
		leftMotorYEst = previousleftMotorYEst
		rightMotorXEst = previousrightMotorXEst
		rightMotorYEst = previousrightMotorYEst
		rotationRadiusEst = previousrotationRadiusEst
		chainSagCorrectionEst = previouschainSagCorrectionEst
		leftChainToleranceEst = previousleftChainToleranceEst
		rightChainToleranceEst = previousrightChainToleranceEst
		adjustMotorSpacingCounter +=1
		if (adjustMotorSpacingCounter == adjustMotorSpacingInterval):
			adjustMotorSpacingCounter = 0
			adjustMotorSpacing = True
		adjustRotationalRadiusCounter +=1
		if (adjustRotationalRadiusCounter == adjustRotationalRadiusInterval):
			adjustRotationalRadiusCounter = 0
			adjustRotationalRadius = True
		adjustChainCompensationCounter +=1
		if (adjustChainCompensationCounter == adjustChainCompensationInterval):
			adjustChainCompensationCounter = 0
			adjustChainCompensation = True
		adjustChainSagCounter +=1
		#print str(adjustChainSagCounter)
		if (adjustChainSagCounter == adjustChainSagInterval):
			#print "here"
			adjustChainSagCounter = 0
			adjustChainSag = True
		if (noImprovementCounter == 10000):
			if (scaleMultiplierCounter == 10):
				scaleMultlipler = 100.0
				scaleMultiplierCounter = 0
			else:
				scaleMultiplier = 10.0
				scaleMultiplierCounter += 1.0
			previousErrorMagnitude = 99999999
			noImprovementCounter = 0
		else:
			noImprovementCounter += 1
			scaleMultiplier = 1.0
	else:
		adjustMotorSpacingCounter = 0
		adjustRotationalRadiusCounter = 0
		adjustChainCompensationCounter = 0
		previousErrorMagnitude = errorMagnitude
		previousrotationRadiusEst = rotationRadiusEst
		previouschainSagCorrectionEst = chainSagCorrectionEst
		previousleftChainToleranceEst = leftChainToleranceEst
		previousrightChainToleranceEst = rightChainToleranceEst
		previousleftMotorXEst = leftMotorXEst
		previousleftMotorYEst = leftMotorYEst
		previousrightMotorXEst = rightMotorXEst
		previousrightMotorYEst = rightMotorYEst
		if (errorMagnitude < bestErrorMagnitude):
			bestErrorMagnitude = errorMagnitude
			bestrotationRadiusEst = rotationRadiusEst
			bestchainSagCorrectionEst = chainSagCorrectionEst
			bestleftChainToleranceEst = leftChainToleranceEst
			bestrightChainToleranceEst = rightChainToleranceEst
			bestleftMotorXEst = leftMotorXEst
			bestleftMotorYEst = leftMotorYEst
			bestrightMotorXEst = rightMotorXEst
			bestrightMotorYEst = rightMotorYEst
			for x in range(holeCount):
				bestLChainErrorHole[x] = LChainErrorHole[x]
				bestRChainErrorHole[x] = RChainErrorHole[x]

			#report better findings
			reportCounter += 1
			if (reportCounter == 1):
				reportCounter = 0
				distBetweenMotors = math.sqrt( math.pow(bestleftMotorXEst-bestrightMotorXEst,2)+math.pow(bestleftMotorYEst-bestrightMotorYEst,2))
				motorTilt = math.atan((bestrightMotorYEst-bestleftMotorYEst)/(bestrightMotorXEst-bestleftMotorXEst))*180.0/3.141592
				print "---------------------------------------------------------------------------------------------"
				print "Best so far at N: " + str(n) + ", Error Magnitude: " + str(round(bestErrorMagnitude, 3))
				print "Motor Spacing: "+str(distBetweenMotors) + ", Motor Elevation: "+str(((bestleftMotorYEst+(bestrightMotorYEst-bestleftMotorYEst)/2.0))-workspaceHeight/2.0)+", Top Beam Tilt: "+str(motorTilt) +" degrees"
				tleftMotorX = math.cos(motorTilt*3.141592/180.0)*distBetweenMotors/-2.0 + (bestrightMotorXEst+bestleftMotorXEst)/2.0
				tleftMotorY = math.sin(motorTilt*3.141592/180.0)*distBetweenMotors/-2.0 + bestleftMotorYEst + (bestrightMotorYEst-bestleftMotorYEst)/2.0
				trightMotorX = math.cos(motorTilt*3.141592/180.0)*distBetweenMotors+tleftMotorX
				trightMotorY = math.sin(motorTilt*3.141592/180.0)*distBetweenMotors/2.0 + bestleftMotorYEst + (bestrightMotorYEst-bestleftMotorYEst)/2.0
				print "tleftMotorX: "+str(tleftMotorX) + ", tleftMotorY: "+str(tleftMotorY)
				print "trightMotorX: "+str(trightMotorX)+", trightMotorY:"+str(trightMotorY)
				print "tmotorspacing: "+str(math.sqrt( math.pow(tleftMotorX-trightMotorX,2)+math.pow(tleftMotorY-trightMotorY,2)))

				print "Rotation Disk Radius: " + str(round(bestrotationRadiusEst, 3)) + ", Chain Sag Correction Value: " + str((bestchainSagCorrectionEst)) + ", Left Chain:"+str(((1.0-bestleftChainToleranceEst)*100))+", Right Chain:"+str(((1.0-bestrightChainToleranceEst)*100))
				print "leftMotorX: "+str(bestleftMotorXEst) + ", leftMotorY: "+str(bestleftMotorYEst)
				print "rightMotorX: "+str(bestrightMotorXEst)+", rightMotorY:"+str(bestrightMotorYEst)
				for x in range(holeCount):
					print "  LChain Error Hole "+str(x)+": " + str(round(bestLChainErrorHole[x],4)) + "\t RChain Error Hole "+str(x)+": " + str(round(bestRChainErrorHole[x],4)) + "\t RMS Error Hole "+str(x)+": " +str(round(math.sqrt(math.pow(bestLChainErrorHole[x],2)+math.pow(bestRChainErrorHole[x],2)),4))
				#x = raw_input("")

	#pick a random variable to adjust
	#direction = random.randint(0,1)  # determine if its an increase or decrease
	adjustValue = random.randint(-100, 100)
	Completed = False # trick value to enter while
	while (Completed == False):
		picked = random.randint(1,6)
		tscaleMultiplier = scaleMultiplier * float(adjustValue)/100.0 #avoid altering scaleMultiplier
		if (picked == 1):
			motor = random.randint(0,3) #pick which motor (or both) to adjust
			if (motor == 0 and adjustMotorTilt): #tilt left motor up or down
				leftMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				# because left motor moved, change x coordinate of right motor to keep distance between motors fixed
				rightMotorXEst = leftMotorXEst + math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((leftMotorYEst-rightMotorYEst),2))
				Completed = True
				#print "1 "+str(leftMotorXEst)+", "+str(rightMotorXEst)+", "+str(desiredMotorSpacing)
			if (motor == 1 and adjustMotorTilt ): #tilt right motor up or down
				rightMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				# because right motor mover, change x coordinate of left motor to keep distance between motors fixed
				leftMotorXEst = rightMotorXEst - math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((rightMotorYEst-leftMotorYEst),2))
				Completed = True
				#print "2"+str(leftMotorXEst)+", "+str(rightMotorXEst)+", "+str(desiredMotorSpacing)
			if (motor ==2 and adjustMotorYcoord): # moves both motors up or down in unison
				leftMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				rightMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				Completed = True
				#print "3"
			if (motor ==3 and adjustMotorSpacing):
				desiredMotorSpacing += motorSpacingCorrectionScale*tscaleMultiplier
				adjustMotorSpacing=False
				motor = random.randint(0,1)
				if (motor == 0):
					leftMotorXEst = rightMotorXEst - math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((rightMotorYEst-leftMotorYEst),2))
				else:
					rightMotorXEst = leftMotorXEst + math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((leftMotorYEst-rightMotorYEst),2))
				Completed = True
		if (picked == 2 and adjustMotorXcoord): #all x moves are in unison to keep distance between motors fixed
			leftMotorXEst += errorMagnitude*motorXcoordCorrectionScale*tscaleMultiplier
			rightMotorXEst += errorMagnitude*motorXcoordCorrectionScale*tscaleMultiplier
			Completed = True
			#print "6"
		if (picked == 3 and adjustChainSag):
			chainSagCorrectionEst += errorMagnitude*chainSagCorrectionCorrectionScale*tscaleMultiplier
			#if (chainSagCorrectionEst < 20):
			#	chainSagCorrectionEst = 25.0
			#if (chainSagCorrectionEst > 30):
			#	chainSagCorrectionEst = 25.0
			Completed = True
			adjustChainSag = False
			#print "7"
		if (picked == 4 and adjustRotationalRadius): #recommend against this one if at all possible
			rotationRadiusEst -= errorMagnitude*rotationRadiusCorrectionScale*tscaleMultiplier
			adjustRotationalRadius = False
			Completed = True
			#print "8"
		if (picked == 5 and adjustChainCompensation):
			leftChainToleranceEst += errorMagnitude*chainCompensationCorrectionScale*tscaleMultiplier
			#rotationRadiusEst -= errorMagnitude*rotationRadiusCorrectionScale*tscaleMultiplier
			#make sure chain tolerance doesn't go over 1 (i.e., chain is shorter than should be.. this can cause optimization to go bonkers)
			if (leftChainToleranceEst>= 1.0):
				leftChainToleranceEst = 1.0
			if (leftChainToleranceEst<0.9):
				leftChainToleranceEst = 0.9
			adjustChainCompensation = False
			Completed = True
			#print "9"
		if (picked == 6 and adjustChainCompensation):
			rightChainToleranceEst += errorMagnitude*chainCompensationCorrectionScale*tscaleMultiplier
			#rotationRadiusEst -= errorMagnitude*rotationRadiusCorrectionScale*tscaleMultiplier #counteract chain tolerance some
			#make sure chain tolerance doesn't go over 1 (i.e., chain is shorter than should be.. this can cause optimization to go bonkers)
			if (rightChainToleranceEst>= 1.0):
				rightChainToleranceEst = 1.0
			if (rightChainToleranceEst<0.9):
				rightChainToleranceEst = 0.9
			adjustChainCompensation = False
			Completed = True
			#print "10"

	#make sure values aren't too far out of whack.
	if (False): # will never be run if False
		if (rotationRadiusEst<desiredRotationalRadius-2):
			rotationRadiusEst = desiredRotationalRadius-2
		if (rotationRadiusEst>desiredRotationalRadius+2):
			rotationRadiusEst = desiredRotationalRadius+2
		if (chainSagCorrectionEst < 10):
			chainSagCorrectionEst = 10
		if (chainSagCorrectionEst > 60):
			chainSagCorrectionEst = 60


print "---------------------------------------------------------------------------------------------"
if n == numberOfIterations:
	print "Machine parameters could no solve to your desired tolerance, but hopefully it got close."
else:
	print "Solved!"

print "Parameters for new GC"
print "--Maslow Settings Tab--"
distBetweenMotors = math.sqrt( math.pow(bestleftMotorXEst-bestrightMotorXEst,2)+math.pow(bestleftMotorYEst-bestrightMotorYEst,2))
print "Distance Between Motors: "+str(distBetweenMotors)
print "Motor Offset Height in mm: "+str(((bestleftMotorYEst+(bestrightMotorYEst-bestleftMotorYEst)/2.0))-workspaceHeight/2.0)
print "--Advanced Settings Tab--"
print "Chain Tolerance, Left Chain: "+str(round((1.0-bestleftChainToleranceEst)*100,7))
print "Chain Tolerance, Right Chain: "+str(round((1.0-bestrightChainToleranceEst)*100,7))
motorTilt = math.atan((bestrightMotorYEst-bestleftMotorYEst)/(bestrightMotorXEst-bestleftMotorXEst))*180.0/3.141592
print "Top Beam Tilt: "+str(round(motorTilt,7))
print "Rotation Radius for Triangular Kinematics: " + str(round(bestrotationRadiusEst, 4))
print "Chain Sag Correction Value for Triangular Kinematics: " + str(round(bestchainSagCorrectionEst, 6))
print "---------------------------------------------------------------------------------------------"
print "Error Magnitude: " + str(round(bestErrorMagnitude, 3))
for x in range(holeCount):
	print "  LChain Error Hole "+str(x)+": " + str(round(bestLChainErrorHole[x],4)) + "\t RChain Error Hole "+str(x)+": " + str(round(bestRChainErrorHole[x],4)) + "\t RMS Error Hole "+str(x)+": " +str(round(math.sqrt(math.pow(bestLChainErrorHole[x],2)+math.pow(bestRChainErrorHole[x],2)),4))


x="n"
while (x<>"x"):
   x = raw_input ("Press 'x' to exit")


#this was here for testing.  typed a lot so I'm saving it.
#print "leftMotorDistanceHole1: "+str(leftMotorDistanceHole1)+", leftMotorDistanceHole2: "+str(leftMotorDistanceHole2)+", leftMotorDistanceHole3: "+str(leftMotorDistanceHole3)+", leftMotorDistanceHole4: "+str(leftMotorDistanceHole4)
#print "rightMotorDistanceHole1: "+str(rightMotorDistanceHole1)+", rightMotorDistanceHole2: "+str(rightMotorDistanceHole2)+", rightMotorDistanceHole3: "+str(rightMotorDistanceHole3)+", leftMotorDistanceHole4: "+str(rightMotorDistanceHole4)
#print "leftChainAngleHole1: "+str(leftChainAngleHole1)+", leftChainAngleHole2: "+str(leftChainAngleHole2)+", leftChainAngleHole3: "+str(leftChainAngleHole3)+", leftChainAngleHole4: "+str(leftChainAngleHole4)
#print "rightChainAngleHole1: "+str(rightChainAngleHole1)+", rightChainAngleHole2: "+str(rightChainAngleHole2)+", rightChainAngleHole3: "+str(rightChainAngleHole3)+", rightChainAngleHole4: "+str(rightChainAngleHole4)
#print "leftChainSag1: "+str(leftChainSag1)+", leftChainSag2: "+str(leftChainSag2)+", leftChainSag3: "+str(leftChainSag3)+", leftChainSag4: "+str(leftChainSag4)
#print "rightChainSag1: "+str(rightChainSag1)+", rightChainSag2: "+str(rightChainSag2)+", rightChainSag3: "+str(rightChainSag3)+", rightChainSag4: "+str(rightChainSag4)
