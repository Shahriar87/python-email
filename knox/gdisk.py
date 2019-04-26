
import json
import knox
import os
import subprocess
import time

from . import byte
from . import logger

def handle_items(items):
    for item in items:
        handle_item(item[0], item[1])

        # Error Checking
        try:
            handle_item(item[0], item[1])
        except:
            msg = "!!!!! GDISK connection failed !!!!!"
            print(msg)
            # error_email function call
            email.error_email(msg)
        else:
            print("!!!! No fail on running GDISK. Check for possible database connection errors !!!!")


def handle_item(disk_name, config):
    real_prefix = config["prefix"] + "-"
    snap_prefix = real_prefix + config["seed"] + "-" + disk_name

    # Take snapshot
    logger.start_progress("Snapshotting " + disk_name)
    if not config["dry_run"]:
        snap_size_b = snapshot_disk(config["gcloud_bin"], disk_name, snap_prefix)
        snap_size_mb = byte.b_to_mb(int(snap_size_b))
    else:
        time.sleep(1)
        snap_size_mb = 0
    logger.end_progress("%.2f MB" % snap_size_mb)

    # Clean snapshots
    disk_snapshots = list_disk_snapshots(config["gcloud_bin"], 
        disk_name, real_prefix)

    expired_snapshots = release_snapshots(disk_snapshots, 
        config["retain"])

    logger.log_info("Cleaning expired snapshots...")
    for snapshot in expired_snapshots:
        logger.start_progress("Deleting " + snapshot)
        delete_snapshot(config["gcloud_bin"], snapshot)
        logger.end_progress()

    logger.log_info("Expired snapshots removed.")

def snapshot_disk(gcloud_bin, disk, name):
    null_fh = open(os.devnull, 'w')
    snapped_json = subprocess.check_output([
        gcloud_bin,
        "-q",
        "compute",
        "disks",
        "snapshot",
        "--format",
        "json",
        disk,
        "--snapshot-names",
        name
    ], stderr=null_fh)
    null_fh.close()
    snapped = json.loads(snapped_json.decode('utf-8'))
    snapshot = snapped[0]
    return snapshot["storageBytes"]

def list_disk_snapshots(gcloud_bin, disk, prefix):
    snapshots_json = subprocess.check_output([
        gcloud_bin,
        "-q",
        "compute",
        "snapshots",
        "list",
        "--format",
        "json",
        "--filter",
        ("sourceDisk=%s" % (disk)),
        "--filter",
        ("name~'^%s'" % prefix)
    ])
    return json.loads(snapshots_json.decode('utf-8'))

def release_snapshots(snapshots, retain):
    snapshot_names = []
    for snapshot in snapshots:
        snapshot_names.append(snapshot["name"])
    return snapshot_names[0:(-int(retain))]

def delete_snapshot(gcloud_bin, name):
    subprocess.check_output([
        gcloud_bin,
        "-q",
        "--no-user-output-enabled",
        "compute",
        "snapshots",
        "delete",
        name
    ])
