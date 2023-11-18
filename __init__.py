# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import time
import random
from .ReampArmature import *
import math
from bpy_extras.io_utils import ExportHelper
from . import decoder
from . import encoder
from . import tz


bl_info = {
    "name" : "AniTool",
    "author" : "M",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


my_source_chains = []
my_target_chains = []
toggle_update = True
Toggle_IK_State = True
toggle_set_chain_map_name = True
save_new_bind_rule = False
save_new_ignore_name = False
boneIgnoreName = 'lowerarm_r_IK,calf_r_IK,lowerarm_l_IK,calf_l_IK,thigh_twist_01_l,calf_twist_01_r,calf_twist_01_l,thigh_twist_01_r,upperarm_twist_01_l,upperarm_twist_01_r,lowerarm_twist_01_l,lowerarm_twist_01_r,ik_hand_root,ik_hand_r,ik_foot_root,ik_foot_r,ik_foot_l'

ik_bones = [
    {'name':'lowerarm_r','type':'IK','left_right':'left','role':'','child_bone':'hand_r','pole_bone':'lowerarm_r','pole':180,'pole_loc':Vector((0,20,0)),'edit_offset':Vector((0,20,0)),'edit_bone_head':'tail','head_tail':1,'chain':2,'use_tail':True},
    {'name':'lowerarm_l','type':'IK','left_right':'left','role':'','child_bone':'hand_l','pole_bone':'lowerarm_l','pole':0,'pole_loc':Vector((0,20,0)),'edit_offset':Vector((0,20,0)),'edit_bone_head':'tail','head_tail':1,'chain':2,'use_tail':True},
    {'name':'calf_r','type':'IK','left_right':'right','role':'calf','child_bone':'foot_r','pole_bone':'calf_r','pole':0,'pole_loc':Vector((0,-20,0)),'edit_offset':Vector((0,20,0)),'edit_bone_head':'tail','head_tail':1,'chain':2,'use_tail':True},
    {'name':'calf_l','type':'IK','left_right':'left','role':'calf','child_bone':'foot_l','pole_bone':'calf_l','pole':180,'pole_loc':Vector((0,-20,0)),'edit_offset':Vector((0,20,0)),'edit_bone_head':'tail','head_tail':1,'chain':2,'use_tail':True},
    {'name':'foot_r','type':'IK','left_right':'right','role':'foot','child_bone':'ball_r','pole_bone':'','pole':180,'pole_loc':Vector((0,0,20)),'edit_offset':Vector((0,0,10)),'edit_bone_head':'tail','head_tail':1,'chain':1,'use_tail':True},
    {'name':'foot_l','type':'IK','left_right':'left','role':'foot','child_bone':'ball_l','pole_bone':'','pole':180,'pole_loc':Vector((0,0,20)),'edit_offset':Vector((0,0,10)),'edit_bone_head':'tail','head_tail':1,'chain':1,'use_tail':True},
    {'name':'ball_r','type':'IK','left_right':'right','role':'toe','child_bone':Vector((0,-20,0)),'pole_bone':'','pole':180,'pole_loc':Vector((0,0,20)),'edit_offset':Vector((0,0,10)),'edit_bone_head':'tail','head_tail':1,'chain':1,'use_tail':True},
    {'name':'ball_l','type':'IK','left_right':'left','role':'toe','child_bone':Vector((0,-20,0)),'pole_bone':'','pole':180,'pole_loc':Vector((0,0,20)),'edit_offset':Vector((0,0,10)),'edit_bone_head':'tail','head_tail':1,'chain':1,'use_tail':True},
    {'name':'pelvis','type':'Transform','left_right':'left','role':'','child_bone':'spine_01','pole_bone':'','pole':180,'pole_loc':Vector((0,-20,0)),'edit_offset':Vector((0,20,0)),'edit_bone_head':'head','head_tail':0,'chain':2,'use_tail':True}
]

default_rule_source_name_LR = ['_l','_r']
default_rule_target_name_LR = ['Left','Right']
default_rule_source_name_body = ['index','middle','pinky','ring','thumb','thigh','clavicle','neck']
default_rule_target_name_body = ['Index','Middle','Pinky','Ring','Thumb','UpLeg','Shoulder','Neck']

# reg_button = [
#     "an.automap_bone_chains",
#     "an.alight_rest_bone",
#     "auto_set_chain.go",
#     "an.build_list",
#     "copy_rotation.go",
#     "an.clear_constraints",
#     "an.copy_rest_pose",
#     "an.apply_rest_pose",
#     "an.set_action_range",
# ]


# ik_button = [
#     "an.add_ikbone",
#     "an.add_temp_ikbone",
#     "an.toggle_ik",
#     "an.link_ik_bone"
# ]

def set_bone_chain(self,context,BoneChains,scnBoneChains):
        scnBoneChains.clear()
        scn = bpy.context.scene
        for bone_chain in BoneChains:
            # print(bone_chain)
            item = scnBoneChains.add()
            boneNames = ''
            for bone in bone_chain:
                item_bone_chain = item.bone_chain.add()
                item_bone_chain.name = bone.name
                boneNames += item_bone_chain.name
            item.name = boneNames

def drawBoneChains(self,context,BoneChains):
        # scn = bpy.context.scene
        layout = self.layout
        for idx,item in enumerate(BoneChains):
            row = layout.row(align=False)
            row.alignment = 'LEFT'
            row.prop(item,'isExtraBone')
            row.label(text=item.name)
            row.split(align=True,factor=0.3)


def sortBoneChains(self,context,scnList):
    newSortList = []
    for bone_chain in scnList.values():
        boneList = []
        for bone in bone_chain.bone_chain.values():

            boneList.append(bone.name)
        newSortList.append(boneList)
    newSortList.sort()

    scnList.clear()

    for bone_chain in newSortList:
        item = scnList.add()
        chainName = ''
        for bone in bone_chain:
            item2 = item.bone_chain.add()
            item2.name = bone
            chainName += bone
        item.name = chainName



def getItem(self,context):
    items = []
    for item in bpy.context.scene.my_target_chains.values():
        Bones = ''
        Bones += item.IsSelected
        for bone in item.bone_chain.values():
            Bones += bone.name
        items.append((Bones,Bones,''))

    return items

def get_enum(self):
    import random
    # return value
    # print(self['testprop'])
    return random.randint(1, 1)


def set_enum(self, value):
    print (dir(self))
    print(self.BoneChain)
    print(self.name)
    # print(self.value)
    # print(self.BoneChain.values()[0])
    self.value = value
    # self.BoneChain = bpy.context.scene.my_enum_bone_chain.values()[value]
    # self.BoneChain = 'mixamorig:RightUpLegmixamorig:RightLegmixamorig:RightFootmixamorig:RightToeBasemixamorig:RightToe_End'
    # self['testprop'] = value
    print("setting value", value)

def vec_roll_to_mat3(vec, roll):
    epsi = 1e-10
    target = Vector((0, 0.1, 0))
    nor = vec.normalized()
    axis = target.cross(nor)
    if axis.dot(axis) > epsi:
        axis.normalize()
        theta = target.angle(nor)
        bMatrix = Matrix.Rotation(theta, 3, axis)
    else:
        updown = 1 if target.dot(nor) > 0 else -1
        bMatrix = Matrix.Scale(updown, 3)
        bMatrix[2][2] = 1.0

    rMatrix = Matrix.Rotation(roll, 3, nor)
    mat = rMatrix @ bMatrix
    return mat
   
def mat3_to_vec_roll(mat, ret_vec=False):
    vec = mat.col[1]
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv @ mat
    roll = math.atan2(rollmat[0][2], rollmat[2][2])
    if ret_vec:
        return vec, roll
    else:
        return roll

def create_edit_bone(bone_name,layer = None):
    b = bpy.context.active_object.data.edit_bones.get(bone_name)
    if not b:
        b = bpy.context.active_object.data.edit_bones.new(bone_name)
    if layer:
        set_bone_layer(b,layer)
    return b

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
    
def create_constraint(rig,bone_name,cst_name,type):
    for cnsts in rig.pose.bones[bone_name].constraints:
        if cnsts.name == cst_name:
            return cnsts
    cst = rig.pose.bones[bone_name].constraints.new(type)
    cst.name = cst_name
    return cst

def copy_bone_transforms(bone1, bone2):
    bone2.head = bone1.head.copy()
    bone2.tail = bone1.tail.copy()
    bone2.roll = bone1.roll

def set_active_object(object_name):
     bpy.context.view_layer.objects.active = object_name
     object_name.hide_set(False)
     object_name.select_set(state=True)

def set_bone_layer(editbone, layer_idx, multi=False):
    editbone.layers[layer_idx] = True
    if multi:
        return
    for i, lay in enumerate(editbone.layers):
        if i != layer_idx:
            editbone.layers[i] = False

def set_armature_layer(layer=None,Viewtype=None):
    i = 0 
    if type(Viewtype) == bool:
        while i <= 31:
            bpy.context.object.data.layers[i] = Viewtype
            i+= 1
    if layer :
        while i <= 31:
            if i == layer:
                bpy.context.object.data.layers[i] = True
            else:
                bpy.context.object.data.layers[i] = False
            i+= 1

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

def build_bone_tweak(self,context,scn_source_chains,scn_source_rig):
    scn = bpy.context.scene

    scn_target_rig = scn.my_target_rig
    set_active_object(scn_target_rig)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    scn_source_rig.select_set(state=True)
    # set_active_object(scn.my_source_rig)
    scn_target_rig.select_set(state=True)
    bpy.ops.object.mode_set(mode='EDIT')

    # create a transform dict of target bones
    obj_mat = scn_target_rig.matrix_world
    tar_bones_dict = {}        
    
    for edit_bone in scn_target_rig.data.edit_bones:
        tar_bones_dict[edit_bone.name] = {
            'matrix': obj_mat @ edit_bone.matrix,
            'head': obj_mat @ edit_bone.head, 
            'tail': obj_mat @ edit_bone.tail, 
            'roll': mat3_to_vec_roll(obj_mat.to_3x3() @ edit_bone.matrix.to_3x3()),
            'x_axis': (obj_mat @ edit_bone.x_axis.normalized()).normalized()
            }
            
    print("  Creating Bones...")
    bone_names = []
    for chains in scn_source_chains:
        for bone in chains.bone_chain:
            bone_names.append(bone.name)
            # print(bone.name)
    
    #autorot_constraints = True
    ik_chains = {}
    loc_helper_bones = []
    
    
    # create the _tweak skeleton for Interactive Tweaks (Bind)
    tweak_suffix = '_REMAPTWEAK'
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    set_active_object(scn_source_rig)
    bpy.context.view_layer.objects.active = scn_source_rig
    scn_source_rig.select_set(state=True)
    bpy.ops.object.mode_set(mode='EDIT')
    # bpy.ops.object.select_all(action='DESELECT')


    # scn_source_rig.select_set(state=True)

    # return

    bone_names = [b.name for b in scn_source_rig.data.edit_bones]
    temp_bone_names = bone_names[:]
    for bone in temp_bone_names:
        if ArmatureBoneInfo.check_helper_bones(bone=bone):
            bone_names.remove(bone)
    for bname in bone_names:
        if not bname.endswith(tweak_suffix):
            eb = bpy.context.object.data.edit_bones.get(bname)  
            if not bpy.context.object.data.edit_bones.get(eb.name+tweak_suffix):
                tweak_b = bpy.context.active_object.data.edit_bones.new(eb.name+tweak_suffix)
                tweak_b.use_deform = False
            # tweak_b['arp_remap_temp_bone'] = 1# tag it for deletion
                tweak_b.head = eb.head.copy()
                tweak_b.tail = eb.tail.copy()
                tweak_b.roll = eb.roll
                set_bone_layer(tweak_b, 25)
                                # set as root

        # copy_bone_transforms(eb, tweak_b)            
        # set_bone_layer(tweak_b, 25)
        
    #   parent
    for eb in scn_source_rig.data.edit_bones:
        # if eb.layers[25]:
        if eb.name.endswith(tweak_suffix):
            source_par = bpy.context.object.data.edit_bones.get(eb.name[:-len(tweak_suffix)])
            par = source_par.parent
            if par:                        
                eb.parent = bpy.context.object.data.edit_bones.get(par.name+tweak_suffix)
    
    #   constrain
    bpy.ops.object.mode_set(mode='POSE')
    
    for pb in scn_source_rig.pose.bones:
        # if pb.bone.layers[25]:
        if pb.name.endswith(tweak_suffix):
            if not len(pb.constraints):
                cns = pb.constraints.new('COPY_TRANSFORMS')
                cns.target = scn_source_rig
                cns.subtarget = pb.name[:-len(tweak_suffix)]
                cns.owner_space = cns.target_space = 'LOCAL'
                cns.mix_mode = 'BEFORE'
                
    bpy.ops.object.mode_set(mode='EDIT')
        
    idxi = 0
    
    obj_mat = scn_source_rig.matrix_world.inverted()



    for bone_item in scn.my_bones_map:

        idxi += 1 
        source_bone_name = bone_item.source_bone
        eb_source_bone = bpy.context.object.data.edit_bones.get(source_bone_name)          
    
        if bone_item.name != "" and bone_item.name != "None" and eb_source_bone and bone_item.name in tar_bones_dict:            
        # if bone_item.name != "" and bone_item.name != "None" and eb_source_bone and bone_item.name in tar_bones_dict:            
            # main
            if bpy.context.active_object.data.edit_bones.get(bone_item.name+"_REMAP"):
                bone_remap = bpy.context.active_object.data.edit_bones.get(bone_item.name+"_REMAP")                
            else:
                bone_remap = bpy.context.active_object.data.edit_bones.new(bone_item.name+"_REMAP")       
            # bone_remap['arp_remap_temp_bone'] = 1# tag it for deletion
            
            # copy target bones transforms
            bone_remap.matrix = obj_mat @ tar_bones_dict[bone_item.name]['matrix']
            bone_remap.head, bone_remap.tail = obj_mat @ tar_bones_dict[bone_item.name]['head'], obj_mat @ tar_bones_dict[bone_item.name]['tail']
            # align_bone_x_axis(bone_remap, obj_mat @ tar_bones_dict[bone_item.name]['x_axis'])                
        
            bone_remap.parent = bpy.context.object.data.edit_bones.get(eb_source_bone.name+tweak_suffix)
            set_bone_layer(bone_remap, 24) 

            if bone_item.is_root:
                # root offset
                root_offset_name = bone_item.name+"_ROOT_OFFSET"
                root_offset = create_edit_bone(root_offset_name) 
                # root_offset =  bpy.context.active_object.data.edit_bones.new(root_offset_name) 
                # root_offset['arp_remap_temp_bone'] = 1# tag it for deletion
                copy_bone_transforms(eb_source_bone, root_offset)
                set_bone_layer(root_offset, 24)
                
                # root pos
                root_pos_name = bone_item.name+"_ROOT"
                root_pos = create_edit_bone(root_pos_name)    
                # root_pos['arp_remap_temp_bone'] = 1# tag it for deletion
                root_pos.matrix = obj_mat @ tar_bones_dict[bone_item.name]['matrix']
                root_pos.head, root_pos.tail = obj_mat @ tar_bones_dict[bone_item.name]['head'], obj_mat@ tar_bones_dict[bone_item.name]['tail']
                root_pos.length = eb_source_bone.length                    
            
                
                #align_bone_x_axis(root_pos, tar_bones_dict[bone_item.name]['x_axis'])  
                root_pos.parent = root_offset
                set_bone_layer(root_pos, 24)
                
                bpy.ops.object.mode_set(mode='POSE')

                # add location constraint
                bone_root_offset_pb = scn_source_rig.pose.bones.get(root_offset_name)
                cns = bone_root_offset_pb.constraints.new('COPY_LOCATION')
                cns.target = scn_source_rig
                cns.subtarget = source_bone_name
                cns.name += '_REMAP'
                
                bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = scn_target_rig
    scn_target_rig.select_set(state=True)
    # bpy.data.objects['Armature'].select_set(state=True)
    bpy.ops.object.mode_set(mode='POSE')

    if scn_target_rig.animation_data:
        scn_target_rig.animation_data.action = None

    for bone_item in scn.my_bones_map:
        if bone_item.name != "" and bone_item.name != "None" and context.active_object.pose.bones.get(bone_item.name):
            
            pose_bone = context.active_object.pose.bones[bone_item.name]              
            context.active_object.data.bones.active = pose_bone.bone
            
            # Add constraints
            # main rotation
            if 'Copy Rotation_REMAP' in pose_bone.constraints:
                cns = pose_bone.constraints['Copy Rotation_REMAP']
            else:
                cns = pose_bone.constraints.new('COPY_ROTATION')
                cns.name += '_REMAP'
            cns.target = scn_source_rig
            cns.subtarget = bone_item.name + "_REMAP"

            if bone_item.is_root:
                if 'Copy Location_loc_REMAP' in pose_bone.constraints:
                    cns_root = pose_bone.constraints['Copy Location_loc_REMAP']
                else:
                    cns_root = pose_bone.constraints.new('COPY_LOCATION')
                    cns_root.name += '_loc_REMAP'                   
                cns_root.target = scn_source_rig
                cns_root.subtarget = bone_item.name + "_ROOT"
                cns_root.owner_space = cns_root.target_space = 'WORLD'

def set_string(self,value):
    # print(value)
    # print(dir(self))
    self.my_test_string = value
    print(self.my_test_string)
    self['abc'] = value
    pass

def get_string(self):
    # print(value)
    # print(dir(self))
    # print(self.my_test_string)
    return self['abc']
    return self.my_test_string

def update_string(self,context):
    if toggle_update:
    # bpy.ops.an.build_chains()
        filter_name()

def set_ignore_source(self,value):
    global boneIgnoreName
    self.enteranl_add_to_ignore_source = value
    if value:
        ignore_name = self.source_chain.split(',')[0]
        boneIgnoreName += ignore_name
        boneIgnoreName += ','
        bpy.ops.an.build_list()

def get_ignore_source(self):
    return self.enteranl_add_to_ignore_source

def set_ignore_target(self,value):
    global boneIgnoreName
    self.enteranl_add_to_ignore_target = value
    if value:
        ignore_name = self.name.split(',')[0]
        boneIgnoreName += ignore_name
        boneIgnoreName += ','
        bpy.ops.an.build_list()

def get_ignore_target(self):
    return self.enteranl_add_to_ignore_target

def set_ignore_bool(self,value):
    scn = bpy.context.scene
    self.in_is_ignore = value
    list = scn.my_ignore_bone_name.split(',')
    if value:
        if self.name not in list:
            list.append(self.name)
    else:
        if self.name in list:
            list.remove(self.name)
    scn.my_ignore_bone_name = ','.join([a for a in list if a != '']) 



def get_ignore_bool(self):
    return self.in_is_ignore

def recoerd_old_value():
    scn = bpy.context.scene
    for item in scn.my_chain_map:
        item.old_name = item.name

def get_chain_map_name(self):
    return self.in_name

def set_chain_map_name(self,value):
    scn = bpy.context.scene
    global toggle_set_chain_map_name
    if toggle_set_chain_map_name == True:
        toggle_set_chain_map_name = False
        for item in scn.my_chain_map:
            if item.name == value:
                item.name = self.name
        toggle_set_chain_map_name = True    
    self.in_name = value
    self.target_bones.clear()
    for bone in value.split(','):
        item = self.target_bones.add()
        item.name = bone


def set_source_chain(self,value):
    self.in_source_chain = value
    self.source_bones.clear()
    for bone in value.split(','):
        item = self.source_bones.add()
        item.name = bone


def get_source_chain(self):
    return self.in_source_chain


def filter_name():
    scn = bpy.context.scene
    chain_map = scn.my_chain_map
    name_need_change = []
    name_all = []
    global my_target_chains

    for item in my_target_chains:
        name_all.append(','.join(a.name for a in item['chain']))

    for item in chain_map:
        if item.old_name != item.name:
            name_need_change.append(item.name)

    name_all = list(set(name_all)-set(name_need_change))

    idx_need_change = []
    for idx,item in enumerate(chain_map):
        if item.name in name_need_change and item.name == item.old_name:
            idx_need_change.append(idx)
        elif item.name in name_all :
            name_all.remove(item.name)

    for idx in idx_need_change:
        chain_map[idx].name = name_all[0]
        name_all.pop(0)
    recoerd_old_value()



def build_default_bind_rule():

    scn = bpy.context.scene
    scn.my_chain_bind_rule_LR.clear()
    scn.my_chain_bind_rule_body.clear()

    global default_rule_source_name_LR 
    global default_rule_target_name_LR 
    global default_rule_source_name_body 
    global default_rule_target_name_body 

    for source_name , name in zip(default_rule_source_name_LR,default_rule_target_name_LR):
        item = scn.my_chain_bind_rule_LR.add()
        item.source_name = source_name
        item.name = name

    for source_name , name in zip(default_rule_source_name_body,default_rule_target_name_body):
        item = scn.my_chain_bind_rule_body.add()
        item.source_name = source_name
        item.name = name

def selects_mode(objs,mode):
    scn = bpy.context.scene
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    for obj in objs:
        obj.hide_set(False)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(state=True)
    bpy.ops.object.mode_set(mode=mode)

def select_mode(obj,mode):
    scn = bpy.context.scene
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    obj.hide_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(state=True)
    bpy.ops.object.mode_set(mode=mode)

def copy_transforms(bone_map):
    scn = bpy.context.scene
    select_mode(scn.my_source_rig,"POSE")
    for item in bone_map:
        pb1 = scn.my_source_rig.pose.bones[item.source_bone]
        pb2 = scn.my_target_rig.pose.bones[item.name]
        cnst = pb2.constraints.new('COPY_TRANSFORMS')
        cnst.target = scn.my_source_rig
        cnst.subtarget = pb1.name

def copy_transforms_all(source,target):
    select_mode(target,"POSE")
    for pb1 in source.pose.bones:
        pb2 = target.pose.bones[pb1.name]
        cnst = pb2.constraints.new('COPY_TRANSFORMS')
        cnst.target = source
        cnst.subtarget = pb1.name

def connect_bones():
    scn = bpy.context.scene
    select_mode(scn.my_source_rig,'EDIT')
    for chain in my_source_chains:
        bpy.context.view_layer.update()
        bone_list = chain['chain']
        for idx,bone in enumerate(bone_list):
            eb = create_edit_bone(bone.name)
            if idx < len(bone_list) - 1:
                eb2 = create_edit_bone(bone_list[idx+1].name)
                offset = eb2.head.copy()
                eb.tail = offset

def rotate_edit_bones():
    scn = bpy.context.scene
    _spine = ['pelvis', 'spine', 'neck', 'head']
    _arms = ['clavicle', 'upperarm', 'lowerarm']
    _hand = ['hand']
    _fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']
    _legs = ['thigh', 'calf']
    _foot = ['foot']
    _toes = ['ball']

    # _spine = ['pelvis']
    # _arms = []
    # _hand = []
    # _fingers = []
    # _legs = []
    # _foot = []
    # _toes = []


    bones_transforms_dict = {}

    print("\nSet Mannequin Axes bones...")

    #display layers


    print("  Build transform dict...")

    #build a dict of bones transforms, excluding custom bones, bend bones, helper bones


    rotate_value = 0.0
    rotate_axis = 'X'
    roll_value = 0.0


    created_bones_dict = {}

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    scn.my_source_rig.select_set(state=True)
    bpy.ops.object.mode_set(mode='EDIT')
    for chain in my_source_chains:
        for pb in chain['chain']:
            bone_name = pb.name
            bone_to_create_name = ""
            rotate_value = 0.0
            roll_value = 0.0
            rotate_axis = Vector((1,0,0))

            if pb.name == 'thigh_twist_01_l':
                a = 1
                pass

            #spine
            for b in _spine:
                if b in bone_name:
                    rotate_value = -math.pi/2
                    roll_value = math.radians(-90)
                    bone_to_create_name = bone_name
                    rotate_axis = 'Z'
                    break

            #arms
            if bone_to_create_name == "":
                for b in _arms:
                    if b in bone_name:
                        if bone_name.endswith(".l") or bone_name.endswith("_l"):

                            rotate_value = -math.pi/2
                            roll_value = 0.0
                            if scn.arp_retro_axes:
                                rotate_value = -math.pi/2
                                roll_value = math.radians(180)

                        if bone_name.endswith(".r") or bone_name.endswith("_r"):

                            rotate_value = math.pi/2
                            roll_value = math.radians(180)
                            if scn.arp_retro_axes:
                                rotate_value = -math.pi/2
                                roll_value = math.radians(0)

                        bone_to_create_name = bone_name
                        rotate_axis = 'Z'
                        break

            #hand
            if bone_to_create_name == "":
                for b in _hand:
                    if b in bone_name:
                        if bone_name.endswith(".l") or bone_name.endswith("_l"):
                            rotate_value = -math.pi/2
                            roll_value = math.radians(-90)

                        if bone_name.endswith(".r") or bone_name.endswith("_r"):
                            rotate_value = math.pi/2
                            roll_value = math.radians(-90)

                        bone_to_create_name = bone_name
                        rotate_axis = 'Z'
                        break

            #fingers
            if bone_to_create_name == "":
                for b in _fingers:
                    if b in bone_name:
                        if bone_name.endswith(".l") or bone_name.endswith("_l"):
                            rotate_value = -math.pi/2
                            roll_value = math.radians(-90)

                        if bone_name.endswith(".r") or bone_name.endswith("_r"):
                            rotate_value = math.pi/2
                            roll_value = math.radians(-90)

                        bone_to_create_name = bone_name
                        rotate_axis = 'Z'
                        break

            #legs
            if bone_to_create_name == "":
                for b in _legs:
                    if b in bone_name:
                        if bone_name.endswith(".l") or bone_name.endswith("_l"):
                            rotate_value = math.pi/2
                            roll_value = math.radians(180)

                        if bone_name.endswith(".r") or bone_name.endswith("_r"):
                            rotate_value = -math.pi/2
                            roll_value = math.radians(0)

                        bone_to_create_name = bone_name
                        rotate_axis = 'Z'
                        break

            #foot
            if bone_to_create_name == "":
                for b in _foot:
                    if b in bone_name:
                        if bone_name.endswith(".l") or bone_name.endswith("_l"):
                            rotate_value = math.pi
                            roll_value = math.radians(90)

                        if bone_name.endswith(".r") or bone_name.endswith("_r"):
                            rotate_value = 0.0
                            roll_value = math.radians(-90)

                        bone_to_create_name = bone_name
                        rotate_axis = 'Z'
                        break

            #toes
            if bone_to_create_name == "":
                for b in _toes:
                    if b in bone_name:
                        if bone_name.endswith(".l") or bone_name.endswith("_l"):
                            rotate_value = -math.pi/2
                            roll_value = math.radians(-90)

                        if bone_name.endswith(".r") or bone_name.endswith("_r"):
                            rotate_value = math.pi/2
                            roll_value = math.radians(-90)

                        bone_to_create_name = bone_name
                        rotate_axis = 'Z'
                        break


            if bone_to_create_name != "" :
                #create _childof bones
                # new_bone = create_edit_bone(bone_to_create_name + "_childof", deform=False)
                # new_bone.head = bones_transforms_dict[bone_to_create_name][0]
                # new_bone.tail = bones_transforms_dict[bone_to_create_name][1]
                # new_bone.roll = bones_transforms_dict[bone_to_create_name][2]

                # R = Matrix.Rotation(math.radians(-90.0),4,eb.z_axis.normalized())
                eb = bpy.context.object.data.edit_bones.get(bone_name)
                R = Matrix.Rotation(rotate_value,4,eb.z_axis.normalized() if rotate_axis == 'Z' else eb.x_axis.normalized())
                # print(R)
                old_head = eb.head.copy()
                eb.transform(R,roll=True)
                # eb.tail.rotate(R)
                offset = -(eb.head - old_head)
                eb.head += offset
                eb.tail += offset
                set_bone_layer(eb, 16)
                # get_edit_bone(bone_to_create_name).use_deform = False
                # store the new bones in a dict
                # created_bones_dict[bone_to_create_name] = rotate_value, roll_value, rotate_axis

                # print(math.pi)
                # print(math.radians(90))
def duplicate(obj, data=True, actions=True, collection=None):
    obj_copy = obj.copy()
    if data:
        obj_copy.data = obj_copy.data.copy()
    if actions and obj_copy.animation_data:
        obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
    bpy.context.collection.objects.link(obj_copy)
    return obj_copy

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

def export_map(file_path):
    scn = bpy.context.scene

    # add extension
    if not file_path.endswith(".toml"):
        file_path += ".toml"
    
    file = open(file_path, 'w', encoding='utf8', newline='\n')

    file.write('')

    config = {}
    common = {}
    chains = {}
    config = {'common':common,'chains':chains}
    common['ignore_name'] = scn.my_ignore_bone_name

    name = locals()
    for idx,chain in enumerate(scn.my_chain_map):
        idx = str(idx)
        name[str(chain.source_chain)] = {}
        # name[str(chain.source_chain)]['source_chain'] = chain.source_chain
        name[str(chain.source_chain)]['target_chain'] = chain.name
        name[str(chain.source_chain)]['is_root'] = chain.is_root
        chains[str(chain.source_chain)] = name[str(chain.source_chain)]
    r = encoder.dump(config, file)
    file.close()
    return

def import_map(file_path):
    scn = bpy.context.scene
    file = open(file_path, 'r', encoding='utf8', newline='\n')

    config = decoder.load(file)
    scn.my_ignore_bone_name = config['common']['ignore_name']
    global save_new_ignore_name 
    save_new_ignore_name = True
    bpy.ops.an.build_list()

    for chain in scn.my_chain_map:
        for source_chain in config['chains']:
            if source_chain == chain.source_chain:
                chain.name = config['chains'][source_chain]['target_chain']
                chain.is_root = config['chains'][source_chain]['is_root']
                del config['chains'][source_chain]
                break
    file.close()
    return

def root_motion():
    scn = bpy.context.scene
    source_action = scn.my_source_rig.animation_data.action
    location_index = 0
    for fc in source_action.fcurves:
        if fc.data_path == 'location':
            scn.my_target_rig.keyframe_insert(data_path=fc.data_path, index=fc.array_index, group=scn.my_target_rig.data.name,frame=0)
            target_fc = scn.my_target_rig.animation_data.action.fcurves.find(fc.data_path,index=fc.array_index)
            for kp in fc.keyframe_points:
                scn.my_target_rig.keyframe_insert(data_path=fc.data_path, index=fc.array_index, group=scn.my_target_rig.data.name,frame=kp.co[0])
                target_kp = target_fc.keyframe_points[-1]
                target_kp.co = kp.co

        if location_index >= 2:
            break

def auto_add_ignore(source,target):
    ignore = []
    source_pb_list = [pb.name for pb in source.pose.bones]
    for target_pb in target.pose.bones:
        if target_pb.name not in source_pb_list:
            ignore.append(target_pb.name)
    return ignore

def copy_rest_pose(bone_map):
    scn = bpy.context.scene
    selects_mode([scn.my_source_rig,scn.my_target_rig],"POSE")
    for pb in scn.my_source_rig.pose.bones:
        pb.matrix_basis = Matrix() 

    if scn.my_copy_rest_pose_rule == 'U2U':
        for item in bone_map:
            pb1 = scn.my_source_rig.pose.bones[item.source_bone]
            pb2 = scn.my_target_rig.pose.bones[item.name]  
            mat_loc = Matrix.Translation(pb.head)
            pb1.matrix = pb2.matrix
            bpy.context.view_layer.update()
            # pb1.matrix = mat_loc @ pb1.matrix

    elif scn.my_copy_rest_pose_rule == 'U2M':
        for item in bone_map:
            bpy.context.view_layer.update()
            pb1 = scn.my_source_rig.pose.bones[item.source_bone]
            pb2 = scn.my_target_rig.pose.bones[item.name]
            v1 = pb1.tail - pb1.head
            v1.normalize()
            v2 = pb2.tail - pb2.head
            temp = v2[1]
            v2[1] = -v2[2]
            v2[2] = temp
            v2.normalize()
            rot = v1.rotation_difference(v2)
            m = (
            Matrix.Translation(pb1.head) @
            rot.to_matrix().to_4x4() @
            Matrix.Translation(-pb1.head)
            )
            pb1.matrix = m @ pb1.matrix

def get_source_rig(self):
    scn = bpy.context.scene
    if self.get('in__source_rig','') != '':
        return self.get('in__source_rig','')
    else:
        if bpy.context.selected_objects :
            scn.source_rig = bpy.context.selected_objects[0].name
            return bpy.context.selected_objects[0].name
        else:
            return ''

def set_source_rig(self,value):
    scn = bpy.context.scene
    self['in__source_rig'] = value
    if value != '':
        scn.my_source_rig = bpy.data.objects[value]
    
def _pick_object(action):
    obj = bpy.context.object
    scene = bpy.context.scene

    if action == "pick_source":
        scene.source_rig = obj.name
    elif action == "pick_target":
        scene.target_rig = obj.name
    elif action == 'pick_bone' or action == 'pick_pole':
        bname = ''
        try:            
            if bpy.context.mode == 'POSE':
                bname = bpy.context.selected_pose_bones[0].name
            elif bpy.context.mode == 'EDIT_ARMATURE':
                bname = bpy.context.selected_editable_bones[0].name            
        except:
            print("can't pick bone")

        if action == 'pick_pole':        
            scene.bones_map[scene.bones_map_index].ik_pole = bname
        elif action == 'pick_bone':
            scene.bones_map[scene.bones_map_index].name = bname      

# class Prpp_Armature(bpy.types.PropertyGroup):
#     def set_selected(self):
#         scn = bpy.context.scene
#         if not scn.my_source_rig :
#             pass
#         else:
#             return scn.my_source_rig

#     name:bpy.props.StringProperty(get=set_selected)
#     in__name:bpy.props.StringProperty()


class EnumBoneCHain(bpy.types.PropertyGroup):
    BoneChain:bpy.props.EnumProperty(items=getItem)
    IsSelected:bpy.props.BoolProperty()
    # BoneChain:bpy.props.EnumProperty(items=getItem,get=get_enum, set=set_enum)

class boneList(bpy.types.PropertyGroup):
    # bone:bpy.props.CollectionProperty(type=bpy.types.PoseBone)
    index:bpy.props.IntProperty()
    name:bpy.props.StringProperty()

class AN_PROP_BoneIgnore(bpy.types.PropertyGroup):
    is_ignore:bpy.props.BoolProperty(get=get_ignore_bool,set=set_ignore_bool)
    in_is_ignore:bpy.props.BoolProperty()

class BoneChains(bpy.types.PropertyGroup):
    # isExtraBone:bpy.props.BoolProperty()
    # IsSelected:bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    # bone_chain:bpy.props.CollectionProperty(type=boneList)
    index:bpy.props.IntProperty()
    is_root:bpy.props.BoolProperty()

class BoneChainsList(bpy.types.PropertyGroup):
    bone_chains: bpy.props.CollectionProperty(type=BoneChains)

class AN_PROP_ChainMap(bpy.types.PropertyGroup):
    is_root:bpy.props.BoolProperty()
    add_to_ignore_source:bpy.props.BoolProperty(set=set_ignore_source,get=get_ignore_source)
    enteranl_add_to_ignore_source:bpy.props.BoolProperty()
    add_to_ignore_target:bpy.props.BoolProperty(set=set_ignore_target,get=get_ignore_target)
    enteranl_add_to_ignore_target:bpy.props.BoolProperty()
    index:bpy.props.IntProperty()
    source_chain: bpy.props.StringProperty(set=set_source_chain,get=get_source_chain)
    in_source_chain: bpy.props.StringProperty()
    source_bones: bpy.props.CollectionProperty(type=AN_PROP_BoneIgnore)
    target_bones: bpy.props.CollectionProperty(type=AN_PROP_BoneIgnore)
    name:bpy.props.StringProperty(set=set_chain_map_name,get=get_chain_map_name)
    in_name:bpy.props.StringProperty()
    old_name:bpy.props.StringProperty()
    # test:bpy.props.IntProperty()

class BonesMap(bpy.types.PropertyGroup):
    source_bone: bpy.props.StringProperty()
    is_root:bpy.props.BoolProperty()

class AN_PGT_ChainBindRule(bpy.types.PropertyGroup):
    source_name: bpy.props.StringProperty()

#operator, connected the button that adds the params
class AN_OT_BuildChains(bpy.types.Operator):
    bl_idname = 'an.build_chains'
    bl_label = 'BuildChains'
    slot: bpy.props.IntProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        scn.my_source_chains.clear()

        self.sourceArmature = ArmatureBoneInfo(scn.my_source_rig)
        self.targetArmature = ArmatureBoneInfo(scn.my_target_rig)

        boneIgnoreName_list = scn.my_ignore_bone_name.split(',')

        self.sourceArmature.boneIgnoreName += boneIgnoreName_list
        self.targetArmature.boneIgnoreName += boneIgnoreName_list

        global my_source_chains
        my_source_chains = self.sourceArmature.bone_chains

        global my_target_chains
        my_target_chains = self.targetArmature.bone_chains

        # scn.my_enum_bone_chain.clear()
        # for item in scn.my_source_chains.values():
        #     scn.my_enum_bone_chain.add()
        
        return {'FINISHED'}
 
    
class AN_OT_ClearIgnoreBone(bpy.types.Operator):
    bl_idname = 'an.clear_ignore_bone'
    bl_label = 'ClearIgnoreBone'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        scn.my_ignore_bone_name = ''
        return {'FINISHED'}

class AN_OT_CopyRestPose(bpy.types.Operator):
    bl_idname = 'an.copy_rest_pose'
    bl_label = 'Copy Rest Pose'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        build_bones_map()
        copy_rest_pose(scn.my_bones_map)

        return {'FINISHED'}

class AN_OT_ApplyRestPose(bpy.types.Operator):
    bl_idname = 'an.apply_rest_pose'
    bl_label = 'Apply Rest Pose'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        temp_source_rig = duplicate(scn.my_source_rig)
        select_mode(scn.my_source_rig,'OBJECT')
        bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')
        mesh = bpy.context.selected_objects[0]
        select_mode(mesh,'OBJECT')

        mod = mesh.modifiers.new(name=mesh.modifiers[0].name+'_rest', type=mesh.modifiers[0].type)
        mod.object = scn.my_source_rig
        bpy.ops.object.modifier_apply(modifier=mod.name)

        select_mode(scn.my_source_rig,'POSE')
        bpy.ops.pose.armature_apply(selected=False)
        # return {'FINISHED'}
        bpy.context.view_layer.update()

        if scn.my_source_rig.animation_data:
            i = 0
            while i < 2:
                copy_transforms_all(temp_source_rig,scn.my_source_rig)
                bpy.context.view_layer.update()

                select_mode(scn.my_source_rig,'POSE')
                bpy.ops.pose.select_all(action='SELECT')

                bpy.context.view_layer.update()

                bpy.ops.nla.bake(
                frame_start=int(scn.my_source_rig.animation_data.action.frame_range[0]),
                frame_end=int(scn.my_source_rig.animation_data.action.frame_range[1]),
                step=1,
                only_selected=True,
                visual_keying=True,
                clear_constraints = True,
                bake_types={'POSE'}
                )
                bpy.context.view_layer.update()
                i += 1

            select_mode(temp_source_rig,'OBJECT')
            bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
            bpy.ops.object.delete()

        return {'FINISHED'}
    
class AN_OT_ImportMap(bpy.types.Operator):
    bl_idname = 'an.import_map'
    bl_label = 'Import Map'
    bl_options = {'UNDO'}

    filter_glob: bpy.props.StringProperty(default="*.toml", options={'HIDDEN'})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", default='toml')

    def execute(self, context):
        scn = bpy.context.scene
        filename_ext = ".toml"
        filter_glob: bpy.props.StringProperty(default="*.toml", options={'HIDDEN'}, maxlen=255)
        import_map(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.filepath = 'remap_preset.toml'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class AN_OT_SetActionRange(bpy.types.Operator):
    bl_idname = 'an.set_action_range'
    bl_label = 'Set Action Range'
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.context.scene.frame_end = int(bpy.context.selected_objects[0].animation_data.action.frame_range[1])
        return {'FINISHED'}

class AN_OT_ExportMap(bpy.types.Operator):
    bl_idname = 'an.export_map'
    bl_label = 'Export Map'
    bl_options = {'UNDO'}

    filter_glob: bpy.props.StringProperty(default="*.toml", options={'HIDDEN'})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", default='toml')

    def execute(self, context):
        scn = bpy.context.scene
        filename_ext = ".toml"
        filter_glob: bpy.props.StringProperty(default="*.toml", options={'HIDDEN'}, maxlen=255)
        export_map(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = 'remap_preset.toml'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        


    
class AN_OT_AutomapBoneChains(bpy.types.Operator):
    bl_idname = 'an.automap_bone_chains'
    bl_label = 'AutomapBoneChains'

    def execute(self, context):
        scn = bpy.context.scene
        global toggle_update
        toggle_update = False
        rule_source_name_LR = [(a.source_name.lower(),a.name.lower()) for a in scn.my_chain_bind_rule_LR]
        rule_source_name_body = [(a.source_name.lower(),a.name.lower()) for a in scn.my_chain_bind_rule_body]

        global toggle_set_chain_map_name
        toggle_set_chain_map_name = False
        # temp_my_chain_map = [a.name for a in my_target_chains]
        for idx,item in enumerate(scn.my_chain_map):
            get_same = False
            for item_target in scn.my_target_bone_chains_list[idx].bone_chains:
                if item.source_chain == item_target.name:
                    item.name = item_target.name
                    get_same = True
                    break
            
            if not get_same:
                for rule_body in rule_source_name_body:
                    if item.source_chain.lower().find(rule_body[0]) >= 0 :
                        for rule_LR in rule_source_name_LR:
                            if item.source_chain.lower().find(rule_LR[0]) >= 0 :
                                for target_name in scn.my_target_bone_chains_list[idx].bone_chains:
                                    if (target_name.name.lower().find(rule_body[1]) >=0 or target_name.name.lower().find(rule_body[0]) >=0) and target_name.name.lower().find(rule_LR[1]) >= 0:
                                        item.name = target_name.name
                                        break
                                break
                        for target_name in scn.my_target_bone_chains_list[idx].bone_chains:
                                if target_name.name.lower().find(rule_body[1]) >=0 or target_name.name.lower().find(rule_body[0]) >=0:
                                    item.name = target_name.name
                                    break
                        break

        toggle_update = True
        # recoerd_old_value()
        toggle_set_chain_map_name = True


        return {'FINISHED'}
    
class autoSetChainOP(bpy.types.Operator):
    bl_idname = 'auto_set_chain.go'
    bl_label = 'autoSetChainOP'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        selectedChain = []
        freeChain = [ a.name for a in scn.my_target_chains]

        # for targetChain in scn.my_enum_bone_chain:
        #     if targetChain.BoneChain in freeChain:
        #         freeChain.remove(targetChain.BoneChain)
        #     else:
        #         targetChain.BoneChain = freeChain[0]
        #         # freeChain.remove(0)
        #         del freeChain[0]

        FixChain = []
        # for item in scn.my_enum_bone_chain:
        #     if item.IsSelected == True :
        #         FixChain.append(item.BoneChain)
                # targetChain.BoneChain='mixamorig:Hips'
        print(FixChain)
        # map(lambda i: scn.my_target_chains.remove(scn.my_target_chains.find(i)),FixChain)
        for item in FixChain:
            idx = scn.my_target_chains.find(item)
            scn.my_target_chains[idx].IsSelected = 'Selected____'
        # scn.my_enum_bone_chain[0].BoneChain = '22'
        # print(scn.my_enum_bone_chain[0].BoneChain)
        for a in scn.my_target_chains:
            print(a )
        return {'FINISHED'}


class AN_OT_BuildList(bpy.types.Operator):
    bl_idname = 'an.build_list'
    bl_label = 'BuildList'
    bl_options = {'UNDO'}

    def execute(self, context):

        scn = bpy.context.scene

        bpy.ops.an.build_chains()

        scn.my_target_bone_chains_list.clear()
        scn.my_chain_map.clear()

        # 从python骨骼链列表转化为blender的UI使用的列表
        root_has_set = False
        for bone_chain,target_chain in zip(my_source_chains,my_target_chains):
            item = scn.my_chain_map.add()
            item.index = bone_chain['index']
            if item.index == 0 and not root_has_set:
                item.is_root = True
                root_has_set = True
            source_chain = ','.join([a.name for a in bone_chain['chain']])
            item.source_chain = source_chain
            target_chain = ','.join([a.name for a in target_chain['chain']])
            # print(target_chain)
            item.name = target_chain

            bone_chains = scn.my_target_bone_chains_list.add()
            for chain in [a['chain'] for a in my_target_chains if a['index'] == bone_chain['index']]:
                item_list = bone_chains.bone_chains.add()
                item_list.name = ','.join([a.name for a in chain])
            # print(scn.my_target_bone_chains_list)

        # 记录骨骼连的变更历史方便选择后触发自动对调
        recoerd_old_value()

        # 增加默认的骨骼命名匹配规则
        global save_new_bind_rule
        if save_new_bind_rule == False:
            build_default_bind_rule()

        bpy.ops.an.automap_bone_chains()
        select_mode(scn.my_source_rig,'OBJECT')
        return {'FINISHED'}

class AN_OT_AutoAddIgnoe(bpy.types.Operator):
    bl_idname = 'an.auto_add_ignore'
    bl_label = 'AutoAddIgnoe'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        scn.my_ignore_bone_name += ','.join(auto_add_ignore(scn.my_source_rig,scn.my_target_rig)) + ','
        scn.my_ignore_bone_name += ','.join(auto_add_ignore(scn.my_target_rig,scn.my_source_rig)) + ','
        return {'FINISHED'}

class AN_OT_AddDefaultIgnoe(bpy.types.Operator):
    bl_idname = 'an.add_default_ignore'
    bl_label = 'AddDefaultIgnoe'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        global boneIgnoreName
        scn.my_ignore_bone_name += boneIgnoreName + ','
        return {'FINISHED'}

class AN_OT_CopyRotation(bpy.types.Operator):
    bl_idname = 'copy_rotation.go'
    bl_label = 'CopyRotation'
    bl_options = {'UNDO'}

    def execute(self, context):

        # return {'FINISHED'}

        scn = bpy.context.scene
        build_bones_map()
        build_bone_tweak(self,context,scn.my_source_chains,scn.my_source_rig)
        select_mode(scn.my_source_rig,'OBJECT')

        select_mode(scn.my_target_rig,'POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.context.view_layer.update()

        fcruves = scn.my_source_rig.animation_data.action.fcurves
        for fc in fcruves:
            if fc.group.name == scn.my_source_rig.data.name:
                fc.mute = True

        # bpy.ops.nla.bake(
        # frame_start=int(scn.my_source_rig.animation_data.action.frame_range[0]),
        # frame_end=int(scn.my_source_rig.animation_data.action.frame_range[1]),
        # step=1,
        # only_selected=True,
        # visual_keying=True,
        # clear_constraints = True,
        # bake_types={'POSE'}
        # )

        fcruves = scn.my_source_rig.animation_data.action.fcurves
        for fc in fcruves:
            if fc.group.name == scn.my_source_rig.data.name:
                fc.mute = False

        root_motion()


        select_mode(scn.my_source_rig,'OBJECT')

        return {'FINISHED'}
    

    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self, width = 350)

    def draw(self, context):
        self.layout.label(text='22222222')

        # return {'FINISHED'}

            # print(source_chain)
                    # bpy.data.objects['root.001']

class AN_OT_AlightRestBone(bpy.types.Operator):
    bl_idname = 'an.alight_rest_bone'
    bl_label = 'Alight Rest Bone'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        temp_source_rig = duplicate(scn.my_source_rig)
        bpy.context.view_layer.update()
        rotate_edit_bones()
        bpy.context.view_layer.update()
        connect_bones()
        build_bones_map()
        bpy.context.view_layer.update()
        orgin_target_rig = scn.my_target_rig
        orgin_source_rig = scn.my_source_rig
        scn.my_target_rig = scn.my_source_rig
        scn.my_source_rig = temp_source_rig

        bpy.ops.an.build_list()
        build_bones_map()
        bpy.ops.copy_rotation.go()
        select_mode(scn.my_target_rig,'POSE')

        bpy.ops.pose.select_all(action='SELECT')
        bpy.context.object.data.layers[16] = True

        bpy.ops.nla.bake(
		frame_start=int(scn.my_source_rig.animation_data.action.frame_range[0]),
		frame_end=int(scn.my_source_rig.animation_data.action.frame_range[1]),
		step=1,
		only_selected=True,
		visual_keying=True,
        clear_constraints = True,
		# use_current_action=True,
		bake_types={'POSE'}
        )

        # copy_transforms(scn.my_bones_map)
        select_mode(scn.my_source_rig,'OBJECT')

        scn.my_source_rig = orgin_source_rig
        scn.my_target_rig = orgin_target_rig

        select_mode(temp_source_rig,'OBJECT')
        bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
        bpy.ops.object.delete()

        return {'FINISHED'}

class AN_OT_pick_object(bpy.types.Operator):

    #tooltip
    """Pick the selected object/bone"""

    bl_idname = "an.pick_object"
    bl_label = "pick_object"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(
        items=(
                ('pick_source', 'pick_source', ''),
                ('pick_target', 'pick_target', ''),
                ('pick_bone', 'pick_bone', ''),
                ('pick_pole', 'pick_pole', '')
            )
        )

    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            _pick_object(self.action)

        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return {'FINISHED'}
    
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
        set_armature_layer(Viewtype=True)
        # create ik bones
        for bone in ik_bones:
            if bone['type'] == 'IK':
                bone_IK = create_edit_bone(bone['name']+'_IK',1)
                bone_target = bpy.context.object.data.edit_bones.get(bone['name'])
                bone_IK.head = bone_IK.tail = eval('bone_target.'+bone['edit_bone_head'])[:]
                bone_IK.tail += bone['edit_offset']

            if bone['type'] == 'Transform':
                # duplicate original bone and child it
                bone_IK_Transfrom = create_edit_bone(bone['name']+'_IK_Transform',1)
                bone_target = bpy.context.object.data.edit_bones.get(bone['name'])
                bone_IK_Transfrom.head = bone_target.head[:]
                bone_IK_Transfrom.tail = bone_target.tail[:]
                bone_IK_Transfrom.matrix = bone_target.matrix
                
            if bone['pole_bone']:
                bone_IK_Pole = create_edit_bone(bone['name']+'_IK_Pole',1)
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
        select_mode(scn.my_source_rig,'EDIT')
        for bone in ik_bones:
            if type(bone['child_bone']) == str:
                link_bone_parent = create_edit_bone(bone['name'])
                link_bone_child = create_edit_bone(bone['child_bone'])
                link_bone_parent.tail = link_bone_child.head[:]
            else:
                link_bone_parent = create_edit_bone(bone['name'])
                link_bone_parent.tail = link_bone_parent.head + bone['child_bone']

        select_mode(scn.my_source_rig,'POSE')

        return {'FINISHED'}

class AN_OT_Bind_Rule(bpy.types.Operator):
    bl_idname = 'an.save_bind_rule'
    bl_label = 'SaveBindRule'
    bl_options = {'UNDO'}

    def execute(self, context):
        global save_new_bind_rule
        save_new_bind_rule = True

        return {'FINISHED'}

class AN_OT_BindRuleReset(bpy.types.Operator):
    bl_idname = 'an.save_bind_rule_reset'
    bl_label = 'ResetBindRule'
    bl_options = {'UNDO'}

    def execute(self, context):
        build_default_bind_rule()

        return {'FINISHED'}
    
class AN_OT_SaveIgnoreName(bpy.types.Operator):
    bl_idname = 'an.save_ignore_name'
    bl_label = 'Save Ignore Name'
    bl_options = {'UNDO'}

    def execute(self, context):
        global save_new_ignore_name 
        save_new_ignore_name = True

        return {'FINISHED'}
    
class AN_OT_ClearConstraints(bpy.types.Operator):
    bl_idname = 'an.clear_constraints'
    bl_label = 'Clear Constraints'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        select_mode(bpy.context.active_object,'POSE')
        for bone in bpy.context.active_object.pose.bones:
            for csts in bone.constraints:
                bone.constraints.remove(csts)
            # print(dir(bone.constraints))
            # break
        select_mode(bpy.context.active_object,'OBJECT')


        return {'FINISHED'}

class AN_OT_SwitchBindRule(bpy.types.Operator):
    bl_idname = 'an.switch_bind_rule'
    bl_label = 'Switch Bind Rule'
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene

        for rule in scn.my_chain_bind_rule_LR:
            a = rule.source_name
            rule.source_name = rule.name
            rule.name = a

        for rule in scn.my_chain_bind_rule_body:
            a = rule.source_name
            rule.source_name = rule.name
            rule.name = a

        # global default_rule_source_name_LR 
        # global default_rule_target_name_LR 
        # global default_rule_source_name_body 
        # global default_rule_target_name_body

        # temp_default_rule_source_name_LR = default_rule_source_name_LR 
        # temp_default_rule_target_name_LR = default_rule_target_name_LR 
        # temp_default_rule_source_name_body = default_rule_source_name_body 
        # temp_default_rule_target_name_body = default_rule_target_name_body

        # default_rule_source_name_LR = temp_default_rule_target_name_LR
        # default_rule_target_name_LR = temp_default_rule_source_name_LR
        # default_rule_source_name_body = temp_default_rule_source_name_body
        # default_rule_target_name_body = temp_default_rule_source_name_body

        bpy.ops.an.save_bind_rule()
        # global save_new_bind_rule
        # save_new_bind_rule = True
        # print(save_new_bind_rule)
        # build_default_bind_rule()

        return {'FINISHED'}
    

# Bones collection
class ARP_UL_items(bpy.types.UIList):

    @classmethod
    def poll(cls, context):
        return (context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=1.0)
        split.prop(item, "source_chain", text="", emboss=False, translate=False)
        split = layout.split(factor=1.0)
        split.prop(item, "name", text="", emboss=False, translate=False)

    def invoke(self, context, event):
        pass

class BoneChainsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "BoneChains"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        layout.label(text='sourceBoneChains')

        drawBoneChains(self,context,scn.my_source_chains)
        # for idx,item in enumerate(scn.my_source_chains):
        #     row = layout.row(align=False)
        #     row.alignment = 'LEFT'
        #     row.prop(item,'isExtraBone')
        #     row.label(text=item.name)
        #     row.split(align=True,factor=0.3)
 
            #     print(i,getattr(input,i))
        layout.label(text='targetBoneChains')
        drawBoneChains(self,context,scn.my_target_chains)



class AN_OP_Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Common Operator"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel5"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        for index,button in enumerate(reg_button):
            if index >= 0 and index%2 == 0:
                row = self.layout.row()
            if hasattr(button,'bl_label_dynamic'):
                row.operator(button.bl_idname,text=button.bl_label_dynamic)
            else:
                row.operator(button.bl_idname)

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


class AN_PT_ArmatureSet(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Armature Set"
    bl_category = "AniTool"
    bl_idname = "HI_PT_armatureset"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        scn = bpy.context.scene

        # Armature选择
        box = self.layout.box()
        row = box.row(align=True)
        row.label(text='Source Armature')
        # row.prop(scn,'source_rig',text='')
        row.prop_search(scn, "source_rig", bpy.data, "objects", text="")
        row.operator("an.pick_object", text="", icon='EYEDROPPER').action = 'pick_source'
        row.prop(scn,'my_source_rig',text='')
        row = box.row(align=True)
        row.label(text='Target Armature')
        row.prop(scn,'my_target_rig',text='')

class AN_PT_ChainList(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "ChainList"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel6"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scn = bpy.context.scene

        # Armature选择
        # box = self.layout.box()
        # row = box.row(align=True)
        # row.label(text='Source Armature')
        # row.prop(scn,'my_source_rig',text='')
        # row = box.row(align=True)
        # row.label(text='Target Armature')
        # row.prop(scn,'my_target_rig',text='')

        # 指定骨骼屏蔽
        box = self.layout.box()
        row = box.row()
        row.label(text='Ignore Bone Name Set')
        row.operator('an.auto_add_ignore')
        row.operator('an.add_default_ignore')
        row.operator('an.clear_ignore_bone')
        row = box.row()
        row.prop(scn,'my_ignore_bone_name',text='')

        # 尝试自动绑定骨骼lm

        box = self.layout.box()
        col = box.column()
        row = box.row()
        row.prop(scn, "an_bind_rule_expand_ui", icon="TRIA_DOWN" if scn.an_bind_rule_expand_ui else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text='Set Name Bind Rule')
        row.operator('an.switch_bind_rule')

        if scn.an_bind_rule_expand_ui:
            col = box.column()
            col.label(text='Set Left And Right Bind Rule')
            for prop in scn.my_chain_bind_rule_LR :
                row = box.row(align=False)
                row.prop(prop,'source_name',text='')
                row.prop(prop,'name',text='')
                
            col = box.column()
            col.label(text='Set Body Bind Rule')
            for prop in scn.my_chain_bind_rule_body :
                row = box.row(align=False)
                row.prop(prop,'source_name',text='')
                row.prop(prop,'name',text='')

            col = box.column()
            row = box.row(align=False)
            row.operator('an.save_bind_rule')
            row.operator('an.save_bind_rule_reset')

        # copy rest pose模式设置
        box = self.layout.box()
        row = box.row()
        row.label(text='set copy rest pose rule')
        row.operator('an.copy_rest_pose')
        row = box.row()
        row.prop(scn,'my_copy_rest_pose_rule')

        # 骨骼链表
        self.layout.template_list("ARP_UL_items", "", scn, "my_chain_map", scn, "my_chain_map_index",rows = 11)

        # 匹配信息导出和导入
        box = self.layout.box()
        row = box.row()
        row.operator('an.export_map')
        row.operator('an.import_map')

        # 骨骼链信息配置
        if scn.my_chain_map_index >= 0 :
            box = self.layout.box()
            row = box.row(align=True)
            if len(scn.my_chain_map) > 0 :
                row.label(text=scn.my_chain_map[scn.my_chain_map_index].source_chain)
                row.prop_search(scn.my_chain_map[scn.my_chain_map_index],'name',scn.my_target_bone_chains_list[scn.my_chain_map_index],'bone_chains',text='')
                row = box.row(align=True)
                row.prop(scn.my_chain_map[scn.my_chain_map_index],'is_root')
                # row.prop(scn.my_chain_map[scn.my_chain_map_index],'add_to_ignore_source')
                # row.prop(scn.my_chain_map[scn.my_chain_map_index],'add_to_ignore_target')
                split = box.split(factor=0.5)
                col = split.column()
                if len(scn.my_chain_map[scn.my_chain_map_index].source_bones):
                    for bone in scn.my_chain_map[scn.my_chain_map_index].source_bones:
                        row = col.row(align=True)
                        row.prop(bone,'is_ignore',text='')
                        row.label(text=bone.name)
                split = split.split(factor=1)
                col = split.column()
                if len(scn.my_chain_map[scn.my_chain_map_index].target_bones):
                    for bone in scn.my_chain_map[scn.my_chain_map_index].target_bones:
                        row = col.row(align=True)
                        row.prop(bone,'is_ignore',text='')
                        row.label(text=bone.name)


classes = [
        # Armature Set
        AN_PT_ArmatureSet,
        AN_PROP_BoneIgnore,
        AN_OT_AddDefaultIgnoe,
        AN_OT_AutoAddIgnoe,
        AN_OT_ExportMap,
        AN_OT_ImportMap,
        AN_OT_ApplyRestPose,
        AN_OT_CopyRestPose,
        AN_OT_SwitchBindRule,
        AN_OT_ClearConstraints,
        AN_OT_SaveIgnoreName,
        AN_OT_BindRuleReset,
        AN_OT_Bind_Rule,
        AN_OT_AlightRestBone,

        AN_PT_PanelIK,
        AN_PT_PanelIK_Bone,
        AN_OT_pick_object,
        AN_OT_AddIKBone,
        AN_OT_AddTempIKBone,
        AN_OT_ToggleIK,
        AN_OT_LinkIKBones,

        AN_PT_ChainList,
        AN_PGT_ChainBindRule,
        AN_OP_Panel,
        ARP_UL_items,
        BonesMap,
        AN_OT_CopyRotation,
        AN_PROP_ChainMap,
        AN_OT_BuildList,
        autoSetChainOP,
        AN_OT_AutomapBoneChains,
        boneList,
        BoneChains,
        BoneChainsList,
        AN_OT_ClearIgnoreBone,
        AN_OT_BuildChains,
        EnumBoneCHain,
        AN_OT_SetActionRange,
        
        #Properties
        
        ]

reg_button = [
    AN_OT_AutomapBoneChains,
    AN_OT_AlightRestBone,
    autoSetChainOP,
    AN_OT_BuildList,
    AN_OT_CopyRotation,
    AN_OT_ClearConstraints,
    AN_OT_CopyRestPose,
    AN_OT_ApplyRestPose,
    AN_OT_SetActionRange,
]

ik_button = [
    AN_OT_AddIKBone,
    AN_OT_AddTempIKBone,
    AN_OT_ToggleIK,
    AN_OT_LinkIKBones
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_copy_rest_pose_rule = bpy.props.EnumProperty(items=(('U2U','Unreal to Unreal','Unreal to Unreal'),('U2M','Unreal to Mixamo','Unreal to Mixamo')))
    bpy.types.Scene.my_test_string = bpy.props.StringProperty(update=update_string)
    bpy.types.Scene.my_sourceBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_source_chains = bpy.props.CollectionProperty(type=BoneChains)
    bpy.types.Scene.my_target_bone_chains_list = bpy.props.CollectionProperty(type=BoneChainsList)
    bpy.types.Scene.my_targetBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_target_chains = bpy.props.CollectionProperty(type=BoneChains)
    bpy.types.Scene.my_target_chainsRig = bpy.props.CollectionProperty(type=BoneChainsList)
    bpy.types.Scene.my_ignore_bone_name = bpy.props.StringProperty()
    bpy.types.Scene.my_chain_map = bpy.props.CollectionProperty(type=AN_PROP_ChainMap)
    bpy.types.Scene.my_bones_map = bpy.props.CollectionProperty(type=BonesMap)
    bpy.types.Scene.my_chain_map_index = bpy.props.IntProperty()
    bpy.types.Scene.an_bind_rule_expand_ui = bpy.props.BoolProperty()
    bpy.types.Scene.my_chain_bind_rule_LR = bpy.props.CollectionProperty(type=AN_PGT_ChainBindRule)
    bpy.types.Scene.my_chain_bind_rule_body = bpy.props.CollectionProperty(type=AN_PGT_ChainBindRule)
    bpy.types.Scene.my_source_rig = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.source_rig = bpy.props.StringProperty(get=get_source_rig,set=set_source_rig)
    bpy.types.Scene.my_target_rig = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.color_set_text = bpy.props.FloatVectorProperty(name="Color Text", subtype="COLOR_GAMMA",
                                                                   default=(0.887, 0.887, 0.887), min=0.0, max=1.0,
                                                                   description="Text color in the picker panel")


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_copy_rest_pose_rule
    del bpy.types.Scene.my_test_string
    del bpy.types.Scene.my_source_chains
    del bpy.types.Scene.my_target_bone_chains_list
    del bpy.types.Scene.my_sourceBoneChain
    del bpy.types.Scene.my_target_chains
    del bpy.types.Scene.my_target_chainsRig
    del bpy.types.Scene.my_targetBoneChain
    del bpy.types.Scene.my_ignore_bone_name
    del bpy.types.Scene.color_set_text
    del bpy.types.Scene.my_chain_map
    del bpy.types.Scene.my_source_rig
    del bpy.types.Scene.source_rig
    del bpy.types.Scene.my_target_rig
    del bpy.types.Scene.my_chain_bind_rule_LR
    del bpy.types.Scene.my_chain_bind_rule_body
    del bpy.types.Scene.my_bones_map
    del bpy.types.Scene.my_chain_map_index
    del bpy.types.Scene.an_bind_rule_expand_ui

if __name__ == "__main__":
    register()