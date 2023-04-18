import os
import time
import json
import traceback
import locale
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


# to convert string (with commas) to integer
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# crawl page using selenium to get same HTML that can be seen in a browser
# using requests was giving a different HTML response :)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.page_load_strategy = 'normal'  
chrome_path = ChromeDriverManager().install()
chrome_service = Service(chrome_path)
DRIVER = Chrome(options=options, service=chrome_service)
DRIVER.implicitly_wait(5)

# URL prefix to be used for getting each extension's web store details page
CHROME_WEBSTORE_URL_PREFIX = "https://chrome.google.com/webstore"

def create_extension_metadata(ext_id, metadata_path):
    name_tag = None
    description_tag = None
    avg_rating_tag = None
    category_tag = None
    num_users_tag = None

    category_debug_filepath = "need_to_find_categories_for.txt"
    category_debug_file = open(category_debug_filepath, "a")
    try: 
        res_dict = {}
        res_dict["extension_id"] = ext_id

        # get page source using selenium
        chrome_webstore_ext_url = f"{CHROME_WEBSTORE_URL_PREFIX}/detail/{ext_id}"
        DRIVER.get(chrome_webstore_ext_url)
        time.sleep(5)

        # parse page source using bs4
        soup = BeautifulSoup(DRIVER.page_source.encode("utf-8"), "html.parser")
        # print(soup.prettify())  # DEBUGGING

        # extracting name
        name_tag = soup.select('meta[property="og:title"]')[0]
        extension_name = name_tag.get("content")
        res_dict["extension_name"] = extension_name

        # # extracting description
        # description_tag = soup.select('meta[property="og:description"]')[0]
        # res_dict["description"] = description_tag.get("content")

        # extracting average rating and number of users who rated 
        # title attribute of tag contains string "Average rating: X out of 5. Y users rated...")
        avg_rating_tag = soup.select('span[aria-label^="Average rating"]')
        if (len(avg_rating_tag) > 0):
            avg_rating_title_text = avg_rating_tag[0].get("aria-label").split() 
            res_dict["avg_rating"] = locale.atof(avg_rating_title_text[2])
            if (avg_rating_title_text[6] == "One"):
                res_dict["num_users_who_rated"] = 1
            else:
                res_dict["num_users_who_rated"] = locale.atoi(avg_rating_title_text[6])
        else:
            print("Average rating not found")
            res_dict["avg_rating"] = 0
            res_dict["num_users_who_rated"] = 0

        # extracting category
        category_tag = soup.select('a[aria-label^="Category:"]')
        if (len(category_tag) > 0):
            res_dict["category"] = category_tag[0].text
        else:
            print(f"No category found for extension {ext_id}: {extension_name}")
            category_debug_file.write(f"No category found for extension {ext_id}: {extension_name}\n")
            res_dict["category"] = "None"

        # extracting number of users (number of users is a string like "10" "100,000+")
        # if number of users = 0, this element is not rendered on the page
        num_users = 0
        num_users_tag = soup.select('span[title$=" users"]')
        if (len(num_users_tag) > 0):
            num_users_str = num_users_tag[0].get("title").split()[0].replace("+", "")
            num_users = locale.atoi(num_users_str)
        res_dict["num_users_who_downloaded"] = num_users

        with open(metadata_path, 'w') as file:
            json.dump(
                res_dict, 
                file, 
                indent=4, 
                sort_keys=False, 
                skipkeys=True
            )
    except Exception as e:
        print(traceback.print_exc())

    category_debug_file.close()

def main():
    out_path = '/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/metadata'
    exts_path = '/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/analysis'
    df = pd.read_csv("/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/src/all_exts.csv")
    exts = df["ext_ids"]
    for i, ext in enumerate(exts):
        if (ext.endswith(".zip") is False):
            # ext = "adbacgifemdbhdkfppmeilbgppmhaobf" # (DEBUGGING)
            ext_path = os.path.join(exts_path, ext)
            metadata_path = os.path.join(out_path, f"{ext}.json")
            if os.path.exists(metadata_path):
                print(f"Already downloaded extension {i} metadata: ", ext)
                continue
            print(f"Downloading extension metadata for extension {i}, storing at {metadata_path}")
            try:
                create_extension_metadata(
                    ext_id=ext,
                    metadata_path=metadata_path
                )
                print("Downloaded metadata for extension: ", ext)
            except:
                continue


if __name__ == "__main__":
    main()