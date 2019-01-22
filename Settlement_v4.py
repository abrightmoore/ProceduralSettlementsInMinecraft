# @TheWorldFoundry
# v2 scans the landscape for placement opportunities


import STARTPROC_v1 # Procedural tools / framework
from STARTPROC_v1 import calcLinesSmooth,IGNOREBLOCKIDS,getBlock,setBlock,log,profileCell,mapEdges,identifyContiguousAreas,delegateGeneration,copyAreaOfSizeWHDFromSchematicAtPosXYZ,pasteAreaOfSizeWHDToSchematicAtPosXYZ,makeBlankAreaOfSizeWHD,getDimensionsFromBox
from random import randint,shuffle
from numpy import zeros
from pymclevel import alphaMaterials,MCSchematic,BoundingBox

def create(generatorName,level,areas):
	# This module creates a settlement in the selection based on the availableAreas.
	SMALL = 8
	MEDIUM = 16
	LARGE = 32
		
	settlementA = ["House","House","House","TownSquare","Tower"] #["TownSquare","TownHall","Farm","House"] # Add any generator types here
	for i in xrange(0,randint(30,100)):
		if randint(1,10) > 9:
			settlementA.append("Tower")
		else:
			settlementA.append("House")
	settlementB = settlementA #["House","House","Farm","Farm","TownSquare","TownHall","Farm","Farm"] # Add any generator types here
	settlements = [settlementA,settlementB] # In reality you'll mix this up with different blueprints
	
	# Optional: Check bounds and whether we can do anything
	
	chosenVariant = settlements[randint(0,len(settlements)-1)] # Pick one at random

	BADFOUNDATIONBLOCKS = [8,9,10,11]
	plotAreas = []	
	for (box,flag) in areas:
		(heightMap,minHeight,maxHeight,layerMap,blocks,blockIDs) = profileCell(level,(box.minx,box.miny,box.minz),(box.maxx,box.maxy,box.maxz))
		edgeMap = mapEdges(heightMap,1)
		cells = identifyContiguousAreas(edgeMap)
		print cells
		# The cells list is (posx,posy,size). So we are going to build a new set of boxes and use them to generate the settlement
		for (x,y,size) in cells:
			if False: # Debug
				col = randint(0,15)
				for ix in xrange(box.minx+x,box.minx+x+size):
					for iz in xrange(box.minz+y,box.minz+y+size):
						setBlock(level,ix,box.maxy-3,iz,(35,col))
						# print ix,box.maxy-3,iz
			if size >= SMALL: # Minimum size to generate against
				# Check if this area has water or lava in it, in which case we can't build here
				okToBuild = True
				badFoundationCount = 0
				width,depth,dim = layerMap.shape
				px = x+1
				py = y+1
				while py < y+1+size:
					if px < width-1 and py < depth-1:
						if layerMap[px][py][0] in BADFOUNDATIONBLOCKS:
							badFoundationCount += 1
							print "Badfoundations :",badFoundationCount
							if badFoundationCount > 9: # is a problem for us	
								print "Badfoundations:",badFoundationCount
								okToBuild = False # Can't build on quicksand (or lava and water)
								py = y+1+size # exit loop
					px += 1
					if px >= x+1+size:
						px = x+1
						py += 1
				if okToBuild == True:
					# what is the height to use? Try for average...
					avgHeight = 0
					for ppx in xrange(x,x+size):
						for ppy in xrange(y,y+size):
							avgHeight += heightMap[ppx][ppy]
					avgHeight = int(avgHeight/(size*size))
					print avgHeight
					plotArea = BoundingBox((box.minx+x,avgHeight,box.minz+y),(size,box.maxy-(avgHeight),size)) # Save this plot, discard all others
					plotAreas.append((plotArea,True))
					print "Viable area",plotArea
				else:
					print "Bad foundations at",x,y,size
	
	resultAreas = []
	keepGoing = True
	blueprintCounter = 0
	while keepGoing == True and len(plotAreas) > 0 and blueprintCounter < len(chosenVariant): # Bounds checking
		shuffle(plotAreas)
		(box,availableFlag) = plotAreas.pop() # Get an area
		if availableFlag == True:
			# Chop up the box to allocate space to the child. We'll use a 2D centre segmentation method
			width,height,depth = getDimensionsFromBox(box)
			
			size = -1
			if width >= LARGE and height >= LARGE and depth >= LARGE:
				size = LARGE
			elif width >= MEDIUM and height >= MEDIUM and depth >= MEDIUM:
				size = MEDIUM
			elif width >= SMALL and height > SMALL and depth > SMALL:
				size = SMALL
			if size != -1: # -1 is invalid - selection too small
				# Carve up the area, allocate the central portion to the delegate generator, and return the free ones to the area stack for re-use
				chopXPos1 = ((box.maxx+box.minx)>>1)-(size>>1)
				chopXPos2 = ((box.maxx+box.minx)>>1)+(size>>1)
				chopZPos1 = ((box.maxz+box.minz)>>1)-(size>>1)
				chopZPos2 = ((box.maxz+box.minz)>>1)+(size>>1)
				
				# These are the free areas
				areas.append((BoundingBox((box.minx,box.miny,box.minz),(chopXPos1-box.minx,height,chopZPos2-box.minz)),True))
				areas.append((BoundingBox((box.minx,box.miny,chopZPos2),(chopXPos2-box.minx,height,box.maxz-1-chopZPos2)),True))
				areas.append((BoundingBox((chopXPos2,box.miny,chopZPos1),(box.maxx-1-chopXPos2,height,box.maxz-1-chopZPos1)),True))
				areas.append((BoundingBox((chopXPos1,box.miny,box.minz),(box.maxx-1-chopXPos1,height,chopZPos1-box.minz)),True))
				
				# This is the new building location
				newBox = BoundingBox((0,0,0),(size,size,size))

				# Create a new level to generate the building within and, once built, copy it back over onto the level
				# scratchpadHouse = makeBlankAreaOfSizeWHD(size,height,size)
				
				# Clear out all the nuisance blocks

				AIR = (0,0)
				for y in xrange(box.miny,box.miny+size):
					for z in xrange(chopZPos1,chopZPos1+size):
						for x in xrange(chopXPos1,chopXPos1+size):
							(theBlockID,theBlockData) = getBlock(level,x,y,z)
							if theBlockID in IGNOREBLOCKIDS:
								setBlock(level,x,y,z,AIR)
				
				scratchpadLand = copyAreaOfSizeWHDFromSchematicAtPosXYZ(level, size, height, size, chopXPos1, box.miny, chopZPos1)
				newGeneratedAreas = delegateGeneration(chosenVariant[blueprintCounter],scratchpadLand,[(newBox,True)])
				# scratchpadLand.copyBlocksFrom(scratchpadHouse,BoundingBox((0,0,0),(size,height,size)),(0,0,0))	
				pasteAreaOfSizeWHDToSchematicAtPosXYZ(scratchpadLand, level, scratchpadLand.Width, scratchpadLand.Height, scratchpadLand.Length, chopXPos1, box.miny, chopZPos1)
				# Put in some support pylons if there are parts of the house suspended...
				log("Placing building supports")
				for iz in xrange(chopZPos1,chopZPos1+scratchpadLand.Length):
					for ix in xrange(chopXPos1,chopXPos1+scratchpadLand.Width):
						iy = box.miny+scratchpadLand.Height-1
						drawPylon = False
						while (iy >= 0 and drawPylon == True) or (drawPylon == False and iy >= box.miny):
							(theBlockID,theBlockData) = getBlock(level,ix,iy,iz)
							if  drawPylon == True and (theBlockID == 0 or theBlockID in IGNOREBLOCKIDS or theBlockID in [8,9,10,11]): # + Liquids
								setBlock(level,ix,iy,iz,(4,0)) # Cobblestone
							elif theBlockID == 4:
								drawPylon = True
							elif drawPylon == True:
								drawPylon = False # Turn it off
								iy = 0 # Break out
							iy -= 1
							
								
								
				
				
				blueprintCounter += 1 # Move onto the next building type
				resultAreas.append((box,True))
			else:
				log("Unable to find space for generation within area "+str(box))
				# Discard this area, it's too small a fragment and cannot be effectively used at this time
				# This causes the areas list to tend to empty
				# TODO: consider putting micro-details into tiny areas

	# Segmentation of the village - low walls and lines of trees/shrubs
	# Voronoi cells
	log("Creating yards and walls")
	minx = 1000000000 
	minz = 1000000000
	maxx = -1000000000
	maxz = -1000000000
	points = []

	for (box,flag) in resultAreas:
		box1centrex = (box.maxx+box.minx)>>1
		box1centrez = (box.maxz+box.minz)>>1
		points.append((box1centrex,box1centrez))
		if box1centrex < minx: minx = box1centrex
		if box1centrex > maxx: maxx = box1centrex
		if box1centrez < minz: minz = box1centrez
		if box1centrez > maxz: maxz = box1centrez
	log(str(points))	
	v = zeros((maxx-minx,maxz-minz,4))
	for z in xrange(minz,maxz):
		for x in xrange(minx,maxx):
			px = x-minx
			pz = z-minz
			if v[px][pz][3] == 0: v[px][pz][2] = 1000000000
			for X,Z in points:
				dx = x-X
				dz = z-Z
				dist = dx*dx+dz*dz
				if dist < v[px][pz][2]:
					v[px][pz][0] = X # Which point we're associated with
					v[px][pz][1] = Z
					v[px][pz][2] = dist # Store a distance
					v[px][pz][3] = 1 # Mark processed
	print v
	edgePoints = []
	# Find edgePoints - those points which are adjacent to a different zone by (X,Z)
	for z in xrange(0,maxz-minz-1):
		for x in xrange(0,maxx-minx-1):
			if v[x][z][3] == 1 and v[x][z+1][3] == 1 and v[x+1][z][3] == 1:
				if  v[x][z][0] != v[x+1][z][0] or v[x][z][1] != v[x+1][z][1] or v[x][z][0] != v[x][z+1][0] or v[x][z][1] != v[x][z+1][1]: # If any of the rightmost/nextmost points are different, this is an edge
					edgePoints.append((x+minx,z+minz))
	log("Making walls")
	log(str(len(edgePoints)))
	COBBLESTONE = 4
	MOSSCOBBLESTONE = 48
	COBBLESTONEWALL = 139
	TORCH_UP = (50,5)		
	for x,z in edgePoints:
		if randint(1,10) > 5:
			y = level.Height
			while y >= 0:
				theBlockID,theBlockData = getBlock(level,x,y,z)
				if theBlockID == 2: # Grass
					if randint(1,10) < 0: # Shrubs and trees DISABLED
						LEAVES = (18,randint(0,11))
						LOG = (17,randint(0,3))
						ht = randint(1,6)
						for y1 in xrange(y,y+ht):
							setBlock(level,x,y1,z,LOG)
							for dx in range(-1,2):
								setBlock(level,x+dx,y1,z,LEAVES)
							for dz in range(-1,2):
								setBlock(level,x,y1,dz+dz,LEAVES)
						for y1 in xrange(y+ht,y+ht+(ht>>1)):
							setBlock(level,x,y1,z,LEAVES)								
					else:
						setBlock(level,x,y,z,(MOSSCOBBLESTONE,0))
						if randint(1,10) >2:
							setBlock(level,x,y+1,z,(COBBLESTONE,0))
							if randint(1,10) >5:
								setBlock(level,x,y+2,z,(COBBLESTONEWALL,randint(0,1)))
								if randint(1,10) >8:
									setBlock(level,x,y+3,z,TORCH_UP)
					y = 0 # Break. Job done
				y -= 1
				
			
	
	# Paths in the grass through resultAreas
	log("Making paths")
	heightW,heightD = heightMap.shape
	PATH = (208,0)
	pathCount = 20
	while pathCount > 0 and len(resultAreas) > pathCount:
		(box,flag) = resultAreas[randint(0,len(resultAreas)-1)]
		(box2,flag1) = resultAreas[randint(0,len(resultAreas)-1)]
		if flag and flag1 and box != box2:
			pathCount -= 1
			log("Pathing... "+str(pathCount))
			box1centrex = (box.maxx+box.minx)>>1
			box1centrez = (box.maxz+box.minz)>>1
			box2centrex = (box2.maxx+box2.minx)>>1
			box2centrez = (box2.maxz+box2.minz)>>1
			# Calculate the line from box1 to box 2
			P = []
			P.append((box1centrex,0,box1centrez))
			P.append(P[0])
			P.append((((box1centrex+box2centrex)>>1)+randint(-100,100),0,((box1centrez+box2centrez)>>1)+randint(-100,100)))
			P.append((box2centrex,0,box2centrez))
			P.append(P[len(P)-1])
			Q = calcLinesSmooth(4,P)
			for (x,y,z) in Q:
				x = x+randint(-2,2)
				z = z+randint(-2,2)
				if randint(1,10) > 3:
					y = level.Height
					while y >= 0:
						theBlockID,theBlockData = getBlock(level,x,y,z)
						if theBlockID == 2: # Grass
							setBlock(level,x,y,z,PATH)
							y = 0 # Break. Job done
						y -= 1
	return resultAreas # Tell the parent generator what we've done