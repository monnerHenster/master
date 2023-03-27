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
    items = []
    for item in bpy.context.scene.enum_Add.values():
        items.append((item.string,item.string,''))
    return items

class enumAdd(bpy.types.PropertyGroup):
    # @classmethod
    # def register(cls):
    #     bpy.types.Scene.enum_Add = bpy.props.CollectionProperty(type=enumAdd)

    # @classmethod
    # def unregister(cls):
    #     del bpy.types.Scene.enum_Add

    string : bpy.props.StringProperty()

#define what the property in the colection will look like

# bpy.context.scene.globalvalue = 3

class myBone(bpy.types.PropertyGroup):
    bone:bpy.props.PointerProperty(type=bpy.types.Action)


class boneList(bpy.types.PropertyGroup):
    # bone:bpy.props.CollectionProperty(type=bpy.types.PoseBone)
    name:bpy.props.StringProperty()

class myString(bpy.types.PropertyGroup):
    string:bpy.props.StringProperty()

class boneChains(bpy.types.PropertyGroup):
    isExtraBone:bpy.props.BoolProperty()
    name: bpy.props.StringProperty()
    boneChain:bpy.props.CollectionProperty(type=boneList)

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
        # retargetValue = retarget()
        # retargetValue.start()
        # sourceRigBoneChains = retargetValue.sourceArmature.boneChains
        # targetRigBoneChains = retargetValue.targetArmature.boneChains

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

        # scn.my_customeProperty.my_sourceRigBoneChains = sourceRigBoneChains

        # print(sourceRigBoneChains)

        setBoneChain(self,context,self.sourceArmature.boneChains,scn.my_sourceBoneChains)
        setBoneChain(self,context,self.targetArmature.boneChains,scn.my_targetBoneChains)

        # for boneChain in self.sourceArmature.boneChains:
        #     # print(boneChain)
        #     item = scn.my_sourceBoneChains.add()
        #     boneNames = ''
        #     for bone in boneChain:
        #         item_boneChain = item.boneChain.add()
        #         item_boneChain.name = bone.name
        #         boneNames += item_boneChain.name
        #     item.name = boneNames
        
        # newItems
        return {'FINISHED'}

class clearIgnoreBone(bpy.types.Operator):
    bl_idname = 'clear_ignore_bone.go'
    bl_label = 'clearIgnoreBone'

    def execute(self, context: 'Context'):
        scn = bpy.context.scene
        scn.my_ignore_bone_name.clear()
        return {'FINISHED'}

class SaveBoneChainsOP(bpy.types.Operator):
    bl_idname = 'savebonechains.go'
    bl_label = 'saveBoneChains'
    
    def execute(self, context):
        #add the param to the registered collection
        # print(idxNeedRmove)
        scn = bpy.context.scene

        item = scn.my_customeProperty.add()

        # for idx,item in enumerate(scn.my_customeProperty):
        #     attr = [a for a in dir(item)]
        #     for b in attr:
        #         print(b,getattr(item,b))

        for idx,boneChain in enumerate(scn.my_sourceBoneChains):
            if boneChain.isExtraBone == True:
                for idx,bone in enumerate(boneChain.boneChain):
                    item = scn.my_ignore_bone_name.add()
                    item.name = bone.name
                    # print(item.bone)
                    # print(dir(bone))
                    # print(type(bone))
                    # for i in bone:
                    #     print(i)
                    # item.bone = bone.bone
                    # print(item.item.bone)
                    break
                # boneChain.remove()
        for idx,bone in enumerate(scn.my_ignore_bone_name):
            print(bone.name,idx)
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

        obj = context.object

        row = layout.row()
        row.operator("hi.go")
        row.operator("savebonechains.go")
        row.operator("clear_ignore_bone.go")
        # row.label(text="Hello world!", icon='WORLD_DATA')
      
        #         #     print(b,getattr(input2,b))
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

        
        row = layout.row()

class HelloWorldPanel2(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Remap"
    bl_category = "AniTool"
    bl_idname = "HI_PT_Panel4"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context: 'Context'):
        pass

classes = [myBone,
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
           enumAdd]

def setBoneChain(self,context,boneChains,scnBoneChains):
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

if __name__ == "__main__":
    register()