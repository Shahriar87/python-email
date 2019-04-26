
import os
import time
from . import byte
from . import dirs
from . import logger
from . import email

def handle_items(items):
    for item in items:
        # Error Checking
        try:
            handle_item(item[0], item[1])
        except:
            msg = "!!!!! MYSQL connection failed !!!!!"
            print(msg)
            # error_email function call
            email.error_email(msg)
        else:
            print("!!!! No fail on running MYSQL. Check for possible database connection errors !!!!")


def handle_item(db_name, config):
    backup_dir = config["base_dir"] + "/" + db_name
    backup_path = backup_dir + "/" + config["seed"] + ".sql.gz"

    # Create backup directory
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    logger.log_info("Processing MySQL backup [%s]" % db_name)
    logger.start_progress("Writing " + backup_path)

    if not config["dry_run"]:
        dump_sql(db_name, backup_path)
    else:
        open(backup_path, 'a').close()
        time.sleep(1)

    backup_size = os.path.getsize(backup_path)
    backup_size_mb = byte.b_to_mb(backup_size)
    logger.end_progress("%.2f MB" % backup_size_mb)

    logger.log_info("Cleaning expired backups...")
    expired_files = dirs.release_files(backup_dir, config["retain"])
    for expired_file in expired_files:
        expired_file_path = backup_dir + "/" + expired_file
        logger.start_progress("Deleting " + expired_file_path)
        os.remove(expired_file_path)
        logger.end_progress()

    logger.log_info("Expired backups deleted.")

def dump_sql(db, backup_path):
    os.system("mysqldump --force --triggers --single-transaction %s | gzip -c > %s" 
        % (db, backup_path))
