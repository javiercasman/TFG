import subprocess
import sys

path = sys.executable
subprocess.call([path, "-m", "ensurepip"])

modules = ["scikit-image", "opencv-python", "plantcv", "colour-science"]

for module in modules:
    subprocess.call([path, "-m", "pip", "install", module])