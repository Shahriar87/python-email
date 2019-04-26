
import configparser
import datetime as dt
import os
import knox.logger
import knox.gdisk
import knox.mysql
import knox.mongo
import knox.email

RC_PATH = os.getenv('HOME') + '/.knox.cfg'


def get_drivers():
    return {
        "mysql": knox.mysql,
        "gdisk": knox.gdisk,
        "mongo": knox.mongo
    }

def get_default_config():
    return {
        "base_dir": os.getenv('HOME') + "/backups",
        "dry_run": False,
        "gcloud_bin": "/snap/bin/gcloud",
        "log_level": 100,
        "retain": 5,
        "seed": get_default_seed(),
        "prefix": "knox"

    }

def main(items):

    # Read configuration
    usr_config = configparser.ConfigParser()
    if os.path.isfile(RC_PATH):
        usr_config.read(RC_PATH)

    # Prepare configuration
    sys_config = get_default_config()

    if usr_config.has_section('defaults'):

        # print(usr_config.items('defaults'))
        sys_config.update(dict(usr_config.items('defaults')))

    validate_config(sys_config)
    logger.run_level = int(sys_config["log_level"])

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
            + ", ".join(invalid_drivers))
    
    # Execute backups
    logger.log_debug("Processing %d items." % len(items))
    for driver_id in sorted_items:
        prepared_items = prepare_items(sorted_items[driver_id], driver_id, sys_config, usr_config)
        logger.log_debug("Sending %d item(s) to driver %s" % (len(prepared_items), driver_id))
        # print(drivers[driver_id].handle_items(prepared_items))
        drivers[driver_id].handle_items(prepared_items)

def get_default_seed():
    return dt.datetime.now().strftime("%Y%m%d%H%M%S")

def sort_items(items):
    by_type = {}
    for item in items:
        parts = item.split(':')

        if len(parts) != 2:
            raise ValueError('Invalid item name: ' + item)

        itype = parts[0]

        if itype not in by_type:
            by_type[itype] = []

        by_type[itype].append(parts[1])

    return by_type

def validate_config(config):
    if not os.path.isdir(config["base_dir"]):
        raise ValueError("Backup dir does not exist: " + config["base_dir"])

def prepare_items(item_names, driver_id, sys_config, usr_config):
    
    # print(usr_config)
    prepared_items = []
    for name in item_names:
        full_name = driver_id + ':' + name

        # Merge defaults config
        item_config = sys_config.copy()

        # Merge driver config
        if usr_config.has_section(driver_id):
            item_config.update(dict(usr_config.items(driver_id)))
            

        # Merge item config
        if usr_config.has_section(full_name):
            item_config.update(dict(usr_config.items(full_name)))

        prepared_items.append((name, item_config))
        # print(prepared_items)

        
    return prepared_items
