# @TheWorldFoundry

import STARTPROC_v1 # Procedural tools / framework
from STARTPROC_v1 import fill,fillForced,log,checkBoundingBoxIntersect,getBlock,setBlock,copyAreaOfSizeWHDFromSchematicAtPosXYZ,delegateGeneration,pasteAreaOfSizeWHDToSchematicAtPosXYZ,makeBlankAreaOfSizeWHD,getDimensionsFromBox

from random import randint, shuffle
from pymclevel import alphaMaterials,MCSchematic,BoundingBox

class Room:
	def __init__(self, type, pos, size):
		self.type = type
		self.pos = pos
		w,h,d = size
		if type == "Tower":
			h += h
		if type == "LivingRoom":
			h += h>>1
		self.size = (w,h,d)
		
		self.schematic = None
			
	def placeRoom(self,level):
		width,height,depth = self.size

		ox,oy,oz = self.pos
		
		# Clear the space
		material = (0,0)
		fillForced(level,(ox,oy,oz),(ox+width,oy+height,oz+depth),material) # The rectangular prism for the room
		
		material = (4,0) # Cobblestone	
		# Floor
		fillForced(level,(ox,oy,oz),(ox+width,oy+1,oz+depth),material)
		# Ceiling

		if width >= depth or randint(1,10) > 9:
			material = (17,8) # Oak Wood North/South
			for i in xrange(0,width):
				if i%2 == 0:
					fillForced(level,(ox+i,oy+height-1,oz),(ox+i+1,oy+height,oz+depth),material)
		else:
			material = (17,4) # Oak Wood East/West
			for i in xrange(0,depth):
				if i%2 == 0:
					fillForced(level,(ox,oy+height-1,oz+i),(ox+width,oy+height,oz+i+1),material)
			
		# Walls
		material = (5,0) # Woodplanks
		if self.type == "Kitchen":
			material = (98,0) # Stone Brick
		fillForced(level,(ox,oy,oz),(ox+width,oy+height,oz+1),material) # Face front
		fillForced(level,(ox,oy,oz),(ox+1,oy+height,oz+depth),material) # Face left
		fillForced(level,(ox+width-1,oy,oz),(ox+width,oy+height,oz+depth),material) # Face right
		fillForced(level,(ox,oy,oz+depth-1),(ox+width,oy+height,oz+depth),material) # Face back
		vertOffset = 0
		if self.type == "Bedroom":
			material = (35,0) # Wool
			vertOffset = 1
		elif self.type == "Kitchen":
			material = (4,0) # Cobblestone
		else:
			material = (159,0) # Stained Clay
		fillForced(level,(ox+1,oy+1+vertOffset,oz),(ox-1+width,oy+height,oz+1),material) # Face front
		fillForced(level,(ox,oy+1+vertOffset,oz+1),(ox+1,oy+height,oz-1+depth),material) # Face left
		fillForced(level,(ox+width-1,oy+1+vertOffset,oz+1),(ox+width,oy+height,oz-1+depth),material) # Face right
		fillForced(level,(ox+1,oy+1+vertOffset,oz+depth-1),(ox-1+width,oy+height,oz+depth),material) # Face back

		
		# Roof
		material = (45,0) # Brick
		keepGoing = True
		step = 0
		roofPitch=randint(1,2)
		while keepGoing:
			xstep = step
			zstep = step
			if roofPitch == 1:
				xstep = 0
			else:
				zstep = 0
			px = ox-1+xstep
			px1 = ox+width+1-xstep
			py = oy+height-1+step
			py1 = oy+height+step
			pz = oz-1+zstep
			pz1 = oz+depth+1-zstep
			if px1 > px and pz1 > pz:
				fillForced(level,(px,py+1,pz),(px1,py1+1,pz1),material)
			else:
				keepGoing = False
			step += 1

		self.schematic = copyAreaOfSizeWHDFromSchematicAtPosXYZ(level, width, height, depth, ox, oy, oz)
			
	def furnish(self,level):
		# Based on the type of room, place things around.
		log("Furnishing...")
		AIR = (0,0)
		DOORS = [64]		
		(ox,oy,oz) = self.pos
		width,height,depth = self.size
		colortheme = randint(0,15)		
		if self.type == "Bedroom":
			# Place a bed

			# Bed. Location shouldn't be adjacent to a door. Find a spot with the head to a wall. Fair share of orientations
			BEDFOOTNORTH = (26,0)
			BEDFOOTEAST = (26,1)
			BEDFOOTSOUTH = (26,2)
			BEDFOOTWEST = (26,3)
			BEDHEADNORTH = (26,8)
			BEDHEADEAST = (26,9)
			BEDHEADSOUTH = (26,10)
			BEDHEADWEST = (26,11)

			
			# Walk the floor looking for a safe place to put a bed
			y = oy+1
			attempts = 100
			while attempts > 0:
				attempts -= 1
				x = randint(ox+1,ox+width-1)
				z = randint(oz+1,oz+depth-1)
				thisSpot = getBlock(level,x,y,z)
				if thisSpot == AIR:
					wid,wdata = westSpot = getBlock(level,x-1,y,z)
					eid,edata = eastSpot = getBlock(level,x+1,y,z)
					sid,sdata = southSpot = getBlock(level,x,y,z+1)
					nid,ndata = northSpot = getBlock(level,x,y,z-1)
					if westSpot != AIR and eastSpot == AIR and wid not in DOORS and nid not in DOORS and sid not in DOORS:
						eid,edata = eastSpot = getBlock(level,x+2,y,z)
						sid,sdata = southSpot = getBlock(level,x+1,y,z+1)
						nid,ndata = northSpot = getBlock(level,x+1,y,z-1)
						if eid not in DOORS and sid not in DOORS and nid not in DOORS:
							setBlock(level,x,y,z,BEDHEADEAST)
							setBlock(level,x+1,y,z,BEDFOOTEAST)
							attempts = 0
				
					elif eastSpot != AIR and westSpot == AIR and eid not in DOORS and nid not in DOORS and sid not in DOORS:
						wid,edata = westSpot = getBlock(level,x-2,y,z)
						sid,sdata = southSpot = getBlock(level,x-1,y,z+1)
						nid,ndata = northSpot = getBlock(level,x-1,y,z-1)
						if wid not in DOORS and sid not in DOORS and nid not in DOORS:
							setBlock(level,x,y,z,BEDHEADWEST)
							setBlock(level,x-1,y,z,BEDFOOTWEST)
							attempts = 0
				
					elif northSpot != AIR and southSpot == AIR and eid not in DOORS and wid not in DOORS and nid not in DOORS:
						wid,edata = westSpot = getBlock(level,x-1,y,z+1)
						eid,sdata = southSpot = getBlock(level,x+1,y,z+1)
						sid,ndata = northSpot = getBlock(level,x,y,z+2)
						if wid not in DOORS and sid not in DOORS and eid not in DOORS:
							setBlock(level,x,y,z,BEDHEADSOUTH)
							setBlock(level,x,y,z+1,BEDFOOTSOUTH)
							attempts = 0
					
					elif northSpot == AIR and southSpot != AIR and eid not in DOORS and wid not in DOORS and sid not in DOORS:
						wid,edata = westSpot = getBlock(level,x-1,y,z-1)
						eid,sdata = southSpot = getBlock(level,x+1,y,z-1)
						nid,ndata = northSpot = getBlock(level,x,y,z-2)
						if wid not in DOORS and eid not in DOORS and nid not in DOORS:
							setBlock(level,x,y,z,BEDHEADNORTH)
							setBlock(level,x,y,z-1,BEDFOOTNORTH)
							attempts = 0

		if self.type == "LivingRoom":	
			STAIRCHAIR = 53 # 0,1,2,3
			log("Chairs")
			placements = []
			for i in xrange(0,randint(2,8)):
				placements.append(STAIRCHAIR)
			y = oy+1
			attempts = 100
			while attempts > 0 and len(placements) > 0:
				attempts -= 1
				x = randint(ox+1,ox+width-1)
				z = randint(oz+1,oz+depth-1)
				thisSpot = getBlock(level,x,y,z)
				if thisSpot == AIR:
					wid,wdata = westSpot = getBlock(level,x-1,y,z)
					eid,edata = eastSpot = getBlock(level,x+1,y,z)
					sid,sdata = southSpot = getBlock(level,x,y,z+1)
					nid,ndata = northSpot = getBlock(level,x,y,z-1)
					if westSpot == AIR and eastSpot == AIR and southSpot == AIR and northSpot == AIR:
						block = placements.pop()
						setBlock(level,x,y,z,(block,randint(0,3)))

			

						
		if self.type == "Kitchen":			
			CRAFTINGTABLE = 58
			FURNACE = 61 # 2,3,4,5
			CAULDRON = 118 # 0,1,2,3
			log("Kitchen")
			placements = [CAULDRON,FURNACE,CRAFTINGTABLE]
			
			# Walk the floor looking for a safe place to put a crafting table
			y = oy+1
			attempts = 100
			while attempts > 0 and len(placements) > 0:
				attempts -= 1
				x = randint(ox+1,ox+width-1)
				z = randint(oz+1,oz+depth-1)
				thisSpot = getBlock(level,x,y,z)
				if thisSpot == AIR:
					wid,wdata = westSpot = getBlock(level,x-1,y,z)
					eid,edata = eastSpot = getBlock(level,x+1,y,z)
					sid,sdata = southSpot = getBlock(level,x,y,z+1)
					nid,ndata = northSpot = getBlock(level,x,y,z-1)
					if westSpot != AIR and eastSpot == AIR and wid not in DOORS and nid not in DOORS and sid not in DOORS:
						block = placements.pop()
						blockID = 0
						if block == CAULDRON:
							blockID = randint(0,3)
						elif block == FURNACE:
							blockID = 4
						setBlock(level,x,y,z,(block,blockID))
				
					elif eastSpot != AIR and westSpot == AIR and eid not in DOORS and nid not in DOORS and sid not in DOORS:
						block = placements.pop()
						blockID = 0
						if block == CAULDRON:
							blockID = randint(0,3)
						elif block == FURNACE:
							blockID = 5
						setBlock(level,x,y,z,(block,blockID))
						
					elif northSpot != AIR and southSpot == AIR and eid not in DOORS and wid not in DOORS and nid not in DOORS:
						block = placements.pop()
						blockID = 0
						if block == CAULDRON:
							blockID = randint(0,3)
						elif block == FURNACE:
							blockID = 3
						setBlock(level,x,y,z,(block,blockID))

						
					elif northSpot == AIR and southSpot != AIR and eid not in DOORS and wid not in DOORS and sid not in DOORS:
						block = placements.pop()
						blockID = 0
						if block == CAULDRON:
							blockID = randint(0,3)
						elif block == FURNACE:
							blockID = 2
						setBlock(level,x,y,z,(block,blockID))

						
		# All rooms - table and torch
		log("Chest")
		CHEST = 54
		y = oy+1
		attempts = 100
		while attempts > 0:
			attempts -= 1
			x = randint(ox+1,ox+width-1)
			z = randint(oz+1,oz+depth-1)
			thisSpot = getBlock(level,x,y,z)
			if thisSpot == AIR:
				wid,wdata = westSpot = getBlock(level,x-1,y,z)
				eid,edata = eastSpot = getBlock(level,x+1,y,z)
				sid,sdata = southSpot = getBlock(level,x,y,z+1)
				nid,ndata = northSpot = getBlock(level,x,y,z-1)
				if westSpot == AIR and eastSpot == AIR and southSpot == AIR and northSpot == AIR:
					setBlock(level,x,y,z,(CHEST,randint(2,5)))
					attempts = 0
		log("Light")
		TORCH_UP = (50,5)		
		#TABLE = (85,0) # Fence
		y = oy+1
		attempts = 100
		while attempts > 0:
			attempts -= 1
			x = randint(ox+1,ox+width-1)
			z = randint(oz+1,oz+depth-1)
			thisSpot = getBlock(level,x,y,z)
			if thisSpot == AIR:
				wid,wdata = westSpot = getBlock(level,x-1,y,z)
				eid,edata = eastSpot = getBlock(level,x+1,y,z)
				sid,sdata = southSpot = getBlock(level,x,y,z+1)
				nid,ndata = northSpot = getBlock(level,x,y,z-1)
				if westSpot == AIR and eastSpot == AIR and southSpot == AIR and northSpot == AIR:
					setBlock(level,x,y,z,(35,colortheme))
					setBlock(level,x,y+1,z,TORCH_UP)
					attempts = 0

		
		log("Carpet")
		# All rooms - Carpet
		CARPET = 171
		if randint(1,10) < 10: # Add carpet
			log("Adding carpet")
			offset = randint(1,3)
			fill(level,(ox+offset,oy+1,oz+offset),(ox+width-offset,oy+2,oz+depth-offset),(CARPET,colortheme))
		
	
class Plan:
	def __init__(self,size):
		self.size = size
		self.rooms = []
		
	def add(self, room): # This is an efficient packing problem
		# Try to place the new room in the floorplan
		# Rooms can overlap by one block for a shared wall
		# For this method we don't care much if there's a gap between rooms. Consider fixing this by growing a blobby room plan later.
		width,height,depth = self.size
		roomWidth,roomHeight,roomDepth = room.size
		
		# precheck - can it fit the available dimensions?
			
		widthGap = width-roomWidth-2
		heightGap = height-roomHeight
		depthGap = depth-roomDepth-2
		if widthGap < 1 or heightGap < 0 or depthGap < 1:
			return False # I cannot place this room in this plan because it is too big
		
		# Ok, now we can check if there's a spot to place the new room. Don't be too aggressive. We want interesting, not optimal
		attempts = 100
		while attempts >= 0:
			attempts -= 1
			xpos = randint(1,widthGap)
			zpos = randint(1,depthGap)
			
			collides = False
			i = 0
			while i < len(self.rooms):
				eachRoom = self.rooms[i]
				x,y,z = eachRoom.pos
				dx,dy,dz = eachRoom.size
				# Remember a 1 block overlap is legal when placing rooms so the adjustment is made to the calculation below
				if checkBoundingBoxIntersect((xpos+1,zpos+1,xpos+roomWidth-2,zpos+roomDepth-2),(x,z,x+dx,z+dz)) == True: # Fail - overlap
					collides = True
					i = len(self.rooms) # Found an exception, stop looping
				i += 1
			
			if collides == False: # We didn't hit anything so we can use this position
				room.pos = (xpos,0,zpos) # Base condition - just put it where it doesn't collide
				log("Trying to shuffle the room "+str(room.pos)+" "+str(room.size))
				# Now shuffle it into the centre until it collides with another room so it is adjacent to an existing room
				cx = width>>1 # Centre x
				cz = depth>>1 # Centre z

				keepGoing = True
				newPosx = xpos
				newPosz = zpos

				dx = newPosx-cx # Distance to centre
				dz = newPosz-cz # Distance to centre
				dirx = 0
				dirz = 0
				if dx < 0:
					dirx = 1
				if dx > 0:
					dirx = -1
				if dz < 0:
					dirz = 1
				if dz > 0:
					dirz = -1
				if dirz != 0 or dirx != 0: # We have some wiggle room
					counter = 100
					while keepGoing and counter > 0:
						counter -= 1
						newPosx -= dirx
						newPosz -= dirz
						if newPosx > 1 and newPosz > 1 and newPosx+roomWidth < width and newPosz+roomDepth < depth:
							while i < len(self.rooms):
								eachRoom = self.rooms[i]
								x,y,z = eachRoom.pos
								dx,dy,dz = eachRoom.size
								if checkBoundingBoxIntersect((newPosx+1,newPosz+1,newPosx+roomWidth-1,newPosz+roomDepth-1),(x,z,x+dx,z+dz)) == True: # Overlap
									# Smash!
									keepGoing = False
									i = len(self.rooms)
									room.pos = (newPosx,0,newPosz)
						else:
							keepGoing = False # Could collide anywhere. Just put it where we first wanted to.
				self.rooms.append(room)			
	
				attempts = -1 # Break out of the loop
				return True # Successful addition
		return False # We couldn't find a place to pop this room
		
		
def makeFloorPlan(box, blueprint):
	# For each of the room types in the blueprint, create a room and place it in a non-overlapping volume in the available space
	# If we can't manage non-overlapping, try going UP!
	# If we're completely stuck for available space, allow overlapping
	#
	# Return the list of rooms as aligned to the available volume, they need to be placed and furnished/lit, and styled according to the area
	width,height,depth = getDimensionsFromBox(box)
	
	minRoomSize = 5
	
	maxWidth = minRoomSize<<1
	maxHeight = minRoomSize
	maxDepth = minRoomSize<<1
	if maxWidth < minRoomSize:
		maxWidth = minRoomSize
	if maxDepth < minRoomSize:
		maxDepth = minRoomSize
	if maxWidth > width:
		maxWidth = width
	if maxDepth > depth:
		maxDepth = depth
	
	plan = Plan((width,height,depth))
	
	i = 0
	while i < len(blueprint):
		roomType = blueprint[i]
		maxRoomWidth = randint(minRoomSize,maxWidth)
		maxRoomDepth = randint(minRoomSize,maxDepth)
		
		room = Room(roomType,(0,0,0),(maxRoomWidth,minRoomSize,maxRoomDepth)) # Default volume for room, including walls floor, ceiling.
		# Put this new volume in the rooms list
		canPlace = plan.add(room)
		if canPlace == False:
			i = len(blueprint) # Stop iterating through the floorplan when we can't add another room
		i += 1
	# Now we have a floorplan we can return it
	return plan

def placeLighting(level):
	# Place lights around the exterior of the dwelling. Find external corners and attach to them
	y = 3
	AIR = (0,0)
	TORCH_EAST = (50,1)
	TORCH_WEST = (50,2)
	TORCH_SOUTH = (50,3)
	TORCH_NORTH = (50,4)
	TORCH_UP = (50,5)
	
	torchLocations = []
	for z in xrange(0,level.Length):
		for x in xrange(0,level.Width):
			blockHere = getBlock(level, x,y,z)
			if blockHere != AIR:
				blockEast = getBlock(level, x+1,y,z)
				blockWest = getBlock(level, x-1,y,z)
				blockSouth = getBlock(level, x,y,z+1)
				blockNorth = getBlock(level, x,y,z-1)
				if blockEast != AIR and blockSouth != AIR and blockWest == AIR and blockNorth == AIR:
					torchLocations.append((x-1,y,z, TORCH_WEST))
					torchLocations.append((x,y,z-1, TORCH_NORTH))
				elif blockEast == AIR and blockSouth != AIR and blockWest != AIR and blockNorth == AIR:
					torchLocations.append((x+1,y,z, TORCH_EAST))
					torchLocations.append((x,y,z-1, TORCH_NORTH))
				elif blockEast == AIR and blockSouth == AIR and blockWest != AIR and blockNorth != AIR:
					torchLocations.append((x+1,y,z, TORCH_EAST))
					torchLocations.append((x,y,z+1, TORCH_SOUTH))
				elif blockEast != AIR and blockSouth == AIR and blockWest == AIR and blockNorth != AIR:
					torchLocations.append((x-1,y,z, TORCH_WEST))
					torchLocations.append((x,y,z+1, TORCH_SOUTH))
	
	for (x,y,z,block) in torchLocations:
		setBlock(level,x,y,z,block)
		
def placeWindows(level):
	# This is at the HOUSE level because the windows are on exterior walls only
	# Punch through the level placing glass if the current block is an exterior wall facing the right way
	AIR = (0,0)
	GLASS = (20,0)
	y = 2 # Window height
	DOUBLEHEIGHTWINDOWS = False
	if randint (1,10) == 10:
		DOUBLEHEIGHTWINDOWS = True
	
	# tunnel width-wise
	z = randint(3,4)
	
	while z < level.Length:
		for x in xrange(1,level.Width-1):
			if getBlock(level,x,y,z) != AIR:
				if getBlock(level,x-1,y,z) == AIR:
					if getBlock(level,x+1,y,z) == AIR: # Behind and in front are air
						floorInFront = getBlock(level,x-1,0,z)
						floorBehind = getBlock(level,x+1,0,z)
						if (floorInFront == AIR and floorBehind != AIR) or (floorInFront != AIR and floorBehind == AIR):
							setBlock(level,x,y,z,GLASS)
							if DOUBLEHEIGHTWINDOWS:
								setBlock(level,x,y+1,z,GLASS)
				
		z += 2
		
	# Tunnel depth-wise
	
	# tunnel width-wise
	x = randint(3,4)
	
	while x < level.Width:
		for z in xrange(1,level.Length-1):
			if getBlock(level,x,y,z) != AIR:
				if getBlock(level,x,y,z-1) == AIR:
					if getBlock(level,x,y,z+1) == AIR: # Behind and in front are air
						floorInFront = getBlock(level,x,0,z-1)
						floorBehind = getBlock(level,x,0,z+1)
						if (floorInFront == AIR and floorBehind != AIR) or (floorInFront != AIR and floorBehind == AIR):
							setBlock(level,x,y,z,GLASS)
							if DOUBLEHEIGHTWINDOWS:
								setBlock(level,x,y+1,z,GLASS)
				
		x += 2

		
def placeDoors(level):
	# This is at the "HOUSE" level because the doors are common to rooms, and exterior walls
	# Punch through the level placing door if the current block is an exterior wall facing the right way
	AIR = (0,0)
	DOOREAST = (64,0) # bitwise or with 0x8 for the top
	DOOREASTTOP = (64,8) # bitwise or with 0x8 for the top
	DOORWEST = (64,2) # bitwise or with 0x8 for the top
	DOORWESTTOP = (64,10) # bitwise or with 0x8 for the top
	
	DOORSOUTH = (64,1) # bitwise or with 0x8 for the top
	DOORSOUTHTOP = (64,9) # bitwise or with 0x8 for the top
	DOORNORTH = (64,3) # bitwise or with 0x8 for the top
	DOORNORTHTOP = (64,11) # bitwise or with 0x8 for the top

	
	doorsPlaced = 0
	iterations = 0 # Iteration cap
	while doorsPlaced == 0 and iterations <= 3:
		y = 1 # Door height
		# tunnel width-wise
		z = randint(4-iterations,5)
		
		while z < level.Length:
			for x in xrange(1,level.Width-1):
				if getBlock(level,x,y,z) != AIR:
					if getBlock(level,x-1,y,z) == AIR:
						if getBlock(level,x+1,y,z) == AIR: # Behind and in front are air
							floorInFront = getBlock(level,x-1,0,z)
							floorBehind = getBlock(level,x+1,0,z)
							if floorBehind != AIR or floorInFront != AIR and getBlock(level,x-2,y,z) != DOOREAST:
								material = DOOREAST
								materialtop = DOOREASTTOP
								if randint(1,2) == 1:
									material = DOORWEST
									materialtop = DOORWESTTOP
								setBlock(level,x,y,z,material)
								setBlock(level,x,y+1,z,materialtop)
								doorsPlaced += 1
									
					
			z += randint(4-iterations,5-iterations)
			
		# Tunnel depth-wise
		
		# tunnel width-wise
		x = randint(4-iterations,5)
		
		while x < level.Width:
			for z in xrange(1,level.Length-1):
				if getBlock(level,x,y,z) != AIR:
					if getBlock(level,x,y,z-1) == AIR:
						if getBlock(level,x,y,z+1) == AIR: # Behind and in front are air
							floorInFront = getBlock(level,x,0,z-1)
							floorBehind = getBlock(level,x,0,z+1)
							if floorBehind != AIR or floorInFront != AIR and getBlock(level,x-2,y,z) != DOORSOUTH:
								material = DOORSOUTH
								materialtop = DOORSOUTHTOP
								if randint(1,2) == 1:
									material = DOORNORTH
									materialtop = DOORNORTHTOP
								setBlock(level,x,y,z,material)
								setBlock(level,x,y+1,z,materialtop)
								doorsPlaced += 1
					
			x += randint(4-iterations,5-iterations)
		iterations += 1
	
def create(generatorName,level,areas): 
	# NOTE: Assumption is that this level and box object starts from 0,0,0
	# i.e. we're working with a fresh scratchpad schematic and not directly against the world level
	# simplifies calculation of where to put rooms
	log("Generating a "+generatorName)
	while len(areas) > 0:
		(box,availableFlag) = areas.pop()
		width,height,depth = getDimensionsFromBox(box)
		log("Generating a "+generatorName+" at "+str(box))

		# A house is a collection of rooms.
		# Start with a floorplan to determine the room layout
		# - each room is a box-like thing with a pitched roof
		# - once assembled doors can be punched through
		# - Windows projected from the exterior faces of the box
		# - Chimney
		
		blueprint = ["Bedroom","Kitchen","LivingRoom","Bedroom","Tower","Bedroom","LivingRoom","Bedroom","Bedroom","LivingRoom","Bedroom","Bedroom","Tower"
					]
		
		log("Making a floor plan")
		plan = makeFloorPlan(box,blueprint)
		log("Placing the rooms")
		for room in plan.rooms:
			room.placeRoom(level) # Floor, walls, ceilings
			#furnishRoom(level,room)
			
		placeWindows(level)
		placeDoors(level)
		placeLighting(level)

		for room in plan.rooms:
			room.furnish(level)
		
		# Fill in the bottom of the area with stone bricks as a quick and easy generatorName

		# material = (35,randint(0,15))
		# fill(level,(box.minx,box.miny,box.minz),(box.maxx,box.miny+randint(height>>1,height),box.maxz),material)


		
		
		
		