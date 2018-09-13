
import os

def release_files(to_clean, retain):
    entries = os.listdir(to_clean)
    entry_files = []
    for entry in entries:
        if os.path.isfile(to_clean + "/" + entry):
            entry_files.append(entry)
    entry_files.sort()
    return entry_files[0:-retain]
