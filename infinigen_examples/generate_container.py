import infinigen.core.util.blender as butil
from infinigen.assets.warehouse.container import ContainerFactory
from infinigen.tools.export import run_export
from pathlib import Path

root = Path(__file__).parent.parent
output_dir = root / "output/container"

butil.clear_scene()
factory = ContainerFactory()
container = factory.create_asset()

run_export(output_dir / "container.stl", "stl", False, False)
