import shutil
from pathlib import Path
from sphinx.cmd import build

source_path = Path(__file__).parent
build_path = source_path.parent / "build"
try:
    shutil.rmtree(build_path)
except FileNotFoundError:
    pass
build.build_main([str(source_path), str(build_path)])
