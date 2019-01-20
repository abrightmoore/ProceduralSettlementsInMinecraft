# @TheWorldFoundry
# Heirarchical generation in 

import time
from numpy import zeros
from random import randint
from pymclevel import alphaMaterials,MCSchematic,BoundingBox
from math import pi,sin,cos,atan2,tan,sqrt,ceil
from os import listdir
from os.path import isfile, join
import glob
import PROCGEN_TOOLS

inputs = (
		("STARTPROC", "label"),
		("Generator Name",("string","value=Settlement_v2")),
		("adrian@TheWorldFoundry.com", "label"),
		("http://theworldfoundry.com", "label"),
		)

IGNOREBLOCKIDS = [6,17,18,31,32,37,38,39,40,50,51,59,63,75,76,78,81,83,86,92,99,100,103,104,105,106,111,115,127,140,141,142,161,162,166,175,176,177,199,200,207,255,]
		
def perform(level, box, options):
	''' 
		This is the top level harness for heirarchical generation procedures
		
		User selects the region to generate in
		This harness packages the selection and invokes the selected generator.
		Services provided at this level include:
		1. delegation to a sub-generator
		2. tracking available spaces to use in generation
		3. logging and commit to the world
		
		Note this is not memory efficient and super-large regions (> 3000x3000 areas) can fail
	'''
	log("Procedural generation is starting... Selected method is "+options["Generator Name"])
	generatedAreas = delegateGeneration(options["Generator Name"],level,[(box,True)])
	print "Areas generated:", generatedAreas
	log("Complete.")
	
def delegateGeneration(generatorName,level,areas):
	log("Delegating generation to "+generatorName+" for areas "+str(areas))
	module = __import__(generatorName)
	areas = module.create(generatorName,level,areas) # This attempts to invoke the create() method on the nominated generator
	# Note that children will apply their changes to the schematic they have been passed
	# Also note that the child is responsible for adjusting the areas list to mark areas that are allocated and available
	return areas

# Schematics

def profileCell(level,startPoint,endPoint):
	# Looks at the region of space within the two points and analyses it for various features
	# This is the place where we look at the landscape and understand it in more detail
	
	
	
	(x1,y1,z1) = startPoint
	(x2,y2,z2) = endPoint
	log("Profile cell starting")
	width = x2-x1
	height = y2-y1
	depth = z2-z1
	
	# Look at the surface features. Ignore block metadata 
	blockIDs = []
	blocks = []

	AIR = (0,0)
	
	maxHeight = 0
	minHeight = -1
	heightMap = zeros((width,depth))
	layerMap = zeros((width,depth,2))
	for z in xrange(z1,z2):
		for x in xrange(x1,x2):
			y = y2
			while y >= y1:
				y -= 1
				(blockID,blockData) = getBlock(level,x,y,z)
				if (blockID,blockData) != AIR and blockID not in IGNOREBLOCKIDS:
					if blockID not in blockIDs:
						blockIDs.append(blockID)
					if (blockID,blockData) not in blocks:
						blocks.append((blockID,blockData))
					heightMap[x-x1][z-z1] = y
					layerMap[x-x1][z-z1][0] = blockID
					layerMap[x-x1][z-z1][1] = blockData
					if y > maxHeight:
						maxHeight = y
					if y < minHeight:
						minHeight = y
					y = -1 # Break the loop, move to the next column
	log("Profile cell ended")
	return (heightMap,minHeight,maxHeight,layerMap,blocks,blockIDs)

def mapEdges(heightMap,deltaHalf):
	(width,depth) = heightMap.shape
	edgeMap = zeros((width-2,depth-2))
	
	for x in xrange(1,width-1):
		for y in xrange(1,depth-1):
			avgDelta = 0
			vr = heightMap[x,y]
			count = 0
			for dx in xrange(-deltaHalf,deltaHalf+1):
				for dy in xrange(-deltaHalf,deltaHalf+1):
					count += 1
					if not (dx == 0 and dy == 0):
						nr = heightMap[x+dx][y+dy]
						# print vr,nr
						avgDelta = avgDelta + int(abs(vr-nr))
			avgDelta = avgDelta / count 
			edgeMap[x-1][y-1] = avgDelta
	return edgeMap		

def identifyContiguousAreas(edgeMap):
	# Finding the flat areas on the map to build on
	(width,depth) = edgeMap.shape
	print "Edgemap",width,depth
	allocations = zeros((width,depth)) # Track the cells we've allocated or discarded
	SLOPETOLERANCE = 1
	
	cells = []
	# The strategy here is to identify square areas of the same values throughout the map.
	# They shouldn't overlap.
	
	cursorx = 0 # Start top-left
	cursory = 0
	keepGoing = True
	count = 1000000
	while keepGoing and count > 0:
		count -= 1 # Exit the loop eventually
		
		size = 0 # Grow this square until we hit a value that's outside the tolerance
		
		growingSquare = True
		while growingSquare:
			same = True
			size += 1
			for dx in xrange(0,size): # Scan the next row
				px = cursorx+dx
				py = cursory+size
				if px < width and py < depth:
					if abs(edgeMap[px][py]) > SLOPETOLERANCE or allocations[px][py] != 0:
						same = False
						break # from the for loop
				else:
					same = False
			if same == True:
				for dy in xrange(0,size): # Scan the next column
					px = cursorx+size
					py = cursory+dy
					if px < width and py < depth:
						if abs(edgeMap[px][py]) > SLOPETOLERANCE or allocations[px][py] != 0:
							same = False
							break # from the for loop
					else:
						same = False
			if same == False: # We found a cell that's too high or low. Add the square up to this point and mark the cells allocated. The start again from a free cell
				cells.append((cursorx,cursory,size-1)) # Save the square we were traversing as a complete unit
				for dx in xrange(cursorx,cursorx+size):
					for dy in xrange(cursory,cursory+size):
						if dx < width and dy < depth:
							allocations[dx][dy] = 1 # mark allocated
				growingSquare = False
			if cursorx+size >= width and cursory+size >= depth: # We're off the edge of the edgeMap
				growingSquare = False

		# find a free cell to start the search from
		x = 0
		y = 0
		findingFreeCell = True
		while findingFreeCell:
			# if randint(1,1000) == 999: print "---",x,y
			if allocations[x,y] == 0:
				cursorx = x
				cursory = y
				findingFreeCell = False
			x += 1
			if x >= width:
				y += 1
				x = 0
				if y >= depth: # No free cells
					findingFreeCell = False
					keepGoing = False
		
		if cursorx >= width and cursory >= depth: # We're off the edge of the edgeMap
			keepGoing = False
		
	
	return cells
	
def makeBlankAreaOfSizeWHD(width, height, depth):
	return MCSchematic((width, height, depth))
	
def copyAreaOfSizeWHDFromSchematicAtPosXYZ(source, width, height, depth, posx, posy, posz):
	return source.extractSchematic(BoundingBox((posx,posy,posz),(width,height,depth)))
	
def pasteAreaOfSizeWHDToSchematicAtPosXYZ(source, destination, width, height, depth, posx, posy, posz):
	# Paste into the world, but don't damage anything already there
	#b=range(4096); b.remove(0) # @CodeWarrior0 and @Wout12345 explained how to merge schematics
	destination.copyBlocksFrom(source,BoundingBox((0,0,0),(width,height,depth)),(posx,posy,posz))	

# Boxes
	
def getDimensionsFromBox(box):
	return (box.maxx-box.minx,box.maxy-box.miny,box.maxz-box.minz)
	
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

def log(message):
	print "STARTPROC",time.ctime(),message

# Block
	
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

# Lines

def fill(level,(minx,miny,minz),(maxx,maxy,maxz),material):
	for y in xrange(miny,maxy):
		for x in xrange(minx,maxx):
			for z in xrange(minz,maxz):
				if getBlock(level,x,y,z) == (0,0):
					setBlock(level,x,y,z,material)
					
def fillForced(level,(minx,miny,minz),(maxx,maxy,maxz),material):
	for y in xrange(miny,maxy):
		for x in xrange(minx,maxx):
			for z in xrange(minz,maxz):
				setBlock(level,x,y,z,material)
					
def flatten(anArray):
	result = []
	for a in anArray:
		for b in a:
			result.append(b)
	return result
	
def calcLine((x,y,z), (x1,y1,z1) ):
	return calcLineConstrained((x,y,z), (x1,y1,z1), 0 )

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

def calcLinesSmooth(SMOOTHAMOUNT,P):
	Q = []
	for i in xrange(0,SMOOTHAMOUNT):
		P = chaikinSmoothAlgorithm(P)
	Q = calcLines(P)
	return flatten(Q)
	
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