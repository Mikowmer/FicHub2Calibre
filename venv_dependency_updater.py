"""
    Utility Script that uses Virtualenv's package management to include the appropriate dependencies and generate a
    requirements.txt file.
"""
# import warnings
import re

from os import listdir
from os.path import isdir, join, normpath

from shutil import rmtree, copytree

package_dst = 'included-dependencies'
dist_info_dst = 'dist-info'
venv_site_packages_loc = "venv/Lib/site-packages"
package_exclusions = frozenset(['pip', 'pkg_resources', 'setuptools', 'wheel'])

try:
    from pip._internal.operations import freeze
except ImportError:
    from pip.operations import freeze


def dependency_updater():
    print("Removing old dependencies...", end="", flush=True)
    try:
        rmtree(package_dst)
        print("\tOld dependencies removed.")
    except FileNotFoundError:
        print("\tNo old dependencies to remove.")

    print("Removing old dist-info...", end="", flush=True)
    try:
        rmtree(dist_info_dst)
        print("\t\tOld dist-info removed.")
    except FileNotFoundError:
        print("\t\tNo old dist-info to remove.")

    pkgs = list(freeze.freeze())

    packages_to_transfer = [d for d in listdir(venv_site_packages_loc) if isdir(join(venv_site_packages_loc, d))
                            and d[0] != '_' and d[-10:] != '.dist-info' and all(
        pkg_loop != d for pkg_loop in package_exclusions)]

    regex = r"^(.+)==(.+)$"
    subst = "\\g<1>-\\g<2>.dist-info"

    dist_info_to_transfer = [
        pkg for pkg in pkgs if not re.match(r"^(pip|setuptools|wheel)(==)(.+)$", pkg, re.MULTILINE)
    ]

    with open("requirements.txt", "w") as f:
        for pkg in dist_info_to_transfer:
            f.write(pkg + "\n")

    dist_info_to_transfer = [
        re.sub(regex, subst, pkg.replace('-', '_'), 0, re.MULTILINE) for pkg in dist_info_to_transfer
    ]

    # The following code would be useful if typing-extensions had a folder for itself.
    # if len(packages_to_transfer) != len(dist_info_to_transfer):
    #     warnings.warn(
    #         "Number of dist-info directories does not match number of package directories. Please manually verify."
    #     )

    print("Transferring Packages:")

    for package_dir in packages_to_transfer:
        print(".", end="", flush=True)
        src_dir = normpath(join(venv_site_packages_loc, package_dir))
        dst_dir = normpath(join(package_dst, package_dir))

        copytree(src_dir, dst_dir)

    print("\nTransferring dist-info:")

    for dist_info_dir in dist_info_to_transfer:
        print(".", end="", flush=True)
        src_dir = normpath(join(venv_site_packages_loc, dist_info_dir))
        dst_dir = normpath(join(dist_info_dst, dist_info_dir))

        copytree(src_dir, dst_dir)


if __name__ == '__main__':
    dependency_updater()
