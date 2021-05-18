# ======================================
#                Useful
# ======================================

import os
import zipfile
from itertools import islice
import concurrent.futures
   
def unzip(zip_file, target_dir):
    with zipfile.ZipFile(zip_file, 'r') as f:
        f.extractall(target_dir)
    print(f"DONE! Unzipped {os.path.basename(zip_file)} into {target_dir}")

def makeBatches(items, batch_size):
    while True:
        batch = list(islice(items, batch_size))
        if not batch:
            break
        yield batch