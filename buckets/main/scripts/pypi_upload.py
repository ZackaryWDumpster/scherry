"""
pypi upload script
"""
import os
import sys
import shutil
from keyring.backends.Windows import WinVaultKeyring

if not os.path.exists("setup.py"):
    print("No setup.py found")
    sys.exit(1)

if os.path.exists(os.path.join(os.getcwd(), "presetup.py")):
    os.system("python presetup.py")

keyring = WinVaultKeyring()

# build if not exist
if not os.path.exists("dist"):
    os.system("python -m build")
# check
if not os.path.exists("dist"):
    print("No dist folder found, please run python setup.py sdist")
    sys.exit(1)

# check dist
os.system("twine check dist/*")

# upload
token = keyring.get_password("PYPI_TOKEN", "zackary")

if token is None:
    print("No PYPI_TOKEN found")
    sys.exit(1)

os.system(f"twine upload dist/* -u __token__ -p {token}")

# clean
shutil.rmtree("dist")

