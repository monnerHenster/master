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



def getItem(self,context):
    # items = (
    #     ("humanoid", "Humanoid", "Humanoid rig type, simple bones hierarchy to ensure animation retargetting"),
    #     ("mped", "Universal", "Universal rig type, simple bones hierarchy for any creature (dog, spider...)")
    #     )
    items = []
    for item in bpy.context.scene.my_targetBoneChains.values():
        Bones = ''
        Bones += item.IsSelected
        for bone in item.boneChain.values():
            Bones += bone.name
        items.append((Bones,Bones,''))
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

class boneChains(bpy.types.PropertyGroup):
    isExtraBone:bpy.props.BoolProperty()
    IsSelected:bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    boneChain:bpy.props.CollectionProperty(type=boneList)
    boneChainString:bpy.props.StringProperty()
    index:bpy.props.IntProperty()

class boneChainsMap(bpy.types.PropertyGroup):
    # checked: bpy.props.BoolProperty(name="")
    # boneChains: bpy.props.StringProperty()
    boneChains: bpy.props.CollectionProperty(type=boneChains)
    # boneChains: bpy.context.scene.my_sourceBoneChains
    targetBoneChainsEnum: bpy.props.EnumProperty(items = getItem)

class customeProerty(bpy.types.PropertyGroup):
    pass

#operator, connected the button that adds the params
class HiOp(bpy.types.Operator):
    bl_idname = 'hi.go'
    bl_label = 'showBonechains'
    slot: bpy.props.IntProperty()
    
    def execute(self, context):
        scn = bpy.context.scene
        scn.my_sourceBoneChains.clear()

        source_rig = bpy.data.objects['root.001']
        target_rig = bpy.data.objects['Armature.001']

        # boneIgnoreName = ['thigh_twist_01_l','calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        boneIgnoreName = ['calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        
        for idx,bone in enumerate(scn.my_ignore_bone_name):
            boneIgnoreName.append(str(bone.name))
        self.sourceArmature = ArmatureBoneInfo(source_rig)
        self.targetArmature = ArmatureBoneInfo(target_rig)
        # a.boneIgnoreName.append('thigh_twist_01_l')
        self.sourceArmature.boneIgnoreName += boneIgnoreName
        self.targetArmature.boneIgnoreName += boneIgnoreName

        setBoneChain(self,context,self.sourceArmature.boneChains,scn.my_sourceBoneChains)
        setBoneChain(self,context,self.targetArmature.boneChains,scn.my_targetBoneChains)

        sortBoneChains(self,context,scn.my_sourceBoneChains)
        sortBoneChains(self,context,scn.my_targetBoneChains)

        scn.my_enum_bone_chain.clear()
        for item in scn.my_sourceBoneChains.values():
            scn.my_enum_bone_chain.add()
        
        # newItems
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
        freeChain = [ a.name for a in scn.my_targetBoneChains]

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
        # map(lambda i: scn.my_targetBoneChains.remove(scn.my_targetBoneChains.find(i)),FixChain)
        for item in FixChain:
            idx = scn.my_targetBoneChains.find(item)
            scn.my_targetBoneChains[idx].IsSelected = 'Selected____'
        # scn.my_enum_bone_chain[0].BoneChain = '22'
        # print(scn.my_enum_bone_chain[0].BoneChain)
        for a in scn.my_targetBoneChains:
            print(a )
        return {'FINISHED'}

class CopyRotationOP(bpy.types.Operator):
    bl_idname = 'copy_rotation.go'
    bl_label = 'CopyRotationOP'

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        for idx,BoneChain in enumerate(scn.my_sourceBoneChains):
            for idx2,Bone in enumerate(BoneChain.boneChain):
                # print(Bone.name)
                # print(idx2)
                print(scn.my_enum_bone_chain[idx].BoneChain)
                # print(scn.my_targetBoneChains[idx])
        return {'FINISHED'}

def sortBoneChains(self,context,scnList):
    newSortList = []
    for boneChain in scnList.values():
        boneList = []
        for bone in boneChain.boneChain.values():

            boneList.append(bone.name)
        newSortList.append(boneList)
    newSortList.sort()

    scnList.clear()

    for boneChain in newSortList:
        item = scnList.add()
        chainName = ''
        for bone in boneChain:
            item2 = item.boneChain.add()
            item2.name = bone
            chainName += bone
        item.name = chainName




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

        for idx,boneChain in enumerate(scn.my_sourceBoneChains):
            if boneChain.isExtraBone == True:
                for idx,bone in enumerate(boneChain.boneChain):
                    item = scn.my_ignore_bone_name.add()
                    item.name = bone.name

                    break
                # boneChain.remove()
        for idx,bone in enumerate(scn.my_ignore_bone_name):
            pass
            # print(bone.name,idx)
        # print
      

        # context.scene.boneChainsMap.remove(0)
        return {'FINISHED'}        

class HelloWorldPanel(bpy.types.Panel):
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

        drawBoneChains(self,context,scn.my_sourceBoneChains)
        # for idx,item in enumerate(scn.my_sourceBoneChains):
        #     row = layout.row(align=False)
        #     row.alignment = 'LEFT'
        #     row.prop(item,'isExtraBone')
        #     row.label(text=item.name)
        #     row.split(align=True,factor=0.3)
 
            #     print(i,getattr(input,i))
        layout.label(text='targetBoneChains')
        drawBoneChains(self,context,scn.my_targetBoneChains)

class HelloWorldPanel2(bpy.types.Panel):
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
        for item in scn.my_sourceBoneChains:
            row = column.row()
            row.label(text=item.name)

        split = split.split(factor=1)
        column = split.column()
        column.label(text = 'TargetChain')
        for idx,item in enumerate(scn.my_sourceBoneChains):
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
        row.operator("hi.go")
        row.operator("savebonechains.go")
        row.operator("clear_ignore_bone.go")
        row = self.layout.row()
        row.operator("auto_set_chain.go")
        row.operator("copy_rotation.go")

classes = [CopyRotationOP,
           autoSetChainOP,
           sortBoneChainsOP,
           OpPanel,
           myBone,
           boneList,
           boneChains,
           boneChainsMap,
           customeProerty,
           myString,
           clearIgnoreBone,
           HelloWorldPanel2,
           HelloWorldPanel,
           SaveBoneChainsOP,
           HiOp,
           enumAdd,
           EnumBoneCHain]

def setBoneChain(self,context,boneChains,scnBoneChains):
        scnBoneChains.clear()
        scn = bpy.context.scene
        for boneChain in boneChains:
            # print(boneChain)
            item = scnBoneChains.add()
            boneNames = ''
            for bone in boneChain:
                item_boneChain = item.boneChain.add()
                item_boneChain.name = bone.name
                boneNames += item_boneChain.name
            item.name = boneNames

def drawBoneChains(self,context,boneChains):
        # scn = bpy.context.scene
        layout = self.layout
        for idx,item in enumerate(boneChains):
            row = layout.row(align=False)
            row.alignment = 'LEFT'
            row.prop(item,'isExtraBone')
            row.label(text=item.name)
            row.split(align=True,factor=0.3)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.enum_Add = bpy.props.CollectionProperty(type=enumAdd)
    bpy.types.Scene.my_sourceBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_sourceBoneChains = bpy.props.CollectionProperty(type=boneChains)
    bpy.types.Scene.my_sourceBoneChainsMap = bpy.props.CollectionProperty(type=boneChainsMap)
    bpy.types.Scene.my_targetBoneChain = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_targetBoneChains = bpy.props.CollectionProperty(type=boneChains)
    bpy.types.Scene.my_targetBoneChainsMap = bpy.props.CollectionProperty(type=boneChainsMap)
    bpy.types.Scene.my_ignore_bone_name = bpy.props.CollectionProperty(type=boneList)
    bpy.types.Scene.my_enum_bone_chain = bpy.props.CollectionProperty(type=EnumBoneCHain)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.enum_Add
    del bpy.types.Scene.my_sourceBoneChains
    del bpy.types.Scene.my_sourceBoneChainsMap
    del bpy.types.Scene.my_sourceBoneChain
    del bpy.types.Scene.my_targetBoneChains
    del bpy.types.Scene.my_targetBoneChainsMap
    del bpy.types.Scene.my_targetBoneChain
    del bpy.types.Scene.my_ignore_bone_name
    del bpy.types.Scene.my_enum_bone_chain

if __name__ == "__main__":
    register()