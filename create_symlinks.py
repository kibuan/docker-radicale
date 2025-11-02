#!/usr/bin/env python3
import os
import logging

logging.basicConfig(level=logging.INFO, format="[create_symlinks] %(message)s")

COLLECTION_ROOT = os.environ.get("COLLECTION_ROOT", "/data/collections/collection-root")
SHARED_ROOT = os.environ.get("SHARED_ROOT", "")  # empty by default -> skip

def ensure_symlink(user_folder, shared_folder):
    basename = os.path.basename(shared_folder.rstrip("/"))
    symlink_path = os.path.join(user_folder, basename)
    try:
        if os.path.islink(symlink_path):
            current_target = os.readlink(symlink_path)
            if current_target != shared_folder:
                logging.info(f"Updating symlink {symlink_path} -> {shared_folder}")
                os.unlink(symlink_path)
                os.symlink(shared_folder, symlink_path)
            else:
                # already correct
                pass
        elif os.path.exists(symlink_path):
            logging.warning(f"Path exists and is not a symlink, skipping: {symlink_path}")
        else:
            logging.info(f"Creating symlink {symlink_path} -> {shared_folder}")
            os.symlink(shared_folder, symlink_path)
    except Exception as e:
        logging.exception(f"Failed to ensure symlink {symlink_path}: {e}")

def remove_old_symlinks(user_folder, valid_targets):
    for entry in os.listdir(user_folder):
        path = os.path.join(user_folder, entry)
        if os.path.islink(path):
            try:
                target = os.readlink(path)
            except OSError:
                # broken link — remove it
                logging.info(f"Removing broken symlink {path}")
                try:
                    os.unlink(path)
                except Exception as e:
                    logging.exception(f"Failed to remove {path}: {e}")
                continue
            if target not in valid_targets:
                logging.info(f"Removing outdated symlink {path} -> {target}")
                try:
                    os.unlink(path)
                except Exception as e:
                    logging.exception(f"Failed to remove {path}: {e}")

def main():
    if not SHARED_ROOT:
        logging.info("SHARED_ROOT not set. Skipping symlink creation.")
        return

    if not os.path.isdir(SHARED_ROOT):
        logging.info(f"SHARED_ROOT directory does not exist: {SHARED_ROOT}. Skipping.")
        return

    # gather existing shared collections (folders)
    shared_folders = []
    for name in os.listdir(SHARED_ROOT):
        shared_folder = os.path.join(SHARED_ROOT, name)
        if os.path.isdir(shared_folder):
            shared_folders.append(shared_folder)

    if not shared_folders:
        logging.info("No shared collections found in SHARED_ROOT. Nothing to do.")
        return

    # iterate users (subfolders) in COLLECTION_ROOT
    for user in os.listdir(COLLECTION_ROOT):
        user_folder = os.path.join(COLLECTION_ROOT, user)
        if not os.path.isdir(user_folder):
            continue

        valid_targets = []
        for shared_folder in shared_folders:
            ensure_symlink(user_folder, shared_folder)
            valid_targets.append(shared_folder)

        # remove symlinks that point to targets not in valid_targets
        remove_old_symlinks(user_folder, valid_targets)

if __name__ == "__main__":
    main()
