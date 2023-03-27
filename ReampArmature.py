import bpy
import numpy
from mathutils import *


class boneIndex():
    def __init__(self) -> None:
        self.bone:bpy.types.PoseBone
        self.index:int

class ArmatureBoneInfo():
    def __init__(self,armature:bpy.types.Object) -> None:
        self.boneChains = []
        self.armature = armature
        self.rootBones:list[bpy.types.PoseBone]=[]
        self.findRootBones()
        self._boneIgnoreName:list[str] = []
        self.boneIgnore:list[bpy.types.PoseBone] = []
        self.findBoneChains()
        # print(self.rootBones[0].bone.child)
        # print(self.rootBones[0].bone.children)
        # self.findBoneChain(self.rootBones[0].bone)
    
    @property
    def boneIgnoreName(self):
        return self._boneIgnoreName
    
    @boneIgnoreName.setter
    def boneIgnoreName(self,boneIgnoreName:list[str]):
        self._boneIgnoreName = boneIgnoreName
        for boneName in boneIgnoreName:
            if boneName in  self.armature.pose.bones:
                self.boneIgnore.append(self.armature.pose.bones[boneName])
        self.boneChains = []
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

    def findRootBones(self):
        # self.rootBones = [boneIndex]
        for orginBone in self.armature.pose.bones:
            if not orginBone.parent:
                # newBone = []
                # newBone = boneIndex()
                # newBone.bone = orginBone
                # newBone.index = 0
                self.rootBones.append(orginBone)

    boneChain = [boneIndex] 
    boneChains = []

    def findBoneChain(self,bone:bpy.types.PoseBone):
        boneChain = []
        boneChain.append(bone)#将传进的骨头作为链的第一个
        # print(bone)
        rBones:list[bpy.types.PoseBone] = bone.children
        rBoneNeedRevmoe = []
        #当下游骨头只有一个合法骨头的时候则添加进去，否则结束
        while len(rBones):
            for rbone in rBones:
                rbone:bpy.types.PoseBone
                if rbone.name == 'thigh_twist_01_l':
                    pass
                if rbone.name in self.boneIgnoreName:
                    rBoneNeedRevmoe.append(rbone)
            rBones = list(set(rBones)-set(rBoneNeedRevmoe))#真实的常规骨头
            if len(rBones) == 1:#如果只有一个常规子骨头
                boneChain.append(rBones[0])
            # bone = rBones[0]
                rBones = rBones[0].children
            else:
                break
        self.boneChains.append(boneChain)
        
        return rBones

    def findBoneChains(self):
        safety = 0
        # boneChildren = self.rootBones
        boneChildren = list(set(self.rootBones)-set(self.boneIgnore))
        boneFinish = []
        boneChainBraches = []
        while safety <= 999 and boneChildren:
            for bone in boneChildren:
                # if bone.name == 'Neck':
                #     pass
                boneChainBraches = self.findBoneChain(bone)
                boneFinish.append(bone)
                if boneChainBraches:
                    break
            boneChildren += boneChainBraches
            boneChainBraches = []
            boneChildren = list(set(boneChildren) - set(boneFinish))
            boneFinish = []
            safety += 1

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
        for chain in self.targetBoneInfo.boneChains:
            boneChain = mapBoneChain(chain,self.sourceBoneInfo.boneChains[self.chooseChain()])
            self.mapchains.append(boneChain)

    def chooseChain(self):
        i = 0
        for chain in self.sourceBoneInfo.boneChains:
            print(i,' ',chain)
        userChoose = input()
        return userChoose




class retarget(object):
    def __init__(self) -> None:
        pass

    ddd = 1
    
    def start(self):
        source_rig = bpy.data.objects['root.001']
        target_rig = bpy.data.objects['Armature.001']

        # boneIgnoreName = ['thigh_twist_01_l','calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']
        boneIgnoreName = ['calf_twist_01_r','calf_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r','lowerarm_twist_01_l','lowerarm_twist_01_r','ik_hand_root','ik_hand_r','ik_foot_root','ik_foot_r','ik_foot_l']

        self.sourceArmature = ArmatureBoneInfo(source_rig)
        self.targetArmature = ArmatureBoneInfo(target_rig)
        # a.boneIgnoreName.append('thigh_twist_01_l')
        self.sourceArmature.boneIgnoreName += boneIgnoreName
        self.targetArmature.boneIgnoreName += boneIgnoreName
        # a.findBoneChains()

        # mapChains = mapBoneChains(sourceArmature,targetArmature)
        print('test')


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

    # print(a.boneChains)
# main()
# print(a.rootBones)

# print(type(source_rig))

# for bone in source_rig.pose.bones:
#     print (type(bone))
#     print(bone.children)
#     break

# print('test')

# for bone in target_rig.pose.bones:
#     # for cst in bone.constraints:
#     #     print(cst.name)
#     #     # bpy.ops.constraint.apply(constraint=cst.name)
#     cst = bone.constraints.new('COPY_ROTATION')
#     cst.target = source_rig
#     cst.subtarget = bone.name