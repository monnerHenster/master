import bpy
import numpy
from mathutils import *

def dict_subtract(origin_dict:list,target_dict:list):
    temp_origin_dict = origin_dict
    for dict1 in origin_dict:
        for dict2 in target_dict:
            if dict1 == dict2:
                temp_origin_dict.remove(dict1)
    return temp_origin_dict

class boneIndex():
    def __init__(self) -> None:
        self.bone:bpy.types.PoseBone
        self.index:int

class ArmatureBoneInfo():
    def __init__(self,armature:bpy.types.Object) -> None:
        self.bone_chains = []
        self.armature = armature
        # self.rootBones:list[bpy.types.PoseBone]=[]
        self.rootBones:dict[str:int,str:bpy.types.PoseBone] = []
        self._boneIgnoreName:list[str] = []
        self.boneIgnore:list[bpy.types.PoseBone] = []
        self.findRootBones()
        self.findBoneChains()
    
    @property
    def boneIgnoreName(self):
        return self._boneIgnoreName
    
    @boneIgnoreName.setter
    def boneIgnoreName(self,boneIgnoreName:list[str]):
        self._boneIgnoreName = boneIgnoreName
        for boneName in boneIgnoreName:
            if boneName in  self.armature.pose.bones:
                self.boneIgnore.append(self.armature.pose.bones[boneName])
        self.bone_chains = []
        self.findBoneChains()
    # @boneIgnoreName.setter
    # def boneIgnoreName

    def initBoneList(Armature:bpy.types.Object):
        for orginBone in Armature.pose.bones:
            if not hasattr(orginBone.parent):
                newBone = boneIndex(newBone)
                newBone.index = 0

                
                newBone.index = 0
                newBone.bone = orginBone
        boneList = []
        return boneList
    
    @staticmethod
    def check_helper_bones(bone):
        helper_bones_name = ['_REMAPTWEAK','_ROOT_OFFSET','_ROOT','_REMAP']
        for helper_bone in helper_bones_name:
            if hasattr(bone,'name'):
                if bone.name.endswith(helper_bone):
                    return True
            else:
                if bone.endswith(helper_bone):
                    return True
        return False

    def findRootBones(self):
        self.rootBones = []
        for orginBone in self.armature.pose.bones:
            if not orginBone.parent:
                self.rootBones.append(orginBone)

    bone_chain = [boneIndex] 
    bone_chains = []

    def get_root_bones(self,bones):
        root_bones = []
        for bone in bones:
            if bone in self.boneIgnoreName:
                for bone2 in self.get_root_bones(bone.children):
                    root_bones.append(bone2)
            else:
                root_bones.append(bone)
        return root_bones


    def get_bone_children(self,bone):
        
        bone_list = []
        for child in bone.children:
            if child.name in self.boneIgnoreName:
                if self.get_bone_children(child):
                    bone_list.append(self.get_bone_children(child))
            else:
                bone_list.append(child)
        return bone_list

    def findBoneChain(self,chain_layer,bone:bpy.types.PoseBone):
        bone_chain = []
        # bone_chain.append(bone)#将传进的骨头作为链的第一个

        #当下游骨头只有一个合法骨头的时候则添加进去，否则结束
        temp_bone = []
        temp_bone.append(bone)
        # print(temp_bone)


        while True:
            bone_chain.append(temp_bone[0])#将传进的骨头作为链的第一个
            # print(temp_bone[0])
            # if temp_bone[0].name == 'head':
            #     i = 1
            temp_bone = self.get_bone_children(temp_bone[0])
            if len(temp_bone) == 1:#如果只有一个常规子骨头
                continue

            else:
                break
        
        self.bone_chains.append({'index':chain_layer,'chain': bone_chain})
        if not temp_bone:
            return
        else:
            return [{'index':chain_layer+1,"chain":bone} for bone in temp_bone]
        
    def findBoneChains(self):
        self.findRootBones()

        chain_layer = 0
        boneChildren = self.rootBones

        boneChildren = list(set(self.rootBones)-set(self.boneIgnore))
        bone_tracking = []
        for bone in boneChildren:
            bone_tracking.append({"index":chain_layer,"chain":bone})
        boneFinish = []
        bone_chainBraches = []
        while  bone_tracking:
            bone = bone_tracking[0]
          
            bone_chainBraches = self.findBoneChain(bone['index'],bone['chain'])
            boneFinish.append(bone)
            if bone_chainBraches:
                bone_tracking += bone_chainBraches
            bone_chainBraches = []
            new_bone_tracking = bone_tracking
            for dict1 in bone_tracking:
                for dict2 in boneFinish:
                    if dict1 == dict2:
                        new_bone_tracking.remove(dict1)

            bone_tracking = new_bone_tracking
            boneFinish = []

class mapBoneChain():
    def __init__(self,sourceChain,targetChain) -> None:
        self.sourceChain = sourceChain
        self.targetChain = targetChain

class mapBoneChains():
    def __init__(self,sourceBoneInfo:ArmatureBoneInfo,targetBoneInfo:ArmatureBoneInfo) -> None:
        self.sourceBoneInfo = sourceBoneInfo
        self.targetBoneInfo = targetBoneInfo

        self.mapchains:list[mapBoneChain]
        self.map()

    def map(self):
        for chain in self.targetBoneInfo.bone_chains:
            bone_chain = mapBoneChain(chain,self.sourceBoneInfo.bone_chains[self.chooseChain()])
            self.mapchains.append(bone_chain)

    def chooseChain(self):
        i = 0
        for chain in self.sourceBoneInfo.bone_chains:
            print(i,' ',chain)
        userChoose = input()
        return userChoose




class retarget(object):
    def __init__(self) -> None:
        pass

    ddd = 1
    
    def start(self):
        source_rig = bpy.data.objects['root']
        target_rig = bpy.data.objects['Armature']

        boneIgnoreName = ['thigh_twist_01_l','calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        # boneIgnoreName = ['calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']

        self.sourceArmature = ArmatureBoneInfo(source_rig)
        self.targetArmature = ArmatureBoneInfo(target_rig)
        # a.boneIgnoreName.append('thigh_twist_01_l')
        self.sourceArmature.boneIgnoreName += boneIgnoreName
        self.targetArmature.boneIgnoreName += boneIgnoreName
        # a.findBoneChains()

        # mapChains = mapBoneChains(sourceArmature,targetArmature)
        print('test')
        print(self.sourceArmature.bone_chains)


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

    # print(a.bone_chains)

def main():
    a = retarget()
    a.start()
# main()