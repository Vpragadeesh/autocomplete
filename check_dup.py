import sys
import os
import tempfile

#!/usr/bin/env python3

def remove_duplicate_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    seen = set()
    unique = []
    dup_found = False
    for line in lines:
        if line in seen:
            dup_found = True
            continue
        seen.add(line)
        unique.append(line)

    if not dup_found:
        print("No duplicates found.")
        return

    dirpath = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirpath)
    with os.fdopen(fd, "w", encoding="utf-8") as tf:
        tf.writelines(unique)
    os.replace(tmp_path, path)
    print(f"Removed duplicates: {len(lines) - len(unique)} lines removed. File updated: {path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_dup.py <file_path>")
        sys.exit(1)
    remove_duplicate_lines(sys.argv[1])