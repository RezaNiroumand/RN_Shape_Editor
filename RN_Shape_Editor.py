#RN_Shape_Editor_v1.0########154####################################################

import pdb;
import maya.cmds as cmds
import maya.mel as mm
import os

blendshape_name = ""
edit_buttons = {}

#------------------------------------------------------------

def get_index_from_button_name(button_name):
	global edit_buttons
	for index in edit_buttons:
		print edit_buttons[index]
		if button_name in edit_buttons[index]:
			print "exist"
			print edit_buttons[index][-3:]
			return edit_buttons[index][-3:]
	return -1

#------------------------------------------------------------

def make_red_button():
	global blendshape_name
	global edit_buttons
	print "make red button..."
	red_button_index = cmds.getAttr(blendshape_name+'.inputTarget[0].sculptTargetIndex')
	
	for edit_button in edit_buttons:
		cmds.button(edit_buttons[edit_button], edit=True, bgc=[.364,.364,.364]) #turn all edit buttons grey	
	if red_button_index != -1:
		cmds.button(edit_buttons[str(red_button_index)], edit=True, bgc=[1,0,0])

#------------------------------------------------------------

def edit_pressed(index_edit):
	global blendshape_name
	print "change edit..."
	cmds.sculptTarget(blendshape_name, e=True, t=int(index_edit))
	make_red_button()

#------------------------------------------------------------

def delete_blend_shape(index_delete):
	global blendshape_name
	print "deleting..."
	print "deleting :"+str(index_delete)
	mm.eval('blendShapeDeleteTargetGroup '+blendshape_name+' '+str(index_delete)+';')
	edit_buttons.pop(str(index_delete))
	cmds.deleteUI("frameLayout")
	cmds.frameLayout("frameLayout",p="Shape_Editor",labelVisible=False)
	load_blend_shape()

#------------------------------------------------------------	

def set_keyframe(index_set_key):
	global blendshape_name
	print "setting keyframe..."
	print blendshape_name
	print blendshape_name+".w["+str(index_set_key)+"]"
	cmds.setKeyframe(blendshape_name+".w["+str(index_set_key)+"]")
	

#------------------------------------------------------------	

def get_index_by_name(blend_shape_name, targetName):
	targets_and_weights = cmds.aliasAttr(blendshape_name+'.w[]', q=True)
	i=0
	for target in targets_and_weights:
		if target == targetName:
			index = targets_and_weights[i+1]
			x=index.split('[')
			y = x[1][:-1]
			print y
			return y
		i = i+1
	return -1

#------------------------------------------------------------	

def blend_shape_exist(selection_string):
	a = cmds.listHistory(selection_string)
	exist = False
	for x in a:
		if "post_corrective_blendshape" in x:
			exist = True
	return exist


#------------------------------------------------------------

def switch_key_mesh(index_switch):
	global blendshape_name
	print "switching..."
	print "switching :"+str(index_switch)
	
	switch_target_name = cmds.listAttr( blendshape_name + '.w['+index_switch+']' , m=True )
	if len(cmds.ls(sl=1))==0 and blendshape_name!="":
		object_name = cmds.ls(cmds.listConnections(blendshape_name),type="transform")[0]
		cmds.select(object_name)		
	
	elif len(cmds.ls(sl=1))==1 and "post_corrective" in cmds.ls(sl=1)[0] and cmds.objectType(cmds.ls(sl=1)) == 'blendShape':
		object_name = cmds.ls(cmds.listConnections(blendshape_name),type="transform")[0]
		cmds.select(object_name)	
	
	elif len(cmds.ls(sl=1))==1 and "post_corrective" in cmds.ls(sl=1)[0] and cmds.objectType(cmds.ls(sl=1)) == 'animCurveTU' and blendshape_name!="":
		object_name = cmds.ls(cmds.listConnections(blendshape_name),type="transform")[0]
		cmds.select(object_name)	
	
	
	elif len(cmds.ls(sl=1))==1 and cmds.objectType(cmds.ls(sl=1)) == 'transform': 
		shape = cmds.listRelatives(cmds.ls(sl=1), shapes=True, noIntermediate=True)
		if len(cmds.ls(cmds.listConnections(shape[0]),type='blendShape')) != 0:
			blenshape_name = cmds.ls(cmds.listConnections(shape[0]),type='blendShape')[0]
			if "post_corrective" in blenshape_name:
				if cmds.objExists(blendshape_name+'_'+switch_target_name[0]):
					cmds.select(blendshape_name+'_'+switch_target_name[0])
				else:
					print "no keyframe"
			else:
				print "object dosen't have post corrective blend shape"						
	else:
		print "select post corrective mesh or blend shape"





#------------------------------------------------------------	

def load_row_UI(target_name,index_ui):
	global blendshape_name
	global edit_buttons
	print "loading UI..."
	cmds.rowLayout(numberOfColumns=8,p="frameLayout")
	cmds.separator( style='none',width=20)
	cmds.text(label=target_name)
	cmds.floatField( 'value' )
	cmds.connectControl( 'value', blendshape_name+'.'+target_name )
	cmds.floatSlider( 'slider',min=0,max=1,value=1)
	cmds.connectControl( 'slider', blendshape_name+'.'+target_name )
	
	edit_button = cmds.button(blendshape_name+"_"+str(index_ui).zfill(3),label="Edit",command=lambda _ignore: edit_pressed(str(index_ui)))
	
	edit_buttons[index_ui]=edit_button
	cmds.button(label="Set Key",command=lambda _ignore: set_keyframe(str(index_ui)))
	cmds.button(label="Delete",command=lambda _ignore: delete_blend_shape(str(index_ui)))
	cmds.button(label="Key/Mesh",command=lambda _ignore: switch_key_mesh(str(index_ui)))
	
#------------------------------------------------------------

def add_blend_shape():
	global blendshape_name
	print "adding blend shape..."
	selection_array = cmds.ls(sl=True)
	if (len(cmds.ls(sl=1))!=1):
		print "select one mesh object!"
	elif cmds.listRelatives(cmds.ls(sl=1))==None:
		print "select one mesh object!"
	elif not cmds.objectType(cmds.listRelatives(cmds.ls(sl=1))[0], isType="mesh"):
		print "select one mesh object!"
	else:
		selection_string = selection_array[0].split(":")[-1]
		blendshape_name = selection_string+"_post_corrective_blendshape"
		if not blend_shape_exist(selection_array[0]):
			cmds.blendShape(frontOfChain=True, name=blendshape_name)
		
		current_frame = int(cmds.currentTime(q=1))
		
		index = mm.eval('string $targetShapes[]; doBlendShapeAddTarget( "{}", 1, 3, "", 1, 0, $targetShapes );'.format(blendshape_name))
		
		target_name = "n"+str(index[0]).zfill(3)+"_"+selection_string+"_frame_"+str(current_frame).zfill(4)
		cmds.aliasAttr( target_name, blendshape_name+'.w['+str(index[0])+']')
		load_row_UI(target_name,str(index[0]))
		cmds.setAttr(blendshape_name+"."+target_name,1)
		make_red_button()

#------------------------------------------------------------

def load_blend_shape():
	print "loading blend shape..."
	global blendshape_name
	global edit_buttons
	edit_buttons = {}
	if (len(cmds.ls(sl=1))!=1):
		print "select one mesh object!"
	elif cmds.listRelatives(cmds.ls(sl=1))==None:
		print "select one mesh object!"
	elif not cmds.objectType(cmds.listRelatives(cmds.ls(sl=1))[0], isType="mesh"):
		print "select one mesh object!"
	else:
		
		selection_array = cmds.ls(sl=1)
		selection_string = selection_array[0]
		existing_blendshape_name = selection_string.split(":")[-1]+"_post_corrective_blendshape"
		print "finding existing blend shape"
		if existing_blendshape_name in cmds.listHistory(selection_string):
			blendshape_name = existing_blendshape_name
			existing_targetList = cmds.listAttr(blendshape_name+'.w',m=True)
			if existing_targetList != None:
				print "target found!"
				for target_name in existing_targetList:
					
					print "target_name :"+target_name
					index_load = get_index_by_name(blendshape_name,target_name)
					
					load_row_UI(target_name,index_load)
				
				
				print "check old sculpt index...."
				
				old_sculpt_index = cmds.getAttr(blendshape_name+'.inputTarget[0].sculptTargetIndex')
				if old_sculpt_index!=-1:
					make_red_button()
				
				print "end of target found!"
			else:
				print "no target found!"
		else:
			print "this object doesn't have a post corrective blendshape"

#------------------------------------------------------------

def select_node():
	if len(cmds.ls(sl=1))==1 and cmds.objectType(cmds.ls(sl=1)) == 'animCurveTU' and blendshape_name!="":
		object_name = cmds.ls(cmds.listConnections(blendshape_name),type="transform")[0]
		cmds.select(object_name)
	elif len(cmds.ls(sl=1))==0 and blendshape_name!="":
		object_name = cmds.ls(cmds.listConnections(blendshape_name),type="transform")[0]
		cmds.select(object_name)
	elif len(cmds.ls(sl=1))==1 and "post_corrective" in cmds.ls(sl=1)[0] and cmds.objectType(cmds.ls(sl=1)) == 'blendShape':
		object_name = cmds.ls(cmds.listConnections(cmds.ls(sl=1)),type="transform")[0]
		cmds.select(object_name)	
	elif len(cmds.ls(sl=1))==1 and cmds.objectType(cmds.ls(sl=1)) == 'transform': 
		shape = cmds.listRelatives(cmds.ls(sl=1), shapes=True, noIntermediate=True)
		if len(cmds.ls(cmds.listConnections(shape[0]),type='blendShape')) != 0:
			blenshape_name = cmds.ls(cmds.listConnections(shape[0]),type='blendShape')[0]
			if "post_corrective" in blenshape_name:
				cmds.select(blenshape_name)
			else:
				print "object dosen't have post corrective blend shape"						
	else:
		print "select post corrective mesh or blend shape"

#------------------------------------------------------------

def SelectionChanged():
    if(cmds.window("Shape_Editor", exists=True)):
    	if len(cmds.ls(sl=1))==1 and (cmds.objectType(cmds.ls(sl=1)) == 'transform'):
	    	cmds.deleteUI("frameLayout")
	    	cmds.frameLayout("frameLayout",p="Shape_Editor",labelVisible=False)
	    	load_blend_shape()

#------------------------------------------------------------

def add_annotation():	
	if len(cmds.ls(sl=1))==1 and cmds.objectType(cmds.ls(sl=1)[0])=="mesh" and "vtx[" in cmds.ls(sl=1)[0]:
		transform = cmds.ls(sl=1)[0].split('.')[0]
		shape = cmds.listRelatives(transform, shapes=True, noIntermediate=True)[0]
		
		if len(cmds.ls(cmds.listConnections(shape),type='blendShape')) != 0:
			blenshape_name = cmds.ls(cmds.listConnections(shape),type='blendShape')[0]
			if "post_corrective" in blenshape_name:
				annotation_text = blenshape_name
				selection = cmds.ls(sl=1)[0]
				annotate_name = cmds.annotate( selection, tx=annotation_text, p=(0, 0, 0) )
				cmds.setAttr(annotate_name+".displayArrow",0)
				group_name = cmds.group( em=True, name=annotation_text+"_annotate" )
				cmds.parent(annotate_name,group_name,s=True)
				cmds.select(selection,group_name)
				cmds.pointOnPolyConstraint()
				cmds.parent(group_name,selection.split('.')[:-1],s=True)
				cmds.delete(annotate_name.split("Shape")[0]+annotate_name.split("Shape")[1])
			else:
				print "mesh dosen't have post corrective blend shape"	
		else:
			print "mesh dosen't have post corrective blend shape"
	else:
		print "select one vertex of a object with post corrective blend shape to add annotation"

def show_help():
	
	directory = os.path.dirname(__file__)
	cmds.launch(movie=directory+"\RN_Shape_Editor_help.mov")

#------------------------------------------------------------

def shape_editor():
    if(cmds.window("Shape_Editor", exists=True)):
        cmds.deleteUI("Shape_Editor")
    cmds.cycleCheck(e=False)
    Shape_Editor=cmds.window("Shape_Editor",title="RN_Shape_Editor_v1.0", iconName='Short Name', resizeToFitChildren=True, widthHeight=(500, 300))
    cmds.scrollLayout( 'scrollLayout' )
    cmds.rowLayout(numberOfColumns=2)
    cmds.separator( style='none',height=40)
    cmds.rowLayout(numberOfColumns=8)
    cmds.separator( style='none',width=12)

    cmds.button(label="  add trget  ", command=lambda _ignore: add_blend_shape())
    cmds.separator( style='none',width=1)
    cmds.button(label="  switch blendshape/object  ", command=lambda _ignore: select_node())
    cmds.separator( style='none',width=1)
    cmds.button(label="  add annotation to vertex  ", command=lambda _ignore: add_annotation())
    cmds.separator( style='none',width=1)
    cmds.button(label="  help  ", command=lambda _ignore: show_help())
    cmds.setParent( '..' )
    cmds.setParent( '..' )
    cmds.frameLayout("frameLayout",labelVisible=False)
    cmds.showWindow()
    myScriptJobID = cmds.scriptJob(event=["SelectionChanged", lambda: SelectionChanged()], p="Shape_Editor")
    SelectionChanged()

#------------------------------------------------------------

shape_editor()


#154##########################################################
