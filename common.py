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

def copy_edit_bone(origin_bone,new_bone):
    oeb = create_edit_bone(origin_bone)
    neb = create_edit_bone(new_bone)
    neb.head = oeb.head
    neb.tail = oeb.tail
    neb.matrix = oeb.matrix
    return neb

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
