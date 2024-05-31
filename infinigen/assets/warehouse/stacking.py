import bpy
from typing import List
import numpy as np
from infinigen.assets.warehouse.stacking_base import SKU, SKUGenerator, StackingFactory
import infinigen.assets.utils.decorate as decorate
import infinigen.core.util.blender as butil


class SingleSKUGenerator(SKUGenerator):
    def __init__(self, sku: SKU, num=None, seed=None):
        super().__init__(seed)
        self.sku = sku
        self.num = num
        self.buffer.append(sku)
        if self.num is not None:
            self.num -= 1

    def populate(self):
        if self.num is None:
            self.buffer.append(self.sku)
        elif self.num > 0:
            self.buffer.append(self.sku)
            self.num -= 1


class SingleSKUStackingFactory(StackingFactory):
    def __init__(self, seed=None):
        super().__init__(seed)

    def create_boxes(
        self, space_dim, sku_generator: SKUGenerator
    ) -> List[bpy.types.Object]:
        space_dim = np.array(space_dim)
        sku = sku_generator.buffer.draw_first()
        sku_dim = np.array(sku.dimensions)
        half_dim = sku_dim / 2
        num_boxes = (space_dim // sku_dim).astype(int)
        boxes = []
        for i in range(num_boxes[0]):
            for j in range(num_boxes[1]):
                for k in range(num_boxes[2]):
                    cube = butil.spawn_cube(size=1)
                    decorate.transform(
                        cube,
                        translation=(
                            i * sku_dim[0] + half_dim[0],
                            j * sku_dim[1] + half_dim[1],
                            k * sku_dim[2] + half_dim[2],
                        ),
                        scale=sku_dim,
                    )
                    boxes.append(cube)
        return boxes
