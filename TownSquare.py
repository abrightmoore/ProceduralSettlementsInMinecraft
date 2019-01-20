# @TheWorldFoundry

import STARTPROC_v1 # Procedural tools / framework
from STARTPROC_v1 import fill,fillForced,log,getDimensionsFromBox, delegateGeneration,pasteAreaOfSizeWHDToSchematicAtPosXYZ,makeBlankAreaOfSizeWHD,getDimensionsFromBox

def create(generatorName,level,areas):
	log("Generating a "+generatorName)
	while len(areas) > 0:
		(box,availableFlag) = areas.pop()
		width,height,depth = getDimensionsFromBox(box)
		cw = width>>1
		cd = depth>>1
		log("Generating a "+generatorName+" at "+str(box))
		material = (0,0)
		fillForced(level,(box.minx,box.miny,box.minz),(box.maxx,box.maxy,box.maxz),material)
		
		# Fill in the bottom of the area with stone bricks as a quick and easy generatorName
		material = (98,0)
		fillForced(level,(box.minx,box.miny,box.minz),(box.maxx,box.miny+2,box.maxz),material)
		material = (0,0)
		fillForced(level,(box.minx+1,box.miny+1,box.minz+1),(box.maxx-1,box.miny+2,box.maxz-1),material)
		material = (0,0)
		fillForced(level,(box.minx+cw-1,box.miny+1,box.minz),(box.minx+cw+2,box.miny+2,box.maxz),material)
		fillForced(level,(box.minx,box.miny+1,box.minz+cd-2),(box.maxx,box.miny+2,box.minz+cd+2),material)
		material = (98,1)
		fillForced(level,(box.minx+cw-(cw>>1),box.miny+1,box.minz+cd-(cd>>1)),(box.minx+cw+(cw>>1),box.miny+2,box.minz+cd+(cd>>1)),material)
		material = (9,0)
		fillForced(level,(box.minx+cw-(cw>>1)+1,box.miny+1,box.minz+cd-(cd>>1)+1),(box.minx+cw+(cw>>1)-1,box.miny+2,box.minz+cd+(cd>>1)-1),material)		
		material = (98,1)
		delta = 6
		while delta > 0:
			fillForced(level,(box.minx+cw-delta,box.miny+1,box.minz+cw-delta),(box.maxx-cw+delta,box.miny+(height>>1)-delta*2,box.maxz-cd+delta),material)
			delta -= 1