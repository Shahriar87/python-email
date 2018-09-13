
import configparser
import datetime as dt
import os
import knox.logger
import knox.gdisk
import knox.mysql

RC_PATH = os.getenv('HOME') + '/.knox.cfg'

def get_drivers():
    return {
        "mysql": knox.mysql,
        "gdisk": knox.gdisk,
    }

def get_default_config():
    return {
        "base_dir": os.getenv('HOME') + "/backups",
        "dry_run": True,
        "gcloud_bin": "/snap/bin/gcloud",
        "log_level": 100,
        "retain_db": 14,
        "retain_disk": 7,
        "seed": get_default_seed(),
        "prefix": "knox"

    }

def get_user_config():
    if os.path.isfile(RC_PATH):
        cfg = configparser.ConfigParser()
        cfg.read(RC_PATH)
        return dict(cfg.items('defaults'))
    else:
        return {}

def main(items):

    # Prepare configuration
    config = {}
    config.update(get_default_config())
    config.update(get_user_config())
    logger.run_level = int(config["log_level"])

    # Load driver modules
    drivers = get_drivers()
    system_drivers = drivers.keys()
    logger.log_debug("Loaded with drivers: %s" % ", ".join(system_drivers))

    # Sort items by driver type
    sorted_items = sort_items(items)
    item_drivers = sorted_items.keys()
    logger.log_debug("Requested drivers: %s" % ", ".join(item_drivers))

    # Validate item types
    invalid_drivers = list(set(item_drivers) - set(system_drivers))
    if len(invalid_drivers) > 0:
        raise ValueError("System does not support drivers: " 
            + ", ".join(invalid_items))
    
    # Execute backups
    logger.log_debug("Processing %d items." % len(items))
    for driver_id in sorted_items:
        driver_items = sorted_items[driver_id]
        logger.log_debug("Sending %d item(s) to driver %s" % (len(driver_items), driver_id))
        drivers[driver_id].handle_items(config, driver_items)

def get_default_seed():
    return dt.datetime.now().strftime("%Y%m%d%H%M%S")

def sort_items(items):
    by_type = {}
    for item in items:
        parts = item.split(':')
        itype = parts[0]

        if itype not in by_type:
            by_type[itype] = []

        by_type[itype].append(parts[1:])

    return by_type
