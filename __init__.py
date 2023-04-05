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
# bpy.props.
# 通过remap获得bonechains信息
# 将信息储存到scene的collisionproperty中
# 用两个collection来保存bonechain，因为是一个数列里面还有一个数列
# 用check和label来表示source中的chain
# 然后去除对应的不要的chain
# 最后用label source enumerate target来匹配chain的手动选择
# 用新的collection来做匹配关系
# 按照chain的对应方式来添加copy rotation
# 
# 待加入流程：
# auto scale
# chain的bone的数量怎么一一对应中
# 做智能化对应 


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
    b = bpy.context.active_object.data.edit_bones.new(bone_name)
        # b.use_deform = deform
    return b
    bpy.context.active_object.data.edit_bones.new(bone_name)

def copy_bone_transforms(bone1, bone2):
    # copy editbone bone1 transforms to bone 2
    # if bone1 == None or bone2 == None:       
    #     return
        
    bone2.head = bone1.head.copy()
    bone2.tail = bone1.tail.copy()
    bone2.roll = bone1.roll

def set_active_object(object_name):
     bpy.context.view_layer.objects.active = object_name
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
            try:
                for bone_idx,bone_item in enumerate(scn.my_target_chains[scn.my_target_chains.find(chain_item.name)].bone_chain):
                    item = scn.my_bones_map.add()
                    item.source_bone = scn.my_source_chains[scn.my_source_chains.find(chain_item.source_chain)].bone_chain[bone_idx].name
                    item.name = bone_item.name

                    if chain_item.is_root:
                        item.is_root = True
            except Exception:
                print("error bone",bone_item.name)

    # for item_bone in scn.my_bones_map:
    #     print(item_bone.source_bone,item_bone.name)

def build_bone_tweak(self,context,scn_source_chains,scn_source_rig):
    scn = bpy.context.scene

    scn_target_rig = scn.my_target_rig
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
    # scn_source_rig.select_set(state=True)
    bpy.ops.object.mode_set(mode='EDIT')
    # bpy.ops.object.select_all(action='DESELECT')

    # scn_source_rig.select_set(state=True)

    # return

    bone_names = [b.name for b in scn_source_rig.data.edit_bones]
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
                cns.name += 'REMAP'
                
                bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = scn_target_rig
    scn_target_rig.select_set(state=True)
    bpy.data.objects['Armature'].select_set(state=True)
    bpy.ops.object.mode_set(mode='POSE')

    scn_target_rig.animation_data.action = None

    for bone_item in scn.my_bones_map:
        if bone_item.name != "" and bone_item.name != "None" and context.active_object.pose.bones.get(bone_item.name):
            
            pose_bone = context.active_object.pose.bones[bone_item.name]              
            context.active_object.data.bones.active = pose_bone.bone
            
            # Add constraints
            # main rotation
            cns = pose_bone.constraints.new('COPY_ROTATION')
            cns.target = scn_source_rig
            cns.subtarget = bone_item.name + "_REMAP"
            cns.name += 'REMAP'

            if bone_item.is_root:
                cns_root = pose_bone.constraints.new('COPY_LOCATION')
                cns_root.target = scn_source_rig
                cns_root.subtarget = bone_item.name + "_ROOT"
                cns_root.name += '_loc_REMAP'                 
                cns_root.owner_space = cns_root.target_space = 'WORLD'

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
    source_chain: bpy.props.StringProperty()

class BonesMap(bpy.types.PropertyGroup):
    source_bone: bpy.props.StringProperty()
    is_root:bpy.props.BoolProperty()


#operator, connected the button that adds the params
class BuildChains(bpy.types.Operator):
    bl_idname = 'build_chains.go'
    bl_label = 'showBonechains'
    slot: bpy.props.IntProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        scn.my_source_chains.clear()

        scn.my_source_rig = bpy.data.objects['root']
        # source_rig = bpy.data.objects['root.001']
        scn.my_target_rig = bpy.data.objects['Armature']
        # target_rig = bpy.data.objects['Armature.001']

        print(scn.my_target_rig)
        # boneIgnoreName = ['thigh_twist_01_l','calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        boneIgnoreName = ['calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        
        for idx,bone in enumerate(scn.my_ignore_bone_name):
            boneIgnoreName.append(str(bone.name))
        self.sourceArmature = ArmatureBoneInfo(scn.my_source_rig)
        self.targetArmature = ArmatureBoneInfo(scn.my_target_rig)
        # a.boneIgnoreName.append('thigh_twist_01_l')
        self.sourceArmature.boneIgnoreName += boneIgnoreName
        self.targetArmature.boneIgnoreName += boneIgnoreName

        set_bone_chain(self,context,self.sourceArmature.bone_chains,scn.my_source_chains)
        set_bone_chain(self,context,self.targetArmature.bone_chains,scn.my_target_chains)

        sortBoneChains(self,context,scn.my_source_chains)
        sortBoneChains(self,context,scn.my_target_chains)

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

        for idx,bone_chain in enumerate(scn.my_source_chains):
            if bone_chain.isExtraBone == True:
                for idx,bone in enumerate(bone_chain.bone_chain):
                    item = scn.my_ignore_bone_name.add()
                    item.name = bone.name

                    break
                # bone_chain.remove()
        for idx,bone in enumerate(scn.my_ignore_bone_name):
            pass
            # print(bone.name,idx)
        # print
      

        # context.scene.BoneChainsList.remove(0)
        return {'FINISHED'}        
    
class clearIgnoreBone(bpy.types.Operator):
    bl_idname = 'clear_ignore_bone.go'
    bl_label = 'clearIgnoreBone'

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        scn.my_ignore_bone_name.clear()
        return {'FINISHED'}

class sortBoneChainsOP(bpy.types.Operator):
    bl_idname = 'sort_bone_chains.go'
    bl_label = 'sortBoneChains'

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        scn.my_ignore_bone_name.clear()
        return {'FINISHED'}
    
class autoSetChainOP(bpy.types.Operator):
    bl_idname = 'auto_set_chain.go'
    bl_label = 'autoSetChainOP'

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

    def execute(self, context: 'Context'):

        scn = bpy.context.scene
        # print(scn.my_target_chains)
        # print(scn.my_target_rig)


        scn.my_target_bone_chains_list.clear()
        scn.my_chain_map.clear()

        for item in scn.my_target_chains:
            bone_chains = scn.my_target_bone_chains_list.add()
            for item in scn.my_target_chains:

                item2 = bone_chains.bone_chains.add()
                item2.name = item.name
        
        for bone_chain in scn.my_source_chains:
            item = scn.my_chain_map.add()
            item.source_chain = bone_chain.name

        # for item in scn.my_target_bone_chains_list[0]:
        #     print(item.name)
        # print(dir(scn.my_target_bone_chains_list[0]))

        return {'FINISHED'}

class CopyRotation(bpy.types.Operator):
    bl_idname = 'copy_rotation.go'
    bl_label = 'CopyRotation'
    bl_options = {'UNDO'}

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        build_bones_map()
        build_bone_tweak(self,context,scn.my_source_chains,scn.my_source_rig)

        return {'FINISHED'}
    
        for item in scn.my_chain_map:
            source_chain = item.source_chain
            target_chain = item.name

            if target_chain :
                for idx,item2 in enumerate(scn.my_source_chains[scn.my_source_chains.find(source_chain)].bone_chain):
                    source_bone = item2.name
                    target_bone = scn.my_target_chains[scn.my_target_chains.find(target_chain)].bone_chain[idx].name
                    print(target_bone)
                    print(scn.my_target_chains.find(target_chain))

                    print(scn.my_target_rig)
                    cst = scn.my_target_rig.pose.bones[target_bone].constraints.new("COPY_ROTATION")
                    cst.target = scn.my_source_rig
                    cst.subtarget = source_bone

    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self, width = 350)

    def draw(self, context):
        self.layout.label(text='22222222')

        # return {'FINISHED'}

            # print(source_chain)
                    # bpy.data.objects['root.001']


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
        row = self.layout.row()
        row.operator("auto_set_chain.go")
        row.operator("build_list.go")
        row.operator("copy_rotation.go")

class ChainList(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "ChainList"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel6"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context: 'Context'):
        scn = bpy.context.scene
        self.layout.template_list("ARP_UL_items", "", scn, "my_chain_map", scn, "my_chain_map_index",rows = 11)

        row = self.layout.row()
        scn = bpy.context.scene
        # for idx,item in enumerate(scn.my_source_chains):
        #     row = self.layout.row()
        #     row.label(text=scn.my_chain_map[idx].source_chain)
        #     row.prop_search(scn.my_chain_map[idx],'name',scn.my_target_bone_chains_list[idx],'bone_chains',text='')

        if scn.my_chain_map_index > 0 :
            box = self.layout.box()
            row = box.row(align=True)

            row.label(text=scn.my_chain_map[scn.my_chain_map_index].source_chain)
            row.prop_search(scn.my_chain_map[scn.my_chain_map_index],'name',scn.my_target_bone_chains_list[scn.my_chain_map_index],'bone_chains',text='')
            row = box.row(align=True)
            row.prop(scn.my_chain_map[scn.my_chain_map_index],'is_root')

            # row.prop(scn.my_bones_map[scn.my_chain_map_index].source_bone)
            # row.prop(scn.my_bones_map[scn.my_chain_map_index].name)


classes = [ARP_UL_items,
           BonesMap,
           CopyRotation,
           ChainMap,
           ChainList,
           BuildList,
           autoSetChainOP,
           sortBoneChainsOP,
           OpPanel,
           myBone,
           boneList,
           BoneChains,
           BoneChainsList,
           myString,
           clearIgnoreBone,
           RemapPanel,
           BoneChainsPanel,
           SaveBoneChainsOP,
           BuildChains,
           enumAdd,
           EnumBoneCHain]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.enum_Add = bpy.props.CollectionProperty(type=enumAdd)
    bpy.types.Scene.my_sourceBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_source_chains = bpy.props.CollectionProperty(type=BoneChains)
    bpy.types.Scene.my_target_bone_chains_list = bpy.props.CollectionProperty(type=BoneChainsList)
    bpy.types.Scene.my_targetBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_target_chains = bpy.props.CollectionProperty(type=BoneChains)
    bpy.types.Scene.my_target_chainsRig = bpy.props.CollectionProperty(type=BoneChainsList)
    bpy.types.Scene.my_ignore_bone_name = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_enum_bone_chain = bpy.props.CollectionProperty(type=EnumBoneCHain)
    bpy.types.Scene.my_chain_map = bpy.props.CollectionProperty(type=ChainMap)
    bpy.types.Scene.my_bones_map = bpy.props.CollectionProperty(type=BonesMap)
    bpy.types.Scene.my_chain_map_index = bpy.props.IntProperty()
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
    del bpy.types.Scene.my_bones_map
    del bpy.types.Scene.my_chain_map_index

if __name__ == "__main__":
    register()