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
import random
from .ReampArmature import *
import math

bl_info = {
    "name" : "PanelPratise",
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
TOGGLE_UPDATE = True
save_new_bind_rule = False
save_new_ignore_name = False
# boneIgnoreName = ['thigh_twist_01_l','calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
boneIgnoreName = 'thigh_twist_01_l,calf_twist_01_r,calf_twist_01_l,thigh_twist_01_r,upperarm_twist_01_l,upperarm_twist_01_r,lowerarm_twist_01_l,lowerarm_twist_01_r,ik_hand_root,ik_hand_r,ik_foot_root,ik_foot_r,ik_foot_l'
ik_bone = 'lowerarm_r,calf_r,lowerarm_l,calf_l'

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
    # items = (
    #     ("humanoid", "Humanoid", "Humanoid rig type, simple bones hierarchy to ensure animation retargetting"),
    #     ("mped", "Universal", "Universal rig type, simple bones hierarchy for any creature (dog, spider...)")
    #     )
    items = []
    for item in bpy.context.scene.my_target_chains.values():
        Bones = ''
        Bones += item.IsSelected
        for bone in item.bone_chain.values():
            Bones += bone.name
        items.append((Bones,Bones,''))

    # bpy.context.scene.enum_Add.add()
    # print(items)
    # items = []
    
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

def create_edit_bone(bone_name):
    # b = get_edit_bone(bone_name)
    # if b == None:
    if bpy.context.active_object.data.edit_bones.get(bone_name):
        b = bpy.context.active_object.data.edit_bones.get(bone_name)
    else:
        b = bpy.context.active_object.data.edit_bones.new(bone_name)
        # b.use_deform = deform
    return b

def create_constraint(rig,bone_name,cst_name,type):
    for cnsts in rig.pose.bones[bone_name].constraints:
        if cnsts.name == cst_name:
            return cnsts
    cst = rig.pose.bones[bone_name].constraints.new(type)
    cst.name = cst_name
    return cst

def copy_bone_transforms(bone1, bone2):
    # copy editbone bone1 transforms to bone 2
    # if bone1 == None or bone2 == None:       
    #     return
        
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

    # for item_bone in scn.my_bones_map:

    #     print(item_bone.source_bone,item_bone.name)

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

    local_armature_name = scn.target_rig + "_local"

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
    if TOGGLE_UPDATE:
    # bpy.ops.build_chains.go()
        filter_name()

def recoerd_old_value():
    scn = bpy.context.scene
    for item in scn.my_chain_map:
        item.old_name = item.name

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

    default_rule_source_name_LR = ['_l','_r']
    default_rule_target_name_LR = ['Left','Right']
    default_rule_source_name_body = ['index','middle','pinky','ring','thumb']
    default_rule_target_name_body = ['Index','Middle','Pinky','Ring','Thumb']

    for source_name , name in zip(default_rule_source_name_LR,default_rule_target_name_LR):
        item = scn.my_chain_bind_rule_LR.add()
        item.source_name = source_name
        item.name = name

    for source_name , name in zip(default_rule_source_name_body,default_rule_target_name_body):
        item = scn.my_chain_bind_rule_body.add()
        item.source_name = source_name
        item.name = name

def select_mode(obj,mode):
        scn = bpy.context.scene
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        obj.hide_set(False)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(state=True)
        bpy.ops.object.mode_set(mode=mode)

class TestStringFunction(bpy.types.PropertyGroup):
    test_string:bpy.props.StringProperty(set=None)

class enumAdd(bpy.types.PropertyGroup):
    # @classmethod
    # def register(cls):
    #     bpy.types.Scene.enum_Add = bpy.props.CollectionProperty(type=enumAdd)

    # @classmethod
    # def unregister(cls):
    #     del bpy.types.Scene.enum_Add

    string : bpy.props.StringProperty()

class EnumBoneCHain(bpy.types.PropertyGroup):
    BoneChain:bpy.props.EnumProperty(items=getItem)
    IsSelected:bpy.props.BoolProperty()
    # BoneChain:bpy.props.EnumProperty(items=getItem,get=get_enum, set=set_enum)

#define what the property in the colection will look like

# bpy.context.scene.globalvalue = 3

class myBone(bpy.types.PropertyGroup):
    bone:bpy.props.PointerProperty(type=bpy.types.Action)


class boneList(bpy.types.PropertyGroup):
    # bone:bpy.props.CollectionProperty(type=bpy.types.PoseBone)
    index:bpy.props.IntProperty()
    name:bpy.props.StringProperty()

class myString(bpy.types.PropertyGroup):
    string:bpy.props.StringProperty()

class BoneChains(bpy.types.PropertyGroup):
    isExtraBone:bpy.props.BoolProperty()
    IsSelected:bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    bone_chain:bpy.props.CollectionProperty(type=boneList)
    index:bpy.props.IntProperty()
    is_root:bpy.props.BoolProperty()

class BoneChainsList(bpy.types.PropertyGroup):
    bone_chains: bpy.props.CollectionProperty(type=BoneChains)

class ChainMap(bpy.types.PropertyGroup):
    is_root:bpy.props.BoolProperty()
    index:bpy.props.IntProperty()
    source_chain: bpy.props.StringProperty()
    name:bpy.props.StringProperty(update=update_string)
    old_name:bpy.props.StringProperty()
    

class BonesMap(bpy.types.PropertyGroup):
    source_bone: bpy.props.StringProperty()
    is_root:bpy.props.BoolProperty()

class AN_PGT_ChainBindRule(bpy.types.PropertyGroup):
    source_name: bpy.props.StringProperty()

#operator, connected the button that adds the params
class BuildChains(bpy.types.Operator):
    bl_idname = 'build_chains.go'
    bl_label = 'showBonechains'
    slot: bpy.props.IntProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        scn.my_source_chains.clear()

        # boneIgnoreName = ['thigh_twist_01_l','calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        # boneIgnoreName = ['calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        
        # for idx,bone in enumerate(scn.my_ignore_bone_name):
        #     boneIgnoreName.append(str(bone.name))
        self.sourceArmature = ArmatureBoneInfo(scn.my_source_rig)
        self.targetArmature = ArmatureBoneInfo(scn.my_target_rig)
        # a.boneIgnoreName.append('thigh_twist_01_l')
        global boneIgnoreName
        if save_new_ignore_name == True:
            boneIgnoreName_str = scn.my_ignore_bone_name
            boneIgnoreName_list = boneIgnoreName_str.split(',')

        else:
            scn.my_ignore_bone_name = boneIgnoreName
            boneIgnoreName_list = scn.my_ignore_bone_name.split(',')

        self.sourceArmature.boneIgnoreName += boneIgnoreName_list
        self.targetArmature.boneIgnoreName += boneIgnoreName_list

        global my_source_chains
        my_source_chains = self.sourceArmature.bone_chains

        global my_target_chains
        my_target_chains = self.targetArmature.bone_chains

        # print(my_source_chains)

        # set_bone_chain(self,context,self.sourceArmature.bone_chains,scn.my_source_chains)
        # set_bone_chain(self,context,self.targetArmature.bone_chains,scn.my_target_chains)

        # sortBoneChains(self,context,scn.my_source_chains)
        # sortBoneChains(self,context,scn.my_target_chains)

        scn.my_enum_bone_chain.clear()
        for item in scn.my_source_chains.values():
            scn.my_enum_bone_chain.add()
        
        # newItems
        return {'FINISHED'}


class SaveBoneChainsOP(bpy.types.Operator):
    bl_idname = 'savebonechains.go'
    bl_label = 'saveBoneChains'
    
    def execute(self, context):
        #add the param to the registered collection
        # print(idxNeedRmove)
        scn = bpy.context.scene
        scn.my_enum_bone_chain.add()

        # item = scn.my_customeProperty.add()

        # for idx,item in enumerate(scn.my_customeProperty):
        #     attr = [a for a in dir(item)]
        #     for b in attr:
        #         print(b,getattr(item,b))

        # for idx,bone_chain in enumerate(scn.my_source_chains):
        #     if bone_chain.isExtraBone == True:
        #         for idx,bone in enumerate(bone_chain.bone_chain):
        #             item = scn.my_ignore_bone_name.add()
        #             item.name = bone.name

        #             break
                # bone_chain.remove()
        # for idx,bone in enumerate(scn.my_ignore_bone_name):
        #     pass
            # print(bone.name,idx)
        # print
      

        # context.scene.BoneChainsList.remove(0)
        return {'FINISHED'}        
    
class clearIgnoreBone(bpy.types.Operator):
    bl_idname = 'clear_ignore_bone.go'
    bl_label = 'clearIgnoreBone'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        scn.my_ignore_bone_name.clear()
        return {'FINISHED'}

class AN_OP_AddIKBone(bpy.types.Operator):
    bl_idname = 'an.add_ikbone'
    bl_label = 'Add IKBone'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        global ik_bone
        ik_bone_list = ik_bone.split(',')
        select_mode(scn.my_source_rig,'EDIT')
        for bone in ik_bone_list:
            bone_IK = create_edit_bone(bone+'_IK')
            bone_foot = bpy.context.object.data.edit_bones.get(bone)
            bone_IK.head = bone_foot.tail
            bone_IK.tail = bone_IK.head[:]
            bone_IK.tail[1] += 20

        

        for bone in ik_bone_list:
            bone_IK = create_edit_bone(bone+'_IK')
            cst = create_constraint(scn.my_source_rig,bone_IK.name,'Copy Transform IK','COPY_LOCATION')
            cst.target = scn.my_source_rig
            cst.head_tail = 1
            cst.subtarget = bone

        select_mode(scn.my_source_rig,'POSE')

        bpy.ops.pose.select_all(action='SELECT')

        bpy.ops.nla.bake(
		frame_start=int(scn.my_target_rig.animation_data.action.frame_range[0]),
		frame_end=int(scn.my_target_rig.animation_data.action.frame_range[1]),
		step=1,
		only_selected=True,
		visual_keying=True,
        clear_constraints = True,
		# use_current_action=True,
		bake_types={'POSE'}
        )
        # return {'FINISHED'}

        select_mode(scn.my_source_rig,'POSE')
        for bone in ik_bone_list:
            cst = create_constraint(scn.my_source_rig,bone,'IK_Anitool','IK')
            cst.target = scn.my_source_rig
            cst.subtarget = bone+'_IK'
            cst.chain_count = 2

        select_mode(scn.my_source_rig,'OBJECT')
        return {'FINISHED'}
    

class AutomapBoneChainsOP(bpy.types.Operator):
    bl_idname = 'automap_bone_chains.go'
    bl_label = 'AutomapBoneChains'

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        global TOGGLE_UPDATE
        TOGGLE_UPDATE = False
        rule_source_name_LR = [(a.source_name,a.name) for a in scn.my_chain_bind_rule_LR]
        rule_source_name_body = [(a.source_name,a.name) for a in scn.my_chain_bind_rule_body]

        temp_my_chain_map = [a.name for a in scn.my_chain_map]
        # temp_my_chain_map = [a.name for a in my_target_chains]
        for idx,item in enumerate(scn.my_chain_map):
            for item_target in (my_target_chains):
                if item.source_chain == ','.join(a.name for a in  item_target['chain']):
                    item.name = ','.join(a.name for a in  item_target['chain'])
                    break
                else:
                    for rule_body in rule_source_name_body:
                        # print(item.source_chain.find(rule_body[0]))
                        if item.source_chain.find(rule_body[0]) >= 0 :
                            for rule_LR in rule_source_name_LR:
                                if item.source_chain.find(rule_LR[0]) >= 0 :
                                    for target_name in scn.my_target_bone_chains_list[idx].bone_chains:
                                        if target_name.name.find(rule_body[1]) >=0 and target_name.name.find(rule_LR[1]) >= 0:
                                            item.name = target_name.name

        TOGGLE_UPDATE = True
        recoerd_old_value()


        return {'FINISHED'}
    
class autoSetChainOP(bpy.types.Operator):
    bl_idname = 'auto_set_chain.go'
    bl_label = 'autoSetChainOP'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
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
        for item in scn.my_enum_bone_chain:
            if item.IsSelected == True :
                FixChain.append(item.BoneChain)
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


class BuildList(bpy.types.Operator):
    bl_idname = 'build_list.go'
    bl_label = 'BuildList'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):

        scn = bpy.context.scene
        # print(scn.my_target_chains)
        # print(scn.my_target_rig)

        bpy.ops.build_chains.go()

        scn.my_target_bone_chains_list.clear()
        scn.my_chain_map.clear()

        # 从python骨骼链列表转化为blender的UI使用的列表
        for bone_chain,target_chain in zip(my_source_chains,my_target_chains):
            item = scn.my_chain_map.add()
            item.index = bone_chain['index']
            if item.index == 0 :
                item.is_root = True
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

        if save_new_bind_rule == False:
            build_default_bind_rule()


        bpy.ops.automap_bone_chains.go()

        select_mode(scn.my_source_rig,'OBJECT')
        return {'FINISHED'}

class CopyRotation(bpy.types.Operator):
    bl_idname = 'copy_rotation.go'
    bl_label = 'CopyRotation'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        build_bones_map()
        build_bone_tweak(self,context,scn.my_source_chains,scn.my_source_rig)
        select_mode(scn.my_source_rig,'OBJECT')
        return {'FINISHED'}
    

    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self, width = 350)

    def draw(self, context):
        self.layout.label(text='22222222')

        # return {'FINISHED'}

            # print(source_chain)
                    # bpy.data.objects['root.001']

class AN_OT_ChangeRestPose(bpy.types.Operator):
    bl_idname = 'an.changerestpose'
    bl_label = 'ChangeRestPose'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
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

        return {'FINISHED'}
    
class AN_OT_Bind_Rule(bpy.types.Operator):
    bl_idname = 'an.save_bind_rule'
    bl_label = 'SaveBindRule'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        save_new_bind_rule = True

        return {'FINISHED'}

class AN_OT_BindRuleReset(bpy.types.Operator):
    bl_idname = 'an.save_bind_rule_reset'
    bl_label = 'ResetBindRule'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        build_default_bind_rule()

        return {'FINISHED'}
    
class AN_OT_SaveIgnoreName(bpy.types.Operator):
    bl_idname = 'an.save_ignore_name'
    bl_label = 'Save Ignore Name'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        global save_new_ignore_name 
        save_new_ignore_name = True

        return {'FINISHED'}
    
class AN_OT_ClearConstraints(bpy.types.Operator):
    bl_idname = 'an.clear_constraints'
    bl_label = 'Clear Constraints'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        select_mode(bpy.context.active_object,'POSE')
        for bone in bpy.context.active_object.pose.bones:
            for csts in bone.constraints:
                bone.constraints.remove(csts)
            # print(dir(bone.constraints))
            # break
        select_mode(bpy.context.active_object,'OBJECT')


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

class RemapPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Remap"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel4"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context: 'Context'):
        scn = bpy.context.scene
        split = self.layout.split(factor=0.3)
        column = split.column()
        column.label(text = 'SourceChain')
        for item in scn.my_source_chains:
            row = column.row()
            row.label(text=item.name)

        split = split.split(factor=1)
        column = split.column()
        column.label(text = 'TargetChain')
        for idx,item in enumerate(scn.my_source_chains):
            row=column.row()
            row.alignment = 'LEFT'
            row.prop(scn.my_enum_bone_chain[idx],'IsSelected')
            row.prop(scn.my_enum_bone_chain.values()[idx],'BoneChain',text='')

class OpPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Operator"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel5"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context: 'Context'):
        row = self.layout.row()
        row.operator("build_chains.go")
        row.operator("savebonechains.go")
        row.operator("clear_ignore_bone.go")
        row.operator("automap_bone_chains.go")
        row = self.layout.row()
        row.operator("an.changerestpose")
        row.operator("auto_set_chain.go")
        row.operator("build_list.go")
        row.operator("copy_rotation.go")
        row = self.layout.row()
        row.operator("an.clear_constraints")
        row.operator("an.add_ikbone")

class ChainList_PT(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "ChainList"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel6"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context: 'Context'):
        scn = bpy.context.scene

        # Armature选择
        box = self.layout.box()
        row = box.row(align=True)
        row.label(text='Source Armature')
        row.prop(scn,'my_source_rig',text='')
        row = box.row(align=True)
        row.label(text='Target Armature')
        row.prop(scn,'my_target_rig',text='')

        # 指定骨骼屏蔽
        box = self.layout.box()
        row = box.row()
        row.label(text='Ignore Bone Name Set')
        row.operator('an.save_ignore_name')
        row = box.row()
        row.prop(scn,'my_ignore_bone_name',text='')

        # 尝试自动绑定骨骼lm

        box = self.layout.box()
        col = box.column()
        row = box.row()
        row.prop(scn, "an_bind_rule_expand_ui", icon="TRIA_DOWN" if scn.an_bind_rule_expand_ui else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text='Set Name Bind Rule')

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



        # 骨骼链表
        self.layout.template_list("ARP_UL_items", "", scn, "my_chain_map", scn, "my_chain_map_index",rows = 11)

        # 骨骼链信息配置
        if scn.my_chain_map_index >= 0 :
            box = self.layout.box()
            row = box.row(align=True)

            row.label(text=scn.my_chain_map[scn.my_chain_map_index].source_chain)
            row.prop_search(scn.my_chain_map[scn.my_chain_map_index],'name',scn.my_target_bone_chains_list[scn.my_chain_map_index],'bone_chains',text='')
            row = box.row(align=True)
            row.prop(scn.my_chain_map[scn.my_chain_map_index],'is_root')


classes = [AN_OP_AddIKBone,
           AN_OT_ClearConstraints,
           AN_OT_SaveIgnoreName,
           AN_OT_BindRuleReset,
           AN_OT_Bind_Rule,
           AN_OT_ChangeRestPose,
           AN_PGT_ChainBindRule,
           TestStringFunction,
           ARP_UL_items,
           BonesMap,
           CopyRotation,
           ChainMap,
           ChainList_PT,
           BuildList,
           autoSetChainOP,
           AutomapBoneChainsOP,
           myBone,
           boneList,
           BoneChains,
           BoneChainsList,
           myString,
           clearIgnoreBone,
           RemapPanel,
           BoneChainsPanel,
           SaveBoneChainsOP,
           OpPanel,
           BuildChains,
           enumAdd,
           EnumBoneCHain]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_test_string = bpy.props.StringProperty(update=update_string)
    bpy.types.Scene.enum_Add = bpy.props.CollectionProperty(type=enumAdd)
    bpy.types.Scene.my_sourceBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_source_chains = bpy.props.CollectionProperty(type=BoneChains)
    bpy.types.Scene.my_target_bone_chains_list = bpy.props.CollectionProperty(type=BoneChainsList)
    bpy.types.Scene.my_targetBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_target_chains = bpy.props.CollectionProperty(type=BoneChains)
    bpy.types.Scene.my_target_chainsRig = bpy.props.CollectionProperty(type=BoneChainsList)
    bpy.types.Scene.my_ignore_bone_name = bpy.props.StringProperty()
    bpy.types.Scene.my_enum_bone_chain = bpy.props.CollectionProperty(type=EnumBoneCHain)
    bpy.types.Scene.my_chain_map = bpy.props.CollectionProperty(type=ChainMap)
    bpy.types.Scene.my_bones_map = bpy.props.CollectionProperty(type=BonesMap)
    bpy.types.Scene.my_chain_map_index = bpy.props.IntProperty()
    bpy.types.Scene.an_bind_rule_expand_ui = bpy.props.BoolProperty()
    bpy.types.Scene.my_chain_bind_rule_LR = bpy.props.CollectionProperty(type=AN_PGT_ChainBindRule)
    bpy.types.Scene.my_chain_bind_rule_body = bpy.props.CollectionProperty(type=AN_PGT_ChainBindRule)
    bpy.types.Scene.my_source_rig = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.my_target_rig = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.color_set_panel = bpy.props.FloatVectorProperty(name="Color Panel", subtype="COLOR_GAMMA",
                                                                    default=(0.2, 0.2, 0.2), min=0.0, max=1.0,
                                                                    description="Back picker panel color")
    bpy.types.Scene.color_set_text = bpy.props.FloatVectorProperty(name="Color Text", subtype="COLOR_GAMMA",
                                                                   default=(0.887, 0.887, 0.887), min=0.0, max=1.0,
                                                                   description="Text color in the picker panel")


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_test_string
    del bpy.types.Scene.enum_Add
    del bpy.types.Scene.my_source_chains
    del bpy.types.Scene.my_target_bone_chains_list
    del bpy.types.Scene.my_sourceBoneChain
    del bpy.types.Scene.my_target_chains
    del bpy.types.Scene.my_target_chainsRig
    del bpy.types.Scene.my_targetBoneChain
    del bpy.types.Scene.my_ignore_bone_name
    del bpy.types.Scene.my_enum_bone_chain
    del bpy.types.Scene.color_set_panel
    del bpy.types.Scene.color_set_text
    del bpy.types.Scene.my_chain_map
    del bpy.types.Scene.my_source_rig
    del bpy.types.Scene.my_target_rig
    del bpy.types.Scene.my_chain_bind_rule_LR
    del bpy.types.Scene.my_chain_bind_rule_body
    del bpy.types.Scene.my_bones_map
    del bpy.types.Scene.my_chain_map_index
    del bpy.types.Scene.an_bind_rule_expand_ui

if __name__ == "__main__":
    register()