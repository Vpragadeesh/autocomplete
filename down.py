import os
import sys
import shutil
import subprocess
import zipfile

# /home/pragadeesh/autocomplete/down.py
import urllib.request

REPOS = [
    "https://github.com/psf/requests",
    "https://github.com/pallets/flask",
    "https://github.com/django/django",
    "https://github.com/tiangolo/fastapi",
    "https://github.com/pallets/jinja",
    "https://github.com/scikit-learn/scikit-learn",
    "https://github.com/pandas-dev/pandas",
]

TMP_DIR = "./tmp"
DATASET_DIR = "./dataset"


def ensure_dirs():
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(DATASET_DIR, exist_ok=True)


def repo_name_from_url(url):
    return url.rstrip("/").split("/")[-1]


def git_clone(url, dest):
    try:
        ret = subprocess.run(["git", "clone", "--depth", "1", url, dest], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False


def download_zip(url, dest_dir):
    name = repo_name_from_url(url)
    for branch in ("main", "master"):
        zip_url = f"{url}/archive/refs/heads/{branch}.zip"
        zpath = os.path.join(dest_dir, f"{name}-{branch}.zip")
        try:
            urllib.request.urlretrieve(zip_url, zpath)
            with zipfile.ZipFile(zpath, "r") as z:
                z.extractall(dest_dir)
            os.remove(zpath)
            # extracted folder name usually like name-branch
            extracted = os.path.join(dest_dir, f"{name}-{branch}")
            if os.path.isdir(extracted):
                return extracted
        except Exception:
            if os.path.exists(zpath):
                os.remove(zpath)
    return None


def copy_py_files(src_repo_dir, repo_name):
    for root, dirs, files in os.walk(src_repo_dir):
        for f in files:
            if f.endswith(".py"):
                src_path = os.path.join(root, f)
                rel_path = os.path.relpath(src_path, src_repo_dir)
                dest_path = os.path.join(DATASET_DIR, repo_name, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                try:
                    shutil.copy2(src_path, dest_path)
                except Exception:
                    pass


def process_repo(url):
    name = repo_name_from_url(url)
    dest = os.path.join(TMP_DIR, name)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    print(f"[+] Processing {name}")
    cloned = False
    if shutil.which("git"):
        cloned = git_clone(url, dest)
    extracted_dir = None
    if not cloned:
        extracted_dir = download_zip(url, TMP_DIR)
        if extracted_dir:
            # move extracted folder to tmp/<name> for consistency
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            shutil.move(extracted_dir, dest)
        else:
            print(f"[-] Failed to fetch {url}")
            return
    copy_py_files(dest, name)


def main():
    ensure_dirs()
    for r in REPOS:
        process_repo(r)
    print("Done. .py files copied into:", os.path.abspath(DATASET_DIR))


if __name__ == "__main__":
    main()