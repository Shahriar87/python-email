
run_level = 100

def log_message(level, msg):
    if (level < run_level):
        print(msg)

def log_error(msg):
    log_message(0, msg)

def log_warning(msg):
    log_message(1, msg)

def log_info(msg):
    log_message(2, msg)

def log_debug(msg):
    log_message(3, msg)

def start_progress(msg):
    print("=>  %s ... " % msg, end='', flush=True)

def end_progress(msg=None):
    if msg:
        print("Done! (%s)" % msg)
    else:
        print("Done!")
