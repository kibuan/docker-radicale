#!/usr/bin/env python3
import os
import logging

logging.basicConfig(level=logging.INFO)

COLLECTION_ROOT = os.environ.get("COLLECTION_ROOT", "/data/collections/collection-root")
SHARED_ROOT = os.environ.get("SHARED_ROOT", "/data/collections/collection-shared")
SHARED_COLLECTIONS = os.environ.get("SHARED_COLLECTIONS", "") # absolute path to extra shared collections. Use , as delimiter 

def ensure_symlink(user_folder, shared_folder):
    basename = os.path.basename(shared_folder.rstrip("/"))
    symlink_path = os.path.join(user_folder, basename)
    if os.path.islink(symlink_path):
        current_target = os.readlink(symlink_path)
        if current_target != shared_folder:
            logging.info(f"Updating symlink {symlink_path} -> {shared_folder}")
            os.unlink(symlink_path)
            os.symlink(shared_folder, symlink_path)
    elif os.path.exists(symlink_path):
        logging.warning(f"Cannot create symlink: path exists and is not symlink: {symlink_path}")
    else:
        logging.info(f"Creating symlink {symlink_path} -> {shared_folder}")
        os.symlink(shared_folder, symlink_path)

def remove_old_symlinks(user_folder, valid_targets):
    for entry in os.listdir(user_folder):
        path = os.path.join(user_folder, entry)
        if os.path.islink(path) and os.path.abspath(os.readlink(path)) not in map(os.path.abspath, valid_targets):
            logging.info(f"Removing outdated symlink {path}")
            os.unlink(path)

def main():
    if not SHARED_ROOT or not os.path.isdir(SHARED_ROOT):
        logging.info("No SHARED_ROOT provided or folder missing. Skipping symlink creation.")
        return

    shared_folders = [
        os.path.join(SHARED_ROOT, entry)
        for entry in os.listdir(SHARED_ROOT)
        if os.path.isdir(os.path.join(SHARED_ROOT, entry))
    ]

    if not shared_folders:
        logging.info("No shared collections found in SHARED_ROOT. Skipping.")
        return

    for user in os.listdir(COLLECTION_ROOT):
        user_folder = os.path.join(COLLECTION_ROOT, user)
        if not os.path.isdir(user_folder):
            continue

        valid_targets = []
        for shared_folder in shared_folders:
            ensure_symlink(user_folder, shared_folder)
            valid_targets.append(shared_folder)

        for shared_folder in SHARED_COLLECTIONS.split(','):
            shared_folder = shared_folder.strip()
            if not shared_folder:
                continue
            if os.path.isdir(shared_folder):
                ensure_symlink(user_folder, shared_folder)
                valid_targets.append(shared_folder)
            else:
                logging.warning(f"Shared collection {shared_folder} does not exist")           

        remove_old_symlinks(user_folder, valid_targets)

if __name__ == "__main__":
    main()
