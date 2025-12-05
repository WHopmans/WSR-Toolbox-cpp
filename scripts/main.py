'''
(c) REACT LAB, Harvard University
Author: Ninad Jadhav, Weiying Wang
'''

#!/usr/bin/env python

from libs import wsr_module
from pathlib import Path
import argparse
from os.path import expanduser

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Input data file")
    parser.add_argument("--d_type", help="Source of robot displacement: gt, t265, odom")
    args = parser.parse_args()
    
    REPO_ROOT = Path(__file__).resolve().parents[1]
    config_fn = str(REPO_ROOT / "config" / "config_3D_SAR.json")

    # #Make C++ function calls to calculate AOA profile
    wsr_obj = wsr_module.PyWSR_Module(config_fn, args.d_type)
    aoa = wsr_obj.AOA_profile()
    print(aoa)


if __name__ == "__main__":
    main()

