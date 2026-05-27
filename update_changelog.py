import os
from datetime import datetime

# ====================================
# FILE YANG DIPANTAU
# ====================================

WATCH_FILES = [

    "app.py",

    "static/css/style.css",

    "static/js/main.js"
]

# ====================================
# FILE CACHE
# ====================================

CACHE_FILE = ".file_hashes"

# ====================================
# CHANGELOG
# ====================================

CHANGELOG_FILE = "CHANGELOG.md"

# ====================================
# AMBIL LAST MODIFIED
# ====================================

def get_modified_time(filepath):

    if not os.path.exists(filepath):
        return None

    return os.path.getmtime(filepath)

# ====================================
# LOAD CACHE
# ====================================

def load_cache():

    cache = {}

    if os.path.exists(CACHE_FILE):

        with open(CACHE_FILE, "r") as f:

            for line in f:

                name, timestamp = line.strip().split("|")

                cache[name] = float(timestamp)

    return cache

# ====================================
# SAVE CACHE
# ====================================

def save_cache(cache):

    with open(CACHE_FILE, "w") as f:

        for key, value in cache.items():

            f.write(f"{key}|{value}\n")

# ====================================
# MAIN
# ====================================

cache = load_cache()

changed_files = []

new_cache = {}

for file in WATCH_FILES:

    modified = get_modified_time(file)

    if modified is None:
        continue

    new_cache[file] = modified

    old_modified = cache.get(file)

    if old_modified != modified:

        changed_files.append(file)

# ====================================
# UPDATE CHANGELOG
# ====================================

if changed_files:

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        CHANGELOG_FILE,
        "a",
        encoding="utf-8"
    ) as changelog:

        changelog.write("\n\n")

        changelog.write(
            f"# Auto Update - {now}\n\n"
        )

        changelog.write(
            "## Updated Files\n\n"
        )

        for file in changed_files:

            changelog.write(
                f"- {file}\n"
            )

    print("CHANGELOG updated!")

else:

    print("No file changes detected.")

# ====================================
# SAVE CACHE
# ====================================

save_cache(new_cache)