import math
from mathutils import *

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