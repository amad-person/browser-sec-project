import os
import time
import json
import traceback
import locale
import pandas as pd


CRITICAL_RISK_API_PERMISSIONS = ['webRequest', 'declarativeNetRequest']
CRITICAL_RISK_HOST_PERMISSIONS = ['*://*/', '*://*/', '<all_urls>']

HIGH_RISK_API_PERMISSIONS = ['scripting', 'tabs', 'webNavigation', 'downloads', 'clipboardRead', 'history']
HIGH_RISK_HOST_PERMISSIONS = ['file:///*', 'http://*/*', 'https://*/*']


def analyze_extension_manifest(ext_id, manifest_file_path, manifest_analysis_path):
    res_dict = {}
    res_dict["extension_id"] = ext_id

    try:
        manifest = json.load(open(manifest_file_path))
    except Exception as e:
        print("error")

    # Number of API and host permissions declared
    # For now we check whether critical/high risk APIs have been declared 
    # We don't check whether they are in host or optional 
    num_api_permissions = 0
    num_critical_risk_api_permissions = 0
    num_high_risk_api_permissions = 0
    if "permissions" in manifest:
        num_api_permissions = len(manifest["permissions"])
        for p in manifest["permissions"]:
            if p in CRITICAL_RISK_API_PERMISSIONS:
                num_critical_risk_api_permissions += 1

            if p in HIGH_RISK_API_PERMISSIONS:
                num_high_risk_api_permissions += 1

    res_dict["num_api_permissions"] = num_api_permissions

    num_opt_api_permissions = 0
    if "optional_permissions" in manifest:
        num_opt_api_permissions = len(manifest["optional_permissions"])
        for p in manifest["optional_permissions"]:
            if p in CRITICAL_RISK_API_PERMISSIONS:
                num_critical_risk_api_permissions += 1

            if p in HIGH_RISK_API_PERMISSIONS:
                num_high_risk_api_permissions += 1

    res_dict["num_opt_api_permissions"] = num_opt_api_permissions

    res_dict["num_critical_risk_api_permissions"] = num_critical_risk_api_permissions
    res_dict["num_high_risk_api_permissions"] = num_high_risk_api_permissions

    num_host_permissions = 0
    num_critical_risk_host_permissions = 0
    num_high_risk_host_permissions = 0
    if "host_permissions" in manifest:
        num_host_permissions = len(manifest["host_permissions"])
        for p in manifest["host_permissions"]:
            if p in CRITICAL_RISK_HOST_PERMISSIONS:
                num_critical_risk_host_permissions += 1

            if p in HIGH_RISK_HOST_PERMISSIONS:
                num_high_risk_host_permissions += 1
    res_dict["num_host_permissions"] = num_host_permissions

    num_opt_host_permissions = 0
    if "optional_host_permissions" in manifest:
        num_opt_host_permissions = len(manifest["optional_host_permissions"])
        for p in manifest["optional_host_permissions"]:
            if p in CRITICAL_RISK_HOST_PERMISSIONS:
                num_critical_risk_host_permissions += 1

            if p in HIGH_RISK_HOST_PERMISSIONS:
                num_high_risk_host_permissions += 1
    res_dict["num_opt_host_permissions"] = num_opt_host_permissions

    res_dict["num_critical_risk_host_permissions"] = num_critical_risk_host_permissions
    res_dict["num_high_risk_host_permissions"] = num_high_risk_host_permissions

    # Whether CSP is declared
    is_csp_declared = 0  # 0 = false
    if "content_security_policy" in manifest:
        is_csp_declared = 1  # 1 = true
    res_dict["is_csp_declared"] = is_csp_declared

    # Number of WARs
    num_wars = 0
    if "web_accessible_resources" in manifest:
        wars_list = manifest["web_accessible_resources"]
        num_wars = sum([len(war["resources"]) for war in wars_list])
    res_dict["num_wars"] = num_wars

    # Number of externally connectable resources
    num_ext_conn = 0
    if "externally_connectable_resources" in manifest:
        ext_conn_obj = manifest["externally_connectable_resources"]
        if "id" in ext_conn_obj:
            ext_conn_list = ext_conn_obj["id"]
            if "*" in ext_conn_list:
                num_ext_conn = "ALL"
            else:
                num_ext_conn = len(ext_conn_list)
    res_dict["num_ext_conn"] = num_ext_conn


    with open(manifest_analysis_path, 'w') as file:
        json.dump(
            res_dict, 
            file, 
            indent=4, 
            sort_keys=False, 
            skipkeys=True
        )


def main():
    out_path = '/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/manifest_analysis'
    
    ext_source_path = '/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/out'
    exts_path = '/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/analysis'
    
    df = pd.read_csv("/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/src/all_exts.csv")
    exts = df["ext_ids"]
    print(len(exts))
    for i, ext in enumerate(exts):
        if (ext.endswith(".zip") is False):
            # ext = "adbacgifemdbhdkfppmeilbgppmhaobf" # (DEBUGGING)
            ext_path = os.path.join(ext_source_path, ext)
            manifest_analysis_path = os.path.join(out_path, f"{ext}.json")
            if os.path.exists(manifest_analysis_path):
                # print(f"Already analyzed extension {i} manifest: ", ext)
                continue
            print(f"Analyzing manifest for extension {i}, storing results at {manifest_analysis_path}")

            analyze_extension_manifest(
                ext_id=ext,
                manifest_file_path=f"{ext_path}/manifest.json",
                manifest_analysis_path=manifest_analysis_path
            )
            print("Analyzing manifest for extension: ", ext)


if __name__ == "__main__":
    main()