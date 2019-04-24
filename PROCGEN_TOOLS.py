# @TheWorldFoundry

from os import listdir
from os.path import isfile, join
from random import randint
from math import pi,sin,cos,atan2,tan,sqrt
import glob
import pygame

from pymclevel import alphaMaterials,MCSchematic,BoundingBox

UUID = randint(1000000000,9999999999)

def copyBlocksFrom(level, schematic, box, pos, b):
	if False:
		level.copyBlocksFrom(schematic, box, pos,b)
	
	# Append to the tracking log
	if True:
		filenameIndex = str(UUID)+"_PROCGEN_Index"
		filenameComposition = str(UUID)+"_PROCGEN_Composition"
		schemaID = randint(1000000000,9999999999)
		filenameSchematic = str(UUID)+"_PROCGEN_Schematic"+str(schemaID)+".schematic"
		suffix = ".txt"
		
		x,y,z = pos
		# Save the schematic as a new unique file
		schematic.saveToFile(filename=filenameSchematic)
		addStringToFile(filenameIndex,suffix,str(schemaID)+"="+filenameSchematic) # Kludge = each schematic placement is a unique copy in this stub
		addStringToFile(filenameComposition,suffix,str(schemaID)+"="+str(x)+","+str(y)+","+str(z))

def addStringToFile(prefix,suffix,theString):
	theFile = open(prefix+'_'+suffix, 'a+')
	theFile.write("\n"+str(theString))
	theFile.close()

def extendFreePlots(alreadyPlacedPlots,placedPlots,buildingDelegatedAreas,newPlots):

	for aPlot in placedPlots:
		alreadyPlacedPlots.append(aPlot)
		print "Placed plot count is now",len(alreadyPlacedPlots)
	if randint(1,100) > 99:
		for a in alreadyPlacedPlots:
			print "AlreadyPlacedPlot",a	
	
	buildingDelegatedAreasCounter = 0
	while buildingDelegatedAreasCounter < len(buildingDelegatedAreas):
		freeSpace = buildingDelegatedAreas[buildingDelegatedAreasCounter]
		(Aminx,Aminz,Amaxx,Amaxz) = freeSpace
		saveThisPlot = True # Candidate to save
		newPlotsCounter = 0
		while newPlotsCounter < len(newPlots):
			(Bminx,Bminz,Bmaxx,Bmaxz) = newPlots[newPlotsCounter]
			newPlotsCounter += 1
			if checkBoundingBoxIntersect((Aminx,Aminz,Aminx+Amaxx,Aminz+Amaxz), (Bminx,Bminz,Bminz+Bmaxz,Bminz+Bmaxz)): # If there is no collision with existing plots, add this one
				saveThisPlot = False # Collides with an existing one
				newPlotsCounter = len(newPlots) # break looping
		if saveThisPlot == True: # Candidate to save
			alreadyPlacedPlotsCounter = 0
			while alreadyPlacedPlotsCounter < len(alreadyPlacedPlots):
				(Bminx,Bminz,Bmaxx,Bmaxz) = alreadyPlacedPlots[alreadyPlacedPlotsCounter]
				alreadyPlacedPlotsCounter += 1
				if checkBoundingBoxIntersect((Aminx,Aminz,Aminx+Amaxx,Aminz+Amaxz), (Bminx,Bminz,Bminz+Bmaxz,Bminz+Bmaxz)): # If there is no collision with existing used plots, add this one
					saveThisPlote = False # Collision
					alreadyPlacedPlotsCounter = len(alreadyPlacedPlots)
		if saveThisPlot == True:
			newPlots.append(freeSpace) # Add any remaining space to the list	
		buildingDelegatedAreasCounter += 1
	return newPlots



def checkBoundingBoxIntersect((Aminx,Aminz,Amaxx,Amaxz), (Bminx,Bminz,Bmaxx,Bmaxz)):
	#print 'Checking BB A/B intersection '
	#printBoundingBox(A)
	#printBoundingBox(B)
	# Check for A completely to the left of B. https://github.com/mcedit/pymclevel/blob/master/box.py
	# http://www.toymaker.info/Games/html/3d_collisions.html
	if Amaxx < Bminx:
	    return False
	# Check for A to the right of B
	if Aminx > Bmaxx:
	    return False
	# Check for A in front of B
	if Amaxz < Bminz:
	    return False
	# Check for A behind B
	if Aminz > Bmaxz:
	    return False
	# Check for A above B
#	if A.miny > B.maxy:
#	    return False
	# Check for A below B
#	if A.maxy < B.miny:
#	   return False
	   
	# Collision has occurred
	#print 'Collision occurred'
	return True


def checkBoundingBoxIntersect3D((Aminx,Aminy,Aminz,Amaxx,Amaxy,Amaxz), (Bminx,Bminy,Bminz,Bmaxx,Bmaxy,Bmaxz)):
	#print 'Checking BB A/B intersection '
	#printBoundingBox(A)
	#printBoundingBox(B)
	# Check for A completely to the left of B. https://github.com/mcedit/pymclevel/blob/master/box.py
	# http://www.toymaker.info/Games/html/3d_collisions.html
	if Amaxx < Bminx:
	    return False
	# Check for A to the right of B
	if Aminx > Bmaxx:
	    return False
	# Check for A in front of B
	if Amaxz < Bminz:
	    return False
	# Check for A behind B
	if Aminz > Bmaxz:
	    return False
	# Check for A above B
	if Aminy > Bmaxy:
	    return False
	# Check for A below B
	if Amaxy < Bminy:
	   return False
	   
	# Collision has occurred
	#print 'Collision occurred'
	return True


	
def createZoneMap(numPoints,boxW,boxD):
	zonePoints = []

	# High-rise
	#zonePoints.append((2.0,boxW>>1,boxD>>1,boxW,0)) # Power, x pos, z pos, wavelength, phase shift
	# Residential
	#zonePoints.append((0.5,randint(0,boxW>>1),randint(0,boxW>>1),boxW<<1,pi)) # Power, x pos, z pos, wavelength
	# Based on the value at the location determined by the interference of the zonePoints we will choose what to build in the plot
	# > 0.7 High-rise
	# > 0.4 Medium-rise
	# > 0.1 Low-rise
	# > -.4 Parkland / vacant
	# > -0.8 Residential
	# otherwise ...

	
	# NOTE: This can be an option to load in a prepared zoning map
	AMPLITUDE = 0.5
	zonePoints.append((AMPLITUDE,boxW>>1,boxD>>1,boxW,0)) # Power, x pos, z pos, wavelength, phase shift
	# Residential
	#zonePoints.append((0.5,randint(0,boxW>>1),randint(0,boxW>>1),boxW,pi)) # Power, x pos, z pos, wavelength
	for i in xrange(0,randint(1,numPoints)):
		zonePoints.append((0.1,randint(0,boxW),randint(0,boxW),boxW,pi)) # Power, x pos, z pos, wavelength
		
	# Debug - plot out the zoning pattern as an image 
	zoneImg = pygame.Surface((boxW,boxD))
	px = pygame.surfarray.pixels3d(zoneImg)
	for x in xrange(0,boxW):
		for z in xrange(0,boxD):
			valHere = 0
			cols = []
			count = 0
			for (amp,ppx,ppz,wavelength,offset) in zonePoints:
				dx = x-(ppx)
				dz = z-(ppz)
				dist = sqrt(dx**2+dz**2)
				ratio = dist/wavelength
				contribution = cos(offset+ratio*pi*2.0)
				valHere += valHere+contribution
				cols.append(contribution)
				count += 1
			valHere = (valHere+1.0)/2.0 * 255
			lowerBound = 0
			excess = 0
			if valHere < 0: 
				lowerBound = 0-valHere
				valHere = 0
			if valHere > 255:
				excess = valHere - 255
				valHere = 255
				
			px[x][z] = (int(lowerBound),int(excess),int(valHere))

	del px
	return zoneImg


def loadSchematicsFromDirectory(pathname):
	print "Loading in schematics from directory",pathname
	
	SchematicFileNames = glob.glob(join(pathname, "*.schematic"))
	for fileName in SchematicFileNames:
		print fileName
	print "Found", len(SchematicFileNames), "schematic files"
	# End cached file names
	CACHE = []
	for fn in SchematicFileNames:
		print "Loading schematic from file",fn
		sourceSchematic = MCSchematic(filename=fn)
		CACHE.append((sourceSchematic,fn))
	return CACHE

def createArea(areaGeneratorName,level,areaBox,parentLevel,parentBox,areaPositionInParent):
	module = __import__(areaGeneratorName)
	result = module.create(level,areaBox,parentLevel,parentBox,areaPositionInParent) # This attempts to invoke the create() method on the nominated generator
	print result
	return result

# ---------------- YE OLDE LIBRARIES ----------------

def setBlock(level,x,y,z,material):
	(id,data) = material
	level.setBlockAt(int(x),int(y),int(z),id)
	level.setBlockDataAt(int(x),int(y),int(z),data)

def getBlock(level,x,y,z):
	id = level.blockAt(int(x),int(y),int(z))
	data = level.blockDataAt(int(x),int(y),int(z))
	return (id,data)
	
def getBlockFromOptions(options,label):
	return ( options[label].ID,
			 options[label].blockData
			)
			
def drawSphere(level,(x,y,z), r, material):
	RSQUARED = r*r
	for iterX in xrange(-r,r+1):
		XSQUARED = iterX*iterX
		XOFFSET = x+iterX
		for iterZ in xrange(-r,r+1):
			ZSQUARED = iterZ*iterZ
			ZOFFSET = z+iterZ
			for iterY in xrange(-r,r+1):
				if XSQUARED + ZSQUARED + iterY*iterY <= RSQUARED:
					setBlock(level, XOFFSET, y+iterY, ZOFFSET, material)

def flatten(anArray):
	result = []
	for a in anArray:
		for b in a:
			result.append(b)
	return result
	
# Ye Olde GFX Libraries
def cosineInterpolate(a, b, x): # http://www.minecraftforum.net/forums/off-topic/computer-science-and-technology/482027-generating-perlin-noise?page=40000
	ft = pi * x
	f = ((1.0 - cos(ft)) * 0.5)
	ret = float(a * (1.0 - f) + b * f)
	return ret

def cnoise(x,y,z):
	# Return the value of interpolated noise at this location
	return float(Random(x+(y<<4)+(z<<8)).random())

def noise(x,y,z):
	ss = 8
	bs = 3
	cx = x >> bs
	cy = y >> bs
	cz = z >> bs

	rdx = float((float(x%ss))/ss)
	rdy = float((float(y%ss))/ss)
	rdz = float((float(z%ss))/ss)
#	print rdx,rdy,rdz
	
	# current noise cell
	P = zeros((2,2,2))
	for iy in xrange(0,2):
		for iz in xrange(0,2):
			for ix in xrange(0,2):
				P[ix,iy,iz] = float(cnoise(cx+ix,cy+iy,cz+iz))
	
	# print P

	dvx1 = cosineInterpolate(P[0,0,0],P[1,0,0],rdx)
	dvx2 = cosineInterpolate(P[0,1,0],P[1,1,0],rdx)
	dvx3 = cosineInterpolate(P[0,0,1],P[1,0,1],rdx)
	dvx4 = cosineInterpolate(P[0,1,1],P[1,1,1],rdx)

	dvz1 = cosineInterpolate(dvx1,dvx3,rdz)
	dvz2 = cosineInterpolate(dvx2,dvx4,rdz)

	n = cosineInterpolate(dvz1,dvz2,rdy)
	
	return n

def drawSphere(level,material,r,x,y,z,overwrite):
	r = int(r)
	RSQUARED = r*r
	for iterX in xrange(-r,r):
		XSQUARED = iterX*iterX
		XOFFSET = x+iterX
		for iterZ in xrange(-r,r):
			ZSQUARED = iterZ*iterZ
			ZOFFSET = z+iterZ
			for iterY in xrange(-r,r):
				if XSQUARED + ZSQUARED + iterY*iterY <= RSQUARED:
					plotPoint(level, material, XOFFSET, y+iterY, ZOFFSET, overwrite)

def createSign(level, x, y, z, text): #abrightmoore - convenience method. Due to Jigarbov - this is not a Sign.
	ALIASKEY = "SEED NUMBER"
	COMMANDBLOCK = 137
	CHUNKSIZE = 16
	STANDING_SIGN = 63
	
	setBlockForced(level, (STANDING_SIGN,8), x, y, z)
	setBlockForced(level, (1,0), x, y-1, z)
	control = TAG_Compound()
	control["id"] = TAG_String("Sign")
	control["Text1"] = TAG_String(ALIASKEY)
	control["Text2"] = TAG_String(text)
	control["Text3"] = TAG_String("Generated by")
	control["Text4"] = TAG_String("@abrightmoore")	
	
	control["x"] = TAG_Int(x)
	control["y"] = TAG_Int(y)
	control["z"] = TAG_Int(z)
	chunka = level.getChunk((int)(x/CHUNKSIZE), (int)(z/CHUNKSIZE))
	chunka.TileEntities.append(control)
	chunka.dirty = True

def chaikinSmoothAlgorithm(P): # http://www.idav.ucdavis.edu/education/CAGDNotes/Chaikins-Algorithm/Chaikins-Algorithm.html
	F1 = 0.25
	F2 = 0.75
	Q = []
	(x0,y0,z0) = (-1,-1,-1)
	count = 0
	for (x1,y1,z1) in P:
		if count > 0: # We have a previous point
			(dx,dy,dz) = (x1-x0,y1-y0,z1-z0)
#			Q.append( (x0*F2+x1*F1,0,z0*F2+z1*F1) )
#			Q.append( (x0*F1+x1*F2,0,z0*F1+z1*F2) )

			Q.append( (x0*F2+x1*F1,y0*F2+y1*F1,z0*F2+z1*F1) )
			Q.append( (x0*F1+x1*F2,y0*F1+y1*F2,z0*F1+z1*F2) )

#			Q.append( (x0+dx*F1+*F2,y0*F1+y1*F2,z0*F1+z1*F2) )
#			Q.append( (x0*F2+x1*F1,y0*F2+y1*F1,z0*F2+z1*F1) )
		else:
			count = count+1
		(x0,y0,z0) = (x1,y1,z1)

	return Q

def drawTrianglePreOp(level, (p1x, p1y, p1z), (p2x, p2y, p2z), (p3x, p3y, p3z), materialEdge, materialFill):
	if materialFill != (0,0):
		# for each step along the 'base' draw a line from the apex
		dx = p3x - p2x
		dy = p3y - p2y
		dz = p3z - p2z

		distHoriz = dx*dx + dz*dz
		distance = sqrt(dy*dy + distHoriz)
		
		phi = atan2(dy, sqrt(distHoriz))
		theta = atan2(dz, dx)

		P = []
		
		iter = 0
		while iter <= distance:
			(px, py, pz) = ((int)(p2x+iter*cos(theta)*cos(phi)), (int)(p2y+iter*sin(phi)), (int)(p2z+iter*sin(theta)*cos(phi)))
			
			iter = iter+0.5 # slightly oversample because I lack faith.
			P.append(calcLine((px, py, pz), (p1x, p1y, p1z) ))
		P = flatten(P)
		Q = []
		for (x,y,z) in P:
			if (int(x),int(y),int(z)) not in Q:
				Q.append((int(x),int(y),int(z)))
				setBlock(level,x,y,z,materialFill)
	
	#drawLine(level, materialEdge, (p1x, p1y, p1z), (p2x, p2y, p2z) )
	#drawLine(level, materialEdge, (p1x, p1y, p1z), (p3x, p3y, p3z) )
	#drawLine(level, materialEdge, (p2x, p2y, p2z), (p3x, p3y, p3z) )
	
def drawTriangle(level, (p1x, p1y, p1z), (p2x, p2y, p2z), (p3x, p3y, p3z), materialEdge, materialFill):
	if materialFill != (0,0):
		# for each step along the 'base' draw a line from the apex
		dx = p3x - p2x
		dy = p3y - p2y
		dz = p3z - p2z

		distHoriz = dx*dx + dz*dz
		distance = sqrt(dy*dy + distHoriz)
		
		phi = atan2(dy, sqrt(distHoriz))
		theta = atan2(dz, dx)

		iter = 0
		while iter <= distance:
			(px, py, pz) = ((int)(p2x+iter*cos(theta)*cos(phi)), (int)(p2y+iter*sin(phi)), (int)(p2z+iter*sin(theta)*cos(phi)))
			
			iter = iter+0.5 # slightly oversample because I lack faith.
			drawLine(level, materialFill, (px, py, pz), (p1x, p1y, p1z) )
	
	
	drawLine(level, materialEdge, (p1x, p1y, p1z), (p2x, p2y, p2z) )
	drawLine(level, materialEdge, (p1x, p1y, p1z), (p3x, p3y, p3z) )
	drawLine(level, materialEdge, (p2x, p2y, p2z), (p3x, p3y, p3z) )

def drawTriangleEdge(level, box, options, (p1x, p1y, p1z), (p2x, p2y, p2z), (p3x, p3y, p3z), materialEdge):
	drawLine(level, materialEdge, (p1x, p1y, p1z), (p2x, p2y, p2z) )
	drawLine(level, materialEdge, (p1x, p1y, p1z), (p3x, p3y, p3z) )
	drawLine(level, materialEdge, (p2x, p2y, p2z), (p3x, p3y, p3z) )

def plotLine(level,material,p1,p2):

	(x1,y1,z1) = p1
	(x2,y2,z2) = p2
	
	dx = x2-x1
	dy = y2-y1
	dz = z2-z1
	
	steps = abs(dx)
	if abs(dy) > abs(dx):
		steps = abs(dy)
	if abs(dz) > abs(dy):
		steps = abs(dz)
	if steps == 0:
		setBlock(level,material,x1,y1,z1)
	else:
		ddx = float(dx)/float(steps)
		ddy = float(dy)/float(steps)
		ddz = float(dz)/float(steps)
		pdx = float(0)
		pdy = float(0)
		pdz = float(0)
		
		for i in xrange(0,int(steps)):
			setBlock(level,material,x1+pdx,y1+pdy,z1+pdz)
			pdx = pdx + ddx
			pdy = pdy + ddy
			pdz = pdz + ddz

def calcLine((x,y,z), (x1,y1,z1) ):
	return calcLineConstrained((x,y,z), (x1,y1,z1), 0 )
			
def drawLine(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1) ):
	return drawLineConstrained(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1), 0 )

def calcLinesSmooth(SMOOTHAMOUNT,P):
	Q = []
	for i in xrange(0,SMOOTHAMOUNT):
		P = chaikinSmoothAlgorithm(P)
	Q = calcLines(P)
	return flatten(Q)

def drawLinesSmooth(level,box,material,SMOOTHAMOUNT,P):
	Q = []
	for i in xrange(0,SMOOTHAMOUNT):
		P = chaikinSmoothAlgorithm(P)
	Q = drawLines(level,box,material,P)
	return Q

def drawLinesSmoothForced(level,box,material,SMOOTHAMOUNT,P):
	Q = []
	for i in xrange(0,SMOOTHAMOUNT):
		P = chaikinSmoothAlgorithm(P)
	Q = drawLinesForced(level,box,material,P)
	return Q

def calcLines(P):
	Q = []
	count = 0
	(x0,y0,z0) = (0,0,0)
	for (x,y,z) in P:
		if count > 0:
			Q.append( calcLine((x0,y0,z0),(x,y,z)) )
		count = count+1
		(x0,y0,z0) = (x,y,z)
	return Q
	
def drawLines(level,box,material,P):
	Q = []
	count = 0
	(x0,y0,z0) = (0,0,0)
	for (x,y,z) in P:
		if count > 0:
			Q.append( drawLine(level,material,(box.minx+x0,box.miny+y0,box.minz+z0),(box.minx+x,box.miny+y,box.minz+z)) )
		count = count+1
		(x0,y0,z0) = (x,y,z)
	return Q

def drawLinesForced(level,box,material,P):
	Q = []
	count = 0
	(x0,y0,z0) = (0,0,0)
	for (x,y,z) in P:
		if count > 0:
			Q.append( drawLineForced(level,material,(box.minx+x0,box.miny+y0,box.minz+z0),(box.minx+x,box.miny+y,box.minz+z)) )
		count = count+1
		(x0,y0,z0) = (x,y,z)
	return Q	
	
def drawLineForced(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1) ):
	return drawLineConstrainedForced(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1), 0 )
	
def drawLine1(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1) ):
	for px, py, pz in bresenham.bresenham((x,y,z),(x1,y1,z1)):
		setBlock(scratchpad,(blockID, blockData),px,py,pz)
	setBlock(scratchpad,(blockID, blockData),x1,y1,z1)

def calcLineConstrained((x,y,z), (x1,y1,z1), maxLength ):
	dx = x1 - x
	dy = y1 - y
	dz = z1 - z

	distHoriz = dx*dx + dz*dz
	distance = sqrt(dy*dy + distHoriz)
	P = []
	if distance < maxLength or maxLength < 1:
		phi = atan2(dy, sqrt(distHoriz))
		theta = atan2(dz, dx)

		iter = 0
		while iter <= distance:
			(xd,yd,zd) = ((int)(x+iter*cos(theta)*cos(phi)), (int)(y+iter*sin(phi)), (int)(z+iter*sin(theta)*cos(phi)))
			# setBlock(scratchpad,(blockID,blockData),xd,yd,zd)
			P.append((xd,yd,zd))
			iter = iter+0.5 # slightly oversample because I lack faith.
	return P # The set of all the points calc'd

	
def drawLineConstrained(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1), maxLength ):
	dx = x1 - x
	dy = y1 - y
	dz = z1 - z

	distHoriz = dx*dx + dz*dz
	distance = sqrt(dy*dy + distHoriz)
	P = []
	if distance < maxLength or maxLength < 1:
		phi = atan2(dy, sqrt(distHoriz))
		theta = atan2(dz, dx)

		iter = 0
		while iter <= distance:
			(xd,yd,zd) = ((int)(x+iter*cos(theta)*cos(phi)), (int)(y+iter*sin(phi)), (int)(z+iter*sin(theta)*cos(phi)))
			setBlock(scratchpad,xd,yd,zd,(blockID,blockData))
			P.append((xd,yd,zd))
			iter = iter+0.5 # slightly oversample because I lack faith.
	return P # The set of all the points drawn

def drawLineConstrainedForced(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1), maxLength ):
	dx = x1 - x
	dy = y1 - y
	dz = z1 - z

	distHoriz = dx*dx + dz*dz
	distance = sqrt(dy*dy + distHoriz)
	P = []
	if distance < maxLength or maxLength < 1:
		phi = atan2(dy, sqrt(distHoriz))
		theta = atan2(dz, dx)

		iter = 0
		while iter <= distance:
			(xd,yd,zd) = ((int)(x+iter*cos(theta)*cos(phi)), (int)(y+iter*sin(phi)), (int)(z+iter*sin(theta)*cos(phi)))
			setBlockForced(scratchpad,(blockID,blockData),xd,yd,zd)
			P.append((xd,yd,zd))
			iter = iter+0.5 # slightly oversample because I lack faith.
	return P # The set of all the points drawn
	
def drawLineConstrainedRandom(scratchpad, (blockID, blockData), (x,y,z), (x1,y1,z1), frequency ):
	dx = x1 - x
	dy = y1 - y
	dz = z1 - z

	distHoriz = dx*dx + dz*dz
	distance = sqrt(dy*dy + distHoriz)


	phi = atan2(dy, sqrt(distHoriz))
	theta = atan2(dz, dx)

	iter = 0
	while iter <= distance:
		if randint(0,99) < frequency:
			scratchpad.setBlockAt((int)(x+iter*cos(theta)*cos(phi)), (int)(y+iter*sin(phi)), (int)(z+iter*sin(theta)*cos(phi)), blockID)
			scratchpad.setBlockDataAt((int)(x+iter*cos(theta)*cos(phi)), (int)(y+iter*sin(phi)), (int)(z+iter*sin(theta)*cos(phi)), blockData)
		iter = iter+0.5 # slightly oversample because I lack faith.
	

def plotPoint(level, (block, data), x, y, z, overwrite):
	if overwrite == True:
		setBlockForced(level, (block, data), x, y, z)
	else:
		setBlock(level, (block, data), x, y, z)

