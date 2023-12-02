import bpy

def get_source_rig(self):
    scn = bpy.context.scene
    # print(self.get('in__source_rig',''))
    # print(bool(bpy.data.objects.get(self.get('in__source_rig',''))))
    # print(len(bpy.context.selected_objects) > 0)
    if (self.get('in__source_rig','') == '' or not bool(bpy.data.objects.get(self.get('in__source_rig','')))) and len(bpy.context.selected_objects) > 0:
        scn.source_rig = bpy.context.selected_objects[0].name
        return bpy.context.selected_objects[0].name
    else:
        return self.get('in__source_rig','')

def set_source_rig(self,value):
    scn = bpy.context.scene
    self['in__source_rig'] = value
    if value != '':
        scn.my_source_rig = bpy.data.objects[value]    

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

classes = [
    AN_PT_ArmatureSet
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.source_rig = bpy.props.StringProperty(get=get_source_rig,set=set_source_rig)
    bpy.types.Scene.my_source_rig = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.my_target_rig = bpy.props.PointerProperty(type=bpy.types.Object)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.source_rig
    del bpy.types.Scene.my_source_rig
    del bpy.types.Scene.my_target_rig