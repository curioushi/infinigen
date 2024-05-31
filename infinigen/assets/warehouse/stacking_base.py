import bpy
from typing import List, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class SKU:
    dimensions: Tuple[float, float, float]


class SKUBuffer(list[SKU]):
    def __init__(self, generator):
        self.generator: SKUGenerator = generator

    def draw(self, index) -> SKU:
        sku = self.pop(index)
        self.generator.populate()
        return sku

    def draw_first(self) -> SKU:
        return self.draw(0)

    def __repr__(self) -> str:
        return f"{super().__repr__()}"

    def __str__(self) -> str:
        return f"{super().__str__()}"


class SKUGenerator:
    def __init__(self, seed=None):
        self.seed = seed
        if self.seed is None:
            self.seed = np.random.randint(1e9)

        self.buffer: SKUBuffer = SKUBuffer(self)

    def populate(self):
        # Override this function to populate the buffer with SKUs
        raise NotImplementedError

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.buffer) == 0:
            raise StopIteration
        else:
            return self.buffer


class StackingFactory:

    def __init__(self, seed=None):
        self.seed = seed
        if self.seed is None:
            self.seed = np.random.randint(1e9)

    def create_boxes(
        self, space_dim, sku_generator: SKUGenerator
    ) -> List[bpy.types.Object]:
        raise NotImplementedError
