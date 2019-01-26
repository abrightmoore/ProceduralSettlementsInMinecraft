# @TheWorldFoundry

# Builds a farm of crop type

from pymclevel import alphaMaterials,BoundingBox
from random import random,randint,Random
import STARTPROC_v1 # Procedural tools / framework
from STARTPROC_v1 import getBlock,setBlock,fill,log, delegateGeneration,pasteAreaOfSizeWHDToSchematicAtPosXYZ,makeBlankAreaOfSizeWHD,getDimensionsFromBox

def chopUpBoxes2D(R,boxes,MINW,MIND):
	newBoxes = []
	for (x,z,w,d) in boxes:
		if w > MINW and d > MIND:
			# Bisect
			if w > d: # Vertical chop
				newW = R.randint(w>>2,w-(w>>2))
				newBox1 = (x,z,newW,d)
				newBox2 = (x+newW,z,w-newW,d)
				newBoxes.append(newBox1)
				newBoxes.append(newBox2)
			else: # Horizontal chop
				newD = R.randint(d>>2,d-(d>>2))
				newBox1 = (x,z,w,newD)
				newBox2 = (x,z+newD,w,d-newD)
				newBoxes.append(newBox1)
				newBoxes.append(newBox2)
		else:
			newBoxes.append((x,z,w,d))
	return newBoxes
	
def Farmland(level,box):
	crops = [ (0,0),(59,0),(59,1),(59,2),(59,3),(59,4),(59,5),(59,6),(59,7),
				(142,0),(142,1),(142,2),(142,3),(142,4),(142,5),(142,6),(142,7),
				(141,0),(141,1),(141,2),(141,3),(141,4),(141,5),(141,6),(141,7),
				# (207,0),(207,1),(207,2),(207,3), # <- This block is ICE on PE and so cannot be used
				(31,1)
			]
	
	CROPS = "RANDOM"
	CROPS_MAT = crops[randint(0,len(crops)-1)]
	
	FARM_MAT = (60,7) 
	EDGE_MAT = (3,0)
	WATER_MAT = (9,0)
	WATERCOVER_MAT = (111,0)
	FENCE_MAT = (85,0)
	SURFACE_MAT = (2,0)
	AIR = (0,0)
	
	(midx,midz) = ((box.minx+box.maxx)>>1,(box.minz+box.maxz)>>1)
	
	# Find the surface blocks
	(surfid,surfdata) = SURFACE_MAT
	surfaceBlocks = []
	for z in xrange(box.minz,box.maxz):
		if z%100 ==0: print "Processing Row: ",z
		for x in xrange(box.minx,box.maxx):
			for y1 in xrange(0,box.maxy-box.miny):
				y = box.maxy-y1-1
				(bid,bdata) = getBlock(level,x,y,z)
				if bid == surfid:
					blockAbove = getBlock(level,x,y+1,z)
					if blockAbove == AIR:
						surfaceBlocks.append((x,y,z))
						break # Found the top of this column, move on
				if bid == 31 and CROPS == "RANDOM":
					setBlock(level,x,y,z,AIR)
	
	# Now, for each of the locations we found, flip to farmland and put the crop on top
	
	print "Found ",len(surfaceBlocks)," blocks. Springtime planting underway"
	
	for (x,y,z) in surfaceBlocks:
		if x == box.minx or x == box.maxx-1 or z == box.minz or z == box.maxz-1:
			if random() > 0.4:
				setBlock(level, x, y+1, z, FENCE_MAT)
			if random() > 0.7:
				setBlock(level, x, y, z, EDGE_MAT)
		else:
			setBlock(level, x, y, z, FARM_MAT)

			if (x-midx)%5 == 0 and (z-midz)%5 == 0: # Place water?
				bw = getBlock(level,x-1,y,z)
				be = getBlock(level,x+1,y,z)
				bn = getBlock(level,x,y,z-1)
				bs = getBlock(level,x,y,z+1)
				if bw != AIR and be != AIR and bn != AIR and bs != AIR:
					setBlock(level, x, y, z, WATER_MAT)
					if getBlock(level, x, y+1, z) == AIR:
						setBlock(level, x, y+1, z, WATERCOVER_MAT)
			else:
				setBlock(level, x, y+1, z, CROPS_MAT)
	
	print "Complete"

# @TheWorldFoundry

def create(generatorName,level,areas):
	log("Generating a "+generatorName)
	while len(areas) > 0:
		(box,availableFlag) = areas.pop()
		width,height,depth = getDimensionsFromBox(box)
		log("Generating a "+generatorName+" at "+str(box))
		
		MINW = width-2
		MIND = depth-2
		SEED = randint(1000000000,9999999999)
		R = Random(SEED) # Seed goes here
		firstBox = (box.minx,box.minz,box.maxx-box.minx,box.maxz-box.minz)
		h = box.maxy-box.miny
		boxes = [firstBox]
		for i in xrange(0,randint(1,5)):
			boxes = chopUpBoxes2D(R,boxes,MINW,MIND)
		
		for (x,z,w,d) in boxes:
			Farmland(level,BoundingBox((x,box.miny,z),(w,h,d)))

					