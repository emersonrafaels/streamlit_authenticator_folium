import os
from pathlib import Path

from dynaconf import Dynaconf

dir_root = Path(__file__).absolute().parent

list_files = [
    str(Path(dir_root, "settings.toml")),
    str(Path(dir_root, ".secrets.toml")),
]

settings = Dynaconf(
    settings_files=list_files,
    environments=True,
    env="development",
)
