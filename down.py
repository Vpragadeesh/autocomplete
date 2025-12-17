import os
import sys
import shutil
import subprocess
import zipfile
import urllib.request
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    base_dir = os.path.dirname(__file__)
except NameError:
    base_dir = os.getcwd()

links_file = os.path.join(base_dir, "links.txt")
REPOS = []
if os.path.exists(links_file):
    with open(links_file, "r", encoding="utf-8") as f:
        REPOS = [
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
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
        subprocess.run(
            ["git", "clone", "--depth", "1", url, dest],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
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
        try:
            shutil.rmtree(dest)
        except Exception:
            pass
    cloned = False
    if shutil.which("git"):
        cloned = git_clone(url, dest)
    if not cloned:
        extracted_dir = download_zip(url, TMP_DIR)
        if extracted_dir:
            if os.path.isdir(dest):
                try:
                    shutil.rmtree(dest)
                except Exception:
                    pass
            try:
                shutil.move(extracted_dir, dest)
            except Exception:
                return (name, False)
        else:
            return (name, False)
    copy_py_files(dest, name)
    return (name, True)


def main():
    ensure_dirs()
    if not REPOS:
        print("No repos found in links.txt")
        return

    max_workers = min(32, ((os.cpu_count() or 1) * 2))
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        futures = {exe.submit(process_repo, r): r for r in REPOS}
        for fut in as_completed(futures):
            try:
                name, ok = fut.result()
                status = "OK" if ok else "FAILED"
            except Exception:
                name = futures[fut]
                status = "FAILED"
            print(f"[{status}] {name}")

    print("Done. .py files copied into:", os.path.abspath(DATASET_DIR))


if __name__ == "__main__":
    main()