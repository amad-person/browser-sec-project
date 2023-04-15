import json
from pprint import pprint as pp
from extstats.download_crx import down
from extstats.parse_infos import extract_manifest_of_file, parse_page
from extstats.CONSTS import CRX_DIRECTORY
from random import shuffle

from termcolor import colored

from tqdm import tqdm

import sys
import os
import shutil
import requests
from extstats.store_infos_history import is_stored_recent, store_infos_history, latest_stored, is_404

ORDER_BY_POP = len(sys.argv) > 1 and sys.argv[1] == 'by_pop'
SPECIFIC_EXT = sys.argv[1] if not ORDER_BY_POP and len(sys.argv) > 1 else None
print('ORDER_BY_POP ?', ORDER_BY_POP)

TMP_FILE = 'crawled/tmp/tmp_crx_{ext_id}.zip'
DEST_DIR = CRX_DIRECTORY + '{ext_id}/'
DEST_FILE = '{dir}/{version}.zip'

extlist = json.load(open('data/sitemap.json'))

shuffle(extlist)

def bad(x): return colored(x, 'red')
def good(x): return colored(x, 'green')

ok = print
print = lambda *x: ''


#@deco.concurrent
def do(url):
    isDownloaded, isMv3 = False, False

    ext_id = url.split('/')[-1]
    if SPECIFIC_EXT and ext_id != SPECIFIC_EXT:
        return isDownloaded, isMv3
    print()
    print(ext_id)
    tmp_file = TMP_FILE.format(ext_id=ext_id)

    latest = latest_stored(ext_id)
    if latest and is_404(latest):
        return isDownloaded, isMv3
    if latest:
        print(latest.get('name'))
    if latest and latest['diff'].days > -2 and 'content' in latest:
        print('using latest stored')
        infos = latest['content']
    else:
        # get current version
        if url is None:
            url = "https://chrome.google.com/webstore/detail/_/"+ext_id
        try:
            req = requests.get(url)
            if req.status_code != 200:
                ok(bad('bad status code:'), req.status_code)
                return isDownloaded, isMv3
            page_html = req.text
        except Exception as e:
            ok(bad('fail to download page: '+url), e)
            return isDownloaded, isMv3
        try:
            infos = parse_page(page_html)
        except Exception as e:
            ok(bad('ERROR: bad parsing for ' + url), e)
            infos = {}
        if not is_stored_recent(ext_id) and 'version' in infos:
            store_infos_history(ext_id, infos)
            print('saved it :D')
    if 'version' not in infos:
        ok(bad('ERROR: no infos for ' + url))
        return isDownloaded, isMv3
    current_version = infos['version']
    print('current_version:', current_version)

    target_dir_path = DEST_DIR.format(ext_id=ext_id)
    target_file_path = DEST_FILE.format(dir=target_dir_path, version=current_version)

    # download extension
    if not os.path.isfile(target_file_path):
        # ^^^ caveat, the guy can have the same version name displayed but different versions
        try:
            down(ext_id, tmp_file)
            isDownloaded = False
        except Exception as e:
            ok(bad('fail to download crx:'), e)
            return isDownloaded, isMv3
        isDownloaded = True
        
        manifest = None
        try:
            manifest = extract_manifest_of_file(tmp_file)
        except Exception as e:
            ok(bad('bad download, parse of manifest failed'), e) 

        if manifest and 'manifest_version' in manifest:
            manifest_version = manifest['manifest_version']
            if manifest_version == 3:
                if manifest and 'version' in manifest:
                    version = manifest['version']
                    ok(good('manifest version:'), manifest_version)
                    isMv3 = True

                    # current_version represent version_name so it can be different than the version stored
                    target_file_path = DEST_FILE.format(dir=target_dir_path, version=version)
                    if os.path.isfile(target_file_path):
                        print(bad("file is already here, here's the version_name"),
                            manifest.get('version_name'),
                            'and .version=', manifest.get('version'))
                        os.remove(tmp_file)
                        return isDownloaded, isMv3
                    ok(good('version is added :D'), manifest['version'], url)
                    # assert current_version == version_name or version
                    os.makedirs(target_dir_path, exist_ok=True)
                    shutil.move(tmp_file, target_file_path)
                else:
                    try:
                        os.remove(tmp_file)
                    except FileNotFoundError:
                        pass
                    except OSError:
                        pass
            else:
                ok(print(good('skipping manifest version:'), manifest_version))
                isMv3 = False
    else:
        print('latest version already downloaded')

    return isDownloaded, isMv3


download_count, mv3_count = 0, 0
for url in tqdm(extlist):
    print(url)
    isDownloaded, isMv3 = do(url)
    if isDownloaded:
        download_count = download_count + 1
    if isMv3:
        mv3_count = mv3_count + 1

print(f"Number of MV3 extensions: {mv3_count}")
