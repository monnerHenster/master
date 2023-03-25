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

import bpy
import random

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
class scad_params(bpy.types.PropertyGroup):
    materialname: bpy.props.StringProperty(name="Material", default="")
    slot: bpy.props.IntProperty(name="Slot")
    checked: bpy.props.BoolProperty(name="")
    boneName: bpy.props.StringProperty(name='')

    # def getItem(self,context,newItems):
    #     items = [
    #         ('NONE', 'None', "Flat geometry"),
    #         ('GEOM', 'Geometry', "Use z value from shape geometry if exists"),
    #         ('FIELD', 'Field', "Extract z elevation value from an attribute field"),
    #         ('OBJ', 'Object', "Get z elevation value from an existing ground mesh")
    #     ]
    #     return items

    targetBoneChainsEnum: bpy.props.EnumProperty(items = getItem)

#operator, connected the button that adds the params
class HiOp(bpy.types.Operator):
    bl_idname = 'hi.go'
    bl_label = 'add a thing'
    slot: bpy.props.IntProperty()
    
    def execute(self, context):
        #add the param to the registered collection
        # context.scene.scad_params.add().slot = self.slot
        context.scene.scad_params.clear()
        context.scene.enum_Add.clear()
       
        # for idx
        i = 0
        while i < 6:
            item = context.scene.enum_Add.add()
            item.string = "dddd"+str(i)
            print(context.scene.enum_Add)
            # item.boneName = str(random.randint(1,100))
            # item.targetBoneChainsEnum =  enumerate([ddd])
        #     [
        #     ('NONE', 'None', "Flat geometry"),
        #     ('GEOM', 'Geometry', "Use z value from shape geometry if exists"),
        #     ('FIELD', 'Field', "Extract z elevation value from an attribute field"),
        #     ('OBJ', 'Object', "Get z elevation value from an existing ground mesh")
        # ]
            i += 1
        item = context.scene.scad_params.add()
        
        # context.scene.scad_params.add().checked
        # context.scene.scad_params.remove(0)

        # newItems
        return {'FINISHED'}

class TestOP(bpy.types.Operator):
    bl_idname = 'test.go'
    bl_label = 'test'
    
    def execute(self, context):
        #add the param to the registered collection
        # context.scene.scad_params.add().slot = self.slot
        idxNeedRmove = []

        for idx,item in enumerate(bpy.context.scene.scad_params):
            if item.checked:

                # print(item.boneName)
                # print(idx)
                idxNeedRmove.append(idx)
        i = 0
        for idx in idxNeedRmove:
            idx -= i
            bpy.context.scene.scad_params.remove(idx)
            i += 1
        print(idxNeedRmove)
        # context.scene.scad_params.add().checked
        # context.scene.scad_params.remove(0)
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
        for index, input in enumerate(context.scene.scad_params):
            row = layout.row()
            # row.prop(input,input.boneName)
            row.prop(input,"checked")
            # row.label(text="boneName")
            row.label(text=input.boneName)
            row.prop(input,"targetBoneChainsEnum",text='')
            # layout.prop(input,text=input.boneName)
            # layout.prop(text=input.boneName)
            # row.prop_search(input, "materialname",bpy.data, "materials")
            
            # attr = [a for a in dir(input) if not a.startswith('__')]
            # for i in attr:
            #     print(i,getattr(input,i))

        
        row = layout.row()
        row.operator("hi.go")
        row.operator("test.go")


def register():
    bpy.utils.register_class(HelloWorldPanel)
    bpy.utils.register_class(TestOP)
    bpy.utils.register_class(HiOp)
    bpy.utils.register_class(scad_params)
    bpy.utils.register_class(enumAdd)
    #register a collection of params so that the operator and panel can share them
    bpy.types.Scene.scad_params = bpy.props.CollectionProperty(type=scad_params)
    bpy.types.Scene.enum_Add = bpy.props.CollectionProperty(type=enumAdd)


def unregister():
    bpy.utils.unregister_class(HelloWorldPanel)
    bpy.utils.unregister_class(HiOp)
    bpy.utils.unregister_class(TestOP)
    bpy.utils.unregister_class(enumAdd)
    bpy.utils.unregister_class(scad_params)
    del bpy.types.Scene.scad_params
    del bpy.types.Scene.enum_Add

if __name__ == "__main__":
    register()