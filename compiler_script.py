from venv_dependency_updater import dependency_updater
from zipfile import ZipFile
from shutil import rmtree, copytree

from os import walk
from os.path import join
import pathlib


def main():
    # dependency_updater()
    try:
        rmtree("./FicHub2Calibre")
    except FileNotFoundError:
        pass

    try:
        copytree("./dist-info", "./FicHub2Calibre/dist-info", dirs_exist_ok=True)
    except FileNotFoundError:
        pass

    try:
        copytree("./included-dependencies", "./FicHub2Calibre", dirs_exist_ok=True)
    except FileNotFoundError:
        pass

    try:
        copytree("./src", "./FicHub2Calibre", dirs_exist_ok=True)
    except FileNotFoundError:
        pass

    with ZipFile("FicHub2Calibre.zip", "w") as zipit:
        for root, directory, files in walk("./FicHub2Calibre"):
            short_root = pathlib.Path(*pathlib.Path(root).parts[2:])
            for file in files:
                zipit.write(join(root, file), arcname=join(short_root, file))


if __name__ == '__main__':
    main()
