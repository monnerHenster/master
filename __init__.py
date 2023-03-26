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


class boneChain(bpy.types.PropertyGroup):
    string:bpy.props.StringProperty()

class boneChains(bpy.types.PropertyGroup):
    boneChain:bpy.props.CollectionProperty(type=boneChain)

class boneChainsMap(bpy.types.PropertyGroup):
    checked: bpy.props.BoolProperty(name="")
    # boneChains: bpy.context.scene.my_boneChains
    boneChains: bpy.props.CollectionProperty(type=boneChains)
    targetBoneChainsEnum: bpy.props.EnumProperty(items = getItem)

#operator, connected the button that adds the params
class HiOp(bpy.types.Operator):
    bl_idname = 'hi.go'
    bl_label = 'show bonechains'
    slot: bpy.props.IntProperty()
    
    def execute(self, context):
        bpy.context.scene.my_boneChainsMap.clear()
        item = bpy.context.scene.my_boneChainsMap.add()
        # item.boneChains = bpy.context.scene.my_boneChains.add()
        # item.boneChains.boneChain = bpy.context.scene.my_boneChain.add()
        # item.boneChains.boneChain.string = 'boneName'


        #add the param to the registered collection
        # context.scene.boneChainsMap.add().slot = self.slot
        # i = 0
        # while i < 6:
        #     item = context.scene.enum_Add.add()
        #     item.string = "dddd"+str(i)
        #     # print(context.scene.enum_Add)
        #     # item.boneName = str(random.randint(1,100))
        #     # item.targetBoneChainsEnum =  enumerate([ddd])
        # #     [
        # #     ('NONE', 'None', "Flat geometry"),
        # #     ('GEOM', 'Geometry', "Use z value from shape geometry if exists"),
        # #     ('FIELD', 'Field', "Extract z elevation value from an attribute field"),
        # #     ('OBJ', 'Object', "Get z elevation value from an existing ground mesh")
        # # ]
        #     i += 1
        # item = context.scene.boneChainsMap.add()
        # item.boneName = "aaaa"
        # context.scene.boneChainsMap.add().checked
        # context.scene.boneChainsMap.remove(0)

        # newItems
        return {'FINISHED'}

class TestOP(bpy.types.Operator):
    bl_idname = 'test.go'
    bl_label = 'test'
    
    def execute(self, context):
        #add the param to the registered collection
        # context.scene.boneChainsMap.add().slot = self.slot
        # idxNeedRmove = []

        # for idx,item in enumerate(bpy.context.scene.boneChainsMap):
        #     if item.checked:

        #         # print(item.boneName)
        #         # print(idx)
        #         idxNeedRmove.append(idx)
        # i = 0
        # for idx in idxNeedRmove:
        #     idx -= i
        #     bpy.context.scene.boneChainsMap.remove(idx)
        #     i += 1
        # print(idxNeedRmove)

        # for item in enumerate(context.scene.boneChainsMap):
        #     attr = [a for a in dir(item) if  not a.startswith('__')]
        #     for str in attr:
        #         print(str,getattr(item,str))
        #         attr2 = [b for b in dir(str) if  not b.startswith('__')]
        #         for str2 in attr2:
        #             print(str2,getattr(str,str2))


        #     break
        # for idx,item in enumerate(context.scene.boneChainsMap):
        #     print(item.boneName)
        #     print(item.targetBoneChainsEnum)
        #     attr = [a for a in dir(item) if  not a.startswith('__')]
        #     for str in attr:
        #         print(str,getattr(item,str))

        for idx,item in enumerate(bpy.context.scene.globalvalue):
            pass
            print(item.string)
        # context.scene.boneChainsMap.add().checked
        # context.scene.boneChainsMap.remove(0)
        return {'FINISHED'}        

class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "HI"
    bl_category = "HI"
    bl_idname = "HI_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')
        # item = context.scene.enum_ 
        #use the registered collection shared with the operator to built the rest of the panel
        for index, input in enumerate(context.scene.my_boneChainsMap):
            row = layout.row()
            # row.prop(input,input.boneName)
            row.prop(input,"boneChains")
            # row.prop(input,"checked")
            # row.label(text="boneName")
            # row.label(text=input.boneName)
            # row.prop(input,"targetBoneChainsEnum",text='')
            # layout.prop(input,text=input.boneName)
            # layout.prop(text=input.boneName)
            # row.prop_search(input, "materialname",bpy.data, "materials")
            
            # attr = [a for a in dir(input) if not a.startswith('__')]
            # for i in attr:
            #     print(i,getattr(input,i))

        
        row = layout.row()
        row.operator("hi.go")
        row.operator("test.go")

classes = [boneChain,boneChains,boneChainsMap]

def register():
    bpy.utils.register_class(HelloWorldPanel)
    bpy.utils.register_class(TestOP)
    bpy.utils.register_class(HiOp)
    # bpy.utils.register_class(boneChainsMap)
    bpy.utils.register_class(enumAdd)
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.utils.register_class(boneChain)
    # bpy.utils.register_class(boneChains)
    #register a collection of params so that the operator and panel can share them
    # bpy.types.Scene.boneChainsMap = bpy.props.CollectionProperty(type=boneChainsMap)
    bpy.types.Scene.enum_Add = bpy.props.CollectionProperty(type=enumAdd)
    bpy.types.Scene.my_boneChains = bpy.props.CollectionProperty(type=boneChains)
    # bpy.types.Scene.my_boneChains = bpy.props.CollectionProperty(type=boneChains)
    bpy.types.Scene.my_boneChainsMap = bpy.props.CollectionProperty(type=boneChainsMap)



def unregister():
    bpy.utils.unregister_class(HelloWorldPanel)
    bpy.utils.unregister_class(HiOp)
    bpy.utils.unregister_class(TestOP)
    bpy.utils.unregister_class(enumAdd)
    # bpy.utils.unregister_class(boneChainsMap)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # bpy.utils.unregister_class(myString)
    # bpy.utils.unregister_class(myString)
    # del bpy.types.Scene.boneChainsMap
    del bpy.types.Scene.enum_Add
    del bpy.types.Scene.my_boneChains
    del bpy.types.Scene.my_boneChainsMap

if __name__ == "__main__":
    register()