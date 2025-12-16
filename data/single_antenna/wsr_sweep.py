#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
import os

# --- CONFIGURE THESE -------------------------------------------------

# All datasets you want to run
DATASETS = [
    "data_10cm_1",
    "data_10cm_2",
    "data_10cm_3",
    "data_30cm_1",
    "data_30cm_2",
    "data_30cm_3",
    "data_50cm_1",
    "data_50cm_2",
    "data_70cm_1",
    "data_70cm_2",
    "data_80cm_1",
    "data_90cm_1",
    "data_forward_1",
    "data_forward_2",
    "data_forward_3",
    "data_right_1",
    "data_right_2",
    "data_right_3",
]

# Where centralized data lives
DATA_ROOT = Path("/home/wardhop/thesis/wsr_data/single_antenna")

# Repo and binary
REPO_ROOT = Path("/home/wardhop/thesis/GitHub/WSR-Toolbox-cpp")
BINARY = REPO_ROOT / "build" / "wsr_module"      # adapt name if different

# Base config (for any one dataset, e.g. your current 10cm_1 config)
BASE_CONFIG = REPO_ROOT / "config" / "config_3D_SAR.json"

# Names for subfolders in each dataset folder
DEBUG_DIR_NAME = "debug_wsr"
OUTPUT_DIR_NAME = "output_wsr"

# ---------------------------------------------------------------------


def make_config_for_dataset(dataset: str) -> Path:
    """
    dataset: e.g. 'data_10cm_1'
    """
    suffix = dataset.replace("data_", "")   # '10cm_1'
    folder = DATA_ROOT / dataset

    csi_rx = folder / f"csi_rx_{suffix}.dat"
    csi_tx = folder / f"csi_tx_{suffix}.dat"
    traj   = folder / f"rx_movement_{suffix}.csv"

    out_dir = folder / OUTPUT_DIR_NAME
    dbg_dir = folder / DEBUG_DIR_NAME

    # Make sure output/debug dirs exist
    out_dir.mkdir(parents=True, exist_ok=True)
    dbg_dir.mkdir(parents=True, exist_ok=True)

    # Sanity check: data files exist
    for p in [csi_rx, csi_tx, traj]:
        if not p.exists():
            raise FileNotFoundError(f"Expected file not found for {dataset}: {p}")

    with BASE_CONFIG.open() as f:
        cfg = json.load(f)

    # ---- Update all dataset-dependent bits ----

    # TX CSI path
    # cfg["input_TX_channel_csi_fn"]["value"]["tx1"]["csi_fn"] exists in your snippet
    cfg["input_TX_channel_csi_fn"]["value"]["tx1"]["csi_fn"] = str(csi_tx)

    # RX CSI path
    # cfg["input_RX_channel_csi_fn"]["value"]["csi_fn"] exists in your snippet
    cfg["input_RX_channel_csi_fn"]["value"]["csi_fn"] = str(csi_rx)

    # Displacement / trajectory CSVs
    for key in [
        "input_displacement_csv_fn_rx",
        "input_trajectory_csv_fn_rx",
        "input_trajectory_csv_fn_gt",
    ]:
        if key in cfg:
            cfg[key]["value"] = str(traj)

    # Make sure trajectory type is correct
    if "trajectory_type" in cfg:
        cfg["trajectory_type"]["value"] = "gt"

    # Output and debug dirs (keep trailing slash like your config)
    if "output_aoa_profile_path" in cfg:
        cfg["output_aoa_profile_path"]["value"] = str(out_dir) + "/"

    if "debug_dir" in cfg:
        cfg["debug_dir"]["value"] = str(dbg_dir) + "/"

    # If you ever want per-dataset packet limits or other tweaks, do them here

    # Write out a dataset-specific config
    out_cfg = DATA_ROOT / f"config_{suffix}.json"
    with out_cfg.open("w") as f:
        json.dump(cfg, f, indent=4)

    return out_cfg


def run_dataset(dataset: str):
    cfg_path = make_config_for_dataset(dataset)
    print(f"\n=== Running {dataset} with config {cfg_path} ===")

    cmd = [str(BINARY), "--config", str(cfg_path)]
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main():
    for ds in DATASETS:
        run_dataset(ds)


if __name__ == "__main__":
    main()
