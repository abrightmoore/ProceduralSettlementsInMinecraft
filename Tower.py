import STARTPROC_v1 # Procedural tools / framework
from STARTPROC_v1 import log, getDimensionsFromBox, setBlock, getBlock
from random import randint

def create(generatorName,level,areas): 
	'''
		We are passed:
		- a string naming this method as 'generatorName',
		- a pymclevel "level" or MCSchematic object as 'level',
		- and a list of (BoundingBox,flag) tuples as 'areas'
	'''
	
	log("Generating a "+generatorName) # Dump a message to the console

	# Some useful material definitions
	AIR = (0,0)
	STONEBRICKS = (98,1)
	COBBLESTONE = (4,0)
	BRICKS = (45,0)
	WOODPLANKS = (5,0)
	FLOORHEIGHT = 5

	while len(areas) > 0: # Iterate through the possible build plot areas we were passed.
		(box,availableFlag) = areas.pop() # Select the first area BoundingBox
		if availableFlag == True: # Confirm we're allowed to use it
			log("Generating a "+generatorName+" at "+str(box)) # Informational to show we found a plot to build in
			width,height,depth = getDimensionsFromBox(box) # Find out how much space we've been given
			if width >= 16 and depth >= 16: # Minimum viable generation space
				cx = width>>1 # Pre-calculate the centre via halving through a bit shift
				cz = depth>>1 # Pre-calculate the centre via halving through a bit shift
				
				
				# A tower is a cylinder with a hat on it.
				towerHeight = height # This is a normal tower with a flat roof
				if randint(1,10) > 7:
					towerHeight = int(height/3*2) # Leave 33% room for the roof otherwise 
				
				radius = cx-(cx>>1) # Push the tower wall into the box
				r2 = radius * radius # Square of the radius. We'll use this a little later to work out if we are in or outside the tower wall
				for y in xrange(0,towerHeight):
					for z in xrange(0,depth):
						dz = z-cz # distance to centre on z axis
						ddz = dz*dz # pre-calculate the distance squared
						for x in xrange(0,width):
							dx = x-cx # distance to centre on x axis
							ddx = dx*dx # pre-calculate the distance squared
							dist2 = ddx+ddz # square of the distance. No need to square-root this
							if dist2 <= r2: # We're within the tower
								material = AIR # Default to overwriting the tower space with air
								if dist2 > r2-16: # This is the wall thickness
									material = STONEBRICKS # Wall
								else: # Inside the wall within a room. Put a floor at this offset
									if y%FLOORHEIGHT == 1: material = WOODPLANKS
								if y == 0 or (material != AIR and width > 16 and randint(1,10) == 1): material = COBBLESTONE # Bottom layer cobblestone which is allows us to pack in empty space below
								
								setBlock(level,box.minx+x,box.miny+y,box.minz+z,material) # Clear the block from this position regardless of what it is
				# Draw the roof, if this tower has one
				for y in xrange(towerHeight, height):
					scalingRatio = 1.0-float(y-towerHeight)/float(height-towerHeight) # this works out how much to taper the radius
					rad = (cx/3*2)*scalingRatio
					r2 = int(rad*rad) # The radius gets smaller the higher we go
					for z in xrange(0,depth):
						dz = z-cz # distance to centre on z axis
						ddz = dz*dz # pre-calculate the distance squared
						for x in xrange(0,width):
							dx = x-cx # distance to centre on x axis
							ddx = dx*dx # pre-calculate the distance squared
							dist2 = ddx+ddz # square of the distance. No need to square-root this
							if dist2 <= r2: # We're within the roof
								material = BRICKS
								setBlock(level,box.minx+x,box.miny+y,box.minz+z,material) # Draw the roof

				# Window features and doorways
				towerRadius = radius>>1
				for y in xrange(0,towerHeight):
					# Randomly punch windows through
					if y%FLOORHEIGHT == 3 or y == 2: # y == 2 for ground floor access
						for x in xrange(cx-towerRadius+1,cx+towerRadius):
							if x != cx:
								if randint(1,10) == 1:
									hitWall = False
									for z in xrange(0,depth): # Drill through
										theBlock = getBlock(level, box.minx+x, box.miny+y, box.minz+z)
										if theBlock != AIR and hitWall == False:
											hitWall = False
											setBlock(level, box.minx+x, box.miny+y, box.minz+z, AIR)
											setBlock(level, box.minx+x, box.miny+y+1, box.minz+z, AIR)
											z = depth
								
						for z in xrange(cz-towerRadius+1,cz+towerRadius):
							if z != cz:
								if randint(1,10) == 1:
									hitWall = False
									for x in xrange(0,width): # Drill through
										theBlock = getBlock(level, box.minx+x, box.miny+y, box.minz+z)
										if theBlock != AIR and hitWall == False:
											hitWall = False
											setBlock(level, box.minx+x, box.miny+y, box.minz+z, AIR)
											setBlock(level, box.minx+x, box.miny+y+1, box.minz+z, AIR)
											x = width
							
			















