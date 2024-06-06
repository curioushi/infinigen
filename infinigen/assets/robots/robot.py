import bpy
import infinigen.core.util.blender as butil
from typing import List


class Action:
    def __init__(self):
        pass

    def execute(self):
        raise NotImplementedError


class ActionRemoveObjects(Action):
    def __init__(self, objs: List[bpy.types.Object]):
        self.objs = objs

    def execute(self):
        with butil.CollectionVisibility("GT World"):
            butil.delete(self.objs)

    def __repr__(self) -> str:
        return f"ActionRemoveObjects({[obj.name for obj in self.objs]})"


class Robot:
    def __init__(self):
        pass

    def perception(self):
        raise NotImplementedError

    def motion_planning(self) -> List[Action]:
        raise NotImplementedError

    def motion_execution(self, actions: List[Action]):
        raise NotImplementedError
