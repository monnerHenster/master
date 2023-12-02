import bpy
import time
import random
from .ReampArmature import *
import math
from bpy_extras.io_utils import ExportHelper
from . import decoder
from . import encoder
from . import tz
from . import config
from .common import *

ik_bones = config.ik_bones
def select_mode(obj,mode):
    scn = bpy.context.scene
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    obj.hide_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(state=True)
    bpy.ops.object.mode_set(mode=mode)

def build_bones_map():
    scn = bpy.context.scene
    scn.my_bones_map.clear()
    for chain_idx,chain_item in enumerate(scn.my_chain_map):
        if chain_item.name:
            # try:
            # print(chain_item.source_chain)
            for source_bone,target_bone in zip(chain_item.source_chain.split(','),chain_item.name.split(',')):
                item = scn.my_bones_map.add()
                item.source_bone = source_bone
                item.name = target_bone


                # for bone_idx,bone_item in enumerate(scn.my_target_chains[scn.my_target_chains.find(chain_item.name)].bone_chain):
                #     item = scn.my_bones_map.add()
                #     item.source_bone = scn.my_source_chains[scn.my_source_chains.find(chain_item.source_chain)].bone_chain[bone_idx].name
                #     item.name = bone_item.name

                if chain_item.is_root:
                    item.is_root = True
            # except Exception:
            #     print("error bone",bone_item.name)
def create_edit_bone(bone_name,arm=None,coll_name = None,color=None):
    eb = bpy.context.active_object.data.edit_bones.get(bone_name)
    if not eb:
        eb = bpy.context.active_object.data.edit_bones.new(bone_name)
    if coll_name:
        set_bone_layer(arm,eb,coll_name)
    if color:
        eb.color.palette = color
    return eb

def set_bone_layer(arm,editbone, coll_name, multi=False):
    try:
        arm.data.collections[coll_name].assign(editbone)
    except:
        arm.data.collections.new(coll_name)
        arm.data.collections[coll_name].assign(editbone)

def create_constraint(rig,bone_name,cst_name,type):
    for cnsts in rig.pose.bones[bone_name].constraints:
        if cnsts.name == cst_name:
            return cnsts
    cst = rig.pose.bones[bone_name].constraints.new(type)
    cst.name = cst_name
    return cst

def bake_root_action(source_rig,target_rig):
    bpy.context.view_layer.update()
    select_mode(source_rig,'POSE')
    bpy.ops.pose.select_all(action='SELECT')
    if source_rig.animation_data:
        i = 0
        while i < 2:
            copy_transforms_all(source_rig,target_rig)
            bpy.context.view_layer.update()

            select_mode(target_rig,'POSE')
            bpy.ops.pose.select_all(action='SELECT')

            bpy.context.view_layer.update()

            bpy.ops.nla.bake(
            frame_start=int(target_rig.animation_data.action.frame_range[0]),
            frame_end=int(target_rig.animation_data.action.frame_range[1]),
            step=1,
            only_selected=True,
            visual_keying=True,
            clear_constraints = True,
            bake_types={'POSE'}
            )
            bpy.context.view_layer.update()
            i += 1

def duplicate(obj, data=True, actions=True, collection=None):
    obj_copy = obj.copy()
    if data:
        obj_copy.data = obj_copy.data.copy()
    if actions and obj_copy.animation_data:
        obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
    bpy.context.collection.objects.link(obj_copy)
    return obj_copy

def make_foot_IK(ik_bones,left_right):
    for bone in ik_bones:
        # 先处理左边再处理右边
        if bone['left_right'] == left_right:
            if bone['role'] == 'calf':
                ik_bone_calf = create_edit_bone(bone['name']+'_IK')
            if bone['role'] == 'foot':
                bone_foot = create_edit_bone(bone['name'])
                ik_bone_foot = create_edit_bone(bone['name']+'_IK')
                ik_bone_foot_rotate = create_edit_bone(bone['name']+'_IK_rotate',1)
                ik_bone_foot_bottom = create_edit_bone(bone['name']+'_IK_bottom',1)
            if bone['role'] == 'toe':
                ik_bone_toe = create_edit_bone(bone['name']+'_IK')

    ik_bone_calf.parent = ik_bone_foot_rotate

    ik_bone_foot_rotate.head = ik_bone_foot_rotate.tail = ik_bone_foot.head[:]
    ik_bone_foot_rotate.tail += Vector((0,20,0))

    ik_bone_foot_bottom.head = ik_bone_foot_bottom.tail = ik_bone_foot.head[:]
    ik_bone_foot_bottom.head += Vector((0,0,-2))
    ik_bone_foot_bottom.tail = ik_bone_foot_bottom.head + Vector((0,20,0))

    ik_bone_foot_rotate.parent = ik_bone_foot.parent = ik_bone_toe.parent = ik_bone_foot_bottom
    
def set_armature_layer(object,collection_name=None,Viewtype=None):
    if type(Viewtype) == bool:
        for bcoll in object.data.collections:
            bcoll.is_visible = Viewtype
    if collection_name :
        for bcoll in object.data.collections:
            if bcoll.name == collection_name:
                bcoll.is_visible = True
            else:
                bcoll.is_visible =False

def _set_source_rig():
    scn = bpy.context.scene
    source_rig = ''
    if (scn.source_rig == '' or (bpy.data.objects.get(scn.source_rig).name not in bpy.context.scene.objects)) and bpy.context.selected_objects:
        source_rig = bpy.context.selected_objects[0].name
    else:
        source_rig = scn.source_rig
    scn.source_rig = source_rig
    scn.my_source_rig = bpy.data.objects.get(scn.source_rig)
        
class AN_PT_PanelIK(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "IK Operator"
    bl_category = "AniTool"
    bl_idname = "IK_PT_Operator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        for index,button in enumerate(ik_button):
            if index >= 0 and index%2 == 0:
                row = self.layout.row()
            if hasattr(button,'bl_label_dynamic'):
                row.operator(button.bl_idname,text=button.bl_label_dynamic)
            else:
                row.operator(button.bl_idname)

class AN_PT_PanelIK_Bone(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "IK Bone Set"
    bl_parent_id = "IK_PT_Operator"
    bl_category = "AniTool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        scn = bpy.context.scene
        row = self.layout.row()

        row.label(text='Source Armature')
        
class AN_OT_AddIKBone(bpy.types.Operator):
    bl_idname = 'an.add_ikbone'
    bl_label = 'Add IKBone'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        build_bones_map()

        global ik_bone
        ik_bone_list = ik_bone.split(',')
        select_mode(scn.my_source_rig,'EDIT')
        for bone in ik_bone_list:
            bone_IK = create_edit_bone(bone+'_IK')
            bone_foot = bpy.context.object.data.edit_bones.get(bone)
            bone_IK.head = bone_foot.tail
            bone_IK.tail = bone_IK.head[:]
            bone_IK.tail[1] += 20

            bone_IK_Pole = create_edit_bone(bone+'_IK_Pole')
            bone_IK_Pole.parnet = bone_IK
            bone_foot = bpy.context.object.data.edit_bones.get(bone)
            bone_IK_Pole.head = bone_foot.head
            bone_IK_Pole.tail = bone_IK_Pole.head[:]
            if bone.find('_l'):
                move_way = 20
            else:
                move_way = -20
            bone_IK_Pole.tail[1] += move_way

        bpy.context.view_layer.update()        
        select_mode(scn.my_source_rig,'POSE')
        for bone in ik_bone_list:
            bone_IK = scn.my_source_rig.pose.bones.get(bone+'_IK')
            cst = create_constraint(scn.my_source_rig,bone_IK.name,'Copy Transform IK','COPY_LOCATION')
            cst.target = scn.my_source_rig
            cst.head_tail = 1
            cst.subtarget = bone

            bone_IK_Pole = scn.my_source_rig.pose.bones.get(bone+'_IK_Pole')
            cst = create_constraint(scn.my_source_rig,bone_IK_Pole.name,'Copy Transform IK','COPY_LOCATION')
            cst.target = scn.my_source_rig
            cst.head_tail = 1
            cst.subtarget = bone

        temp_source_rig = duplicate(scn.my_source_rig)
        bpy.context.view_layer.update()
        select_mode(scn.my_source_rig,'POSE')
        bpy.ops.pose.select_all(action='SELECT')

        bake_root_action(temp_source_rig,scn.my_source_rig)
        select_mode(temp_source_rig,'OBJECT')
        bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
        bpy.ops.object.delete()

        select_mode(scn.my_source_rig,'POSE')
        for bone in ik_bone_list:
            cst = create_constraint(scn.my_source_rig,bone,'IK_Anitool','IK')
            cst.target = scn.my_source_rig
            cst.subtarget = bone+'_IK'
            cst.chain_count = 2 
            cst.pole_target = scn.my_source_rig
            cst.pole_subtarget = bone+'_IK_Pole'

        select_mode(scn.my_source_rig,'OBJECT')
        return {'FINISHED'}
    
class AN_OT_AddTempIKBone(bpy.types.Operator):
    bl_idname = 'an.add_temp_ikbone'
    bl_label = 'Add Temp IKBone'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        build_bones_map()

        global ik_bones
        select_mode(scn.my_source_rig,'EDIT')
        set_armature_layer(scn.my_source_rig,Viewtype=True)
        # create ik bones
        for bone in ik_bones:
            if bone['type'] == 'IK':
                bone_IK = create_edit_bone(bone['name']+'_IK','ik controls')
                # bone_IK = create_edit_bone(bone['name']+'_IK',1)
                bone_target = bpy.context.object.data.edit_bones.get(bone['name'])
                bone_IK.head = bone_IK.tail = eval('bone_target.'+bone['edit_bone_head'])[:]
                bone_IK.tail += bone['edit_offset']

            if bone['type'] == 'Transform':
                # duplicate original bone and child it
                bone_IK_Transfrom = create_edit_bone(bone['name']+'_IK_Transform','ik controls')
                bone_target = bpy.context.object.data.edit_bones.get(bone['name'])
                bone_IK_Transfrom.head = bone_target.head[:]
                bone_IK_Transfrom.tail = bone_target.tail[:]
                bone_IK_Transfrom.matrix = bone_target.matrix
                
            if bone['pole_bone']:
                bone_IK_Pole = create_edit_bone(bone['name']+'_IK_Pole','ik controls')
                bone_IK_Pole.parent = bone_IK
                bone_target = bpy.context.object.data.edit_bones.get(bone['name'])
                bone_IK_Pole.head = bone_target.head
                bone_IK_Pole.tail = bone_IK_Pole.head[:]
                bone_IK_Pole.tail[1] += 20

        # create foot whole ik
        make_foot_IK(ik_bones,'left')
        make_foot_IK(ik_bones,'right')

        select_mode(scn.my_source_rig,'POSE')
        # move parent to pose location
        for bone in ik_bones:
            if bone['role'] == 'foot':
                bone_IK = scn.my_source_rig.pose.bones.get(bone['name']+'_IK_bottom')
                cst = create_constraint(scn.my_source_rig,bone_IK.name,'Copy Transform IK','COPY_LOCATION')
                cst.target = scn.my_source_rig
                cst.head_tail =0
                cst.subtarget = bone['child_bone']
                bpy.context.object.data.bones.active = bone_IK.bone
                bone_IK.bone.select = True
                bpy.ops.constraint.apply(constraint=cst.name, owner='BONE')

        # move child to pose location
        for bone in ik_bones:
            if bone['type'] == 'IK':
                bone_IK = scn.my_source_rig.pose.bones.get(bone['name']+'_IK')
                cst = create_constraint(scn.my_source_rig,bone_IK.name,'Copy Transform IK','COPY_LOCATION')
                cst.target = scn.my_source_rig
                cst.head_tail =bone['head_tail']
                cst.subtarget = bone['name']
                bpy.context.object.data.bones.active = bone_IK.bone
                bone_IK.bone.select = True
                bpy.ops.constraint.apply(constraint=cst.name, owner='BONE')
            
            if bone['pole_bone']:
                bone_IK_Pole = scn.my_source_rig.pose.bones.get(bone['name']+'_IK_Pole')
                cst = create_constraint(scn.my_source_rig,bone_IK_Pole.name,'Copy Transform IK','COPY_LOCATION')
                cst.target = scn.my_source_rig
                cst.head_tail = 0
                cst.subtarget = bone['pole_bone']
                bpy.context.object.data.bones.active = bone_IK_Pole.bone
                bone_IK_Pole.bone.select = True
                bpy.ops.constraint.apply(constraint=cst.name, owner='BONE')
                bone_IK_Pole.location += bone['pole_loc']

            if bone['type'] == 'Transform':
                bone_IK = scn.my_source_rig.pose.bones.get(bone['name']+'_IK_Transform')
                cst = create_constraint(scn.my_source_rig,bone_IK.name,'Copy Transform IK','COPY_TRANSFORMS')
                cst.target = scn.my_source_rig
                cst.head_tail =bone['head_tail']
                cst.subtarget = bone['name']
                bpy.context.object.data.bones.active = bone_IK.bone
                bone_IK.bone.select = True
                bpy.ops.constraint.apply(constraint=cst.name, owner='BONE')

        # add IK constraints
        select_mode(scn.my_source_rig,'POSE')
        for bone in ik_bones:
            if bone['type'] == 'IK':
                cst = create_constraint(scn.my_source_rig,bone['name'],'IK_Anitool','IK')
                cst.target = scn.my_source_rig
                cst.subtarget = bone['name']+'_IK'
                cst.chain_count = bone['chain'] 

            if bone['pole_bone']:
                cst.pole_target = scn.my_source_rig
                cst.pole_subtarget = bone['name']+'_IK_Pole'
                cst.pole_angle = bone['pole']
                cst.use_tail = bone['use_tail']

            if bone['type'] == 'Transform':
                cst = create_constraint(scn.my_source_rig,bone['name'],'IK_Anitool','COPY_TRANSFORMS')
                cst.target = scn.my_source_rig
                cst.subtarget = bone['name']+'_IK_Transform'

        set_armature_layer(1)
        select_mode(scn.my_source_rig,'POSE')
        # bpy.ops.an.toggle_ik()

        return {'FINISHED'}
    
class AN_OT_ToggleIK(bpy.types.Operator):
    bl_idname = 'an.toggle_ik'
    # global Toggle_IK_State
    bl_label = 'Toggle IK'
    bl_options = {'UNDO'}
    bl_label_dynamic = 'Toggle IK Off'

    def execute(self, context):
        global Toggle_IK_State
        scn = bpy.context.scene
        select_mode(scn.my_source_rig,'POSE')
        # check enabled
        for bone in scn.my_source_rig.pose.bones:
            for csts in bone.constraints:
                if csts.name == 'IK_Anitool':
                    if csts.enabled == True:
                        Toggle_IK_State = False
                        self.__class__.bl_label_dynamic = 'Toggle IK On'
                    else:
                        Toggle_IK_State = True
                        self.__class__.bl_label_dynamic = 'Toggle IK Off'
                        break

        # set on or off
        for bone in scn.my_source_rig.pose.bones:
            for csts in bone.constraints:
                if csts.name == 'IK_Anitool':
                    csts.enabled = Toggle_IK_State

        return {'FINISHED'}
    
class AN_OT_LinkIKBones(bpy.types.Operator):
    bl_idname = 'an.link_ik_bone'
    bl_label = 'link ik bones'
    bl_options = {'UNDO'}

    def execute(self, context):
        global ik_bones
        scn = bpy.context.scene
        # _set_source_rig()
        source_rig = scn.my_source_rig
        select_mode(scn.my_source_rig,'EDIT')

        # create ik help and ik bones
        for bone in ik_bones:
            if type(bone['child_bone']) == str:
                link_bone_parent = copy_edit_bone(bone['name'],bone['name']+'_ik_rep')
                create_edit_bone(link_bone_parent.name,arm=scn.my_source_rig,coll_name='ik_rep',color='THEME01')
                link_bone_child = create_edit_bone(bone['child_bone'])
                link_bone_parent.tail = link_bone_child.head[:]
                link_bone_parent.parent = create_edit_bone(bone['name']).parent

                link_bone_help = copy_edit_bone(bone['name']+'_ik_rep',bone['name']+'_ik_rep_help')
                link_bone_help.parent = create_edit_bone(bone['name'])
                create_edit_bone(link_bone_help.name,arm=scn.my_source_rig,coll_name='ik_rep_help',color='THEME03')

            # elif type(bone['child_bone']) == Vector:
            #     link_bone_parent = copy_edit_bone(bone['name'],bone['name']+'_ik_rep')
            #     create_edit_bone(link_bone_parent.name,arm=scn.my_source_rig,coll_name='ik_rep',color='THEME01')
            #     link_bone_parent.tail = link_bone_parent.head + bone['child_bone']
            #     link_bone_parent.parent = create_edit_bone(bone['name'])

        # check if already done
        select_mode(scn.my_source_rig,'POSE')
        ik_ebone_help = []
        ik_ebone_help_all = [a.name for a in source_rig.data.collections['ik_rep_help'].bones]
        select_mode(scn.my_source_rig,'EDIT')
        for ebone_name in ik_ebone_help_all:
            if create_edit_bone(ebone_name.replace('_ik_rep_help','')).parent != create_edit_bone(ebone_name.replace('_help','')):
                ik_ebone_help.append(ebone_name) 

        if len(ik_ebone_help) == 0:
            select_mode(scn.my_source_rig,'POSE')
            return {'FINISHED'}
        
        # copy transform and bake to ik rep
        select_mode(scn.my_source_rig,'POSE')
        for eb in scn.my_source_rig.data.collections['ik_rep'].bones:
            cst = scn.my_source_rig.pose.bones[eb.name].constraints.new('COPY_TRANSFORMS')
            cst.target = scn.my_source_rig
            cst.subtarget = eb.name+'_help'

        bpy.ops.pose.select_all(action='DESELECT')
        for eb in scn.my_source_rig.data.collections['ik_rep'].bones:
            eb.select = True
        bpy.ops.nla.bake(
            frame_start=int(scn.my_source_rig.animation_data.action.frame_range[0]),
            frame_end=int(scn.my_source_rig.animation_data.action.frame_range[1]),
            step=1,
            only_selected=True,
            visual_keying=True,
            clear_constraints = True,
            use_current_action = True,
            bake_types={'POSE'}
            )
        
        # select_mode(scn.my_source_rig,'POSE')
        # ik_ebone_help_list = []
        # for ebone in source_rig.data.collections['ik_rep_help'].bones:
        #     ik_ebone_help_list.append(ebone.name)

        # change origin bone's parent to ik rep
        select_mode(scn.my_source_rig,'EDIT')
        for ebone_name in ik_ebone_help:
            create_edit_bone(ebone_name.replace('_ik_rep_help','')).parent = create_edit_bone(ebone_name.replace('_help',''))

        # clear all oregin bone's transforms
        select_mode(scn.my_source_rig,'POSE')
        fcs = source_rig.animation_data.action.fcurves
        fcs_remove = []
        fcs_done = fcs
        for ebone_name in ik_ebone_help:
            for fc in fcs_done:
                if fc.group.name == ebone_name.replace('_ik_rep_help',''):
                    fcs_remove.append(fc)
                    fcs_done = list(set(fcs_done)-set(fcs_remove))
            pb = source_rig.pose.bones[ebone_name.replace('_ik_rep_help','')]
            pb.location = Vector((0,0,0))
            pb.rotation_quaternion = Quaternion((1,0,0,0))
            pb.scale = Vector((1,1,1))
        for fc in fcs_remove:
            fcs.remove(fc)


        #     if type(bone['child_bone']) == str:
        #         link_bone_parent = copy_edit_bone(bone['name'],bone['name']+'_ik_rep')
        #         create_edit_bone(link_bone_parent.name,arm=scn.my_source_rig,coll_name='ik_rep',color='THEME01')
        #         link_bone_child = create_edit_bone(bone['child_bone'])
        #         link_bone_parent.tail = link_bone_child.head[:]
        #         link_bone_parent.parent = create_edit_bone(bone['name']).parent

        #         link_bone_help = copy_edit_bone(bone['name']+'_ik_rep',bone['name']+'_ik_rep_help')
        #         link_bone_help.parent = create_edit_bone(bone['name'])
        #         create_edit_bone(link_bone_help.name,arm=scn.my_source_rig,coll_name='ik_rep_help',color='THEME03')
        
        select_mode(scn.my_source_rig,'POSE')
        source_rig.data.collections['ik_rep_help'].is_visible = False

        return {'FINISHED'}

ik_button = [
    AN_OT_AddIKBone,
    AN_OT_AddTempIKBone,
    AN_OT_ToggleIK,
    AN_OT_LinkIKBones
]

classes = [
        # Armature Set
        AN_PT_PanelIK,
        AN_PT_PanelIK_Bone,
        AN_OT_AddIKBone,
        AN_OT_AddTempIKBone,
        AN_OT_ToggleIK,
        AN_OT_LinkIKBones,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)