# Copyright (C) 2021 Aurore Fass
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
    To call DoubleX from the command-line.
"""

import os
import argparse
import pandas as pd

from vulnerability_detection import analyze_extension


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def main():
    """ Parsing command line parameters. """

    parser = argparse.ArgumentParser(prog='doublex',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     description="Static analysis of a browser extension to detect "
                                                 "suspicious data flows")

    # parser.add_argument("-cs", "--content-script", dest='cs', metavar="path", type=str,
    #                     help="path of the content script. "
    #                     "Default: empty/contentscript.js (i.e., empty JS file)")
    # parser.add_argument("-bp", "--background-page", dest='bp', metavar="path", type=str,
    #                     help="path of the background page "
    #                          "or path of the WAR if the parameter '--war' is given. "
    #                          "Default for background: empty/background.js (i.e., empty JS file)")
    #
    # parser.add_argument("--war", action='store_true',
    #                     help="indicate that the parameter '-bp' is the path of a WAR")
    # parser.add_argument("--not-chrome", dest='not_chrome', action='store_true',
    #                     help="indicate that the extension is not based on Chromium, e.g., for a Firefox extension")
    #
    # parser.add_argument("--manifest", metavar="path", type=str,
    #                     help="path of the extension manifest.json file. "
    #                          "Default: parent-path-of-content-script/manifest.json")
    # parser.add_argument("--analysis", metavar="path", type=str,
    #                     help="path of the file to store the analysis results in. "
    #                          "Default: parent-path-of-content-script/analysis.json")
    # parser.add_argument("--apis", metavar="str", type=str, default='all',
    #                     help='''specify the sensitive APIs to consider for the analysis:
    # - 'permissions' (default): DoubleX selected APIs iff the extension has the corresponding permissions;
    # - 'all': DoubleX selected APIs irrespective of the extension permissions;
    # - 'empoweb': APIs from the EmPoWeb paper; to use ONLY on the EmPoWeb ground-truth dataset;
    # - path: APIs listed in the corresponding json file; a template can be found in src/suspicious_apis/README.md.''')
    #
    # # TODO: control verbosity of logging?
    #
    # args = parser.parse_args()
    #
    # cs = args.cs
    # bp = args.bp
    # if cs is None:
    #     cs = os.path.join(os.path.dirname(SRC_PATH), 'empty', 'contentscript.js')
    # if bp is None:
    #     bp = os.path.join(os.path.dirname(SRC_PATH), 'empty', 'background.js')

    out_path = '/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/analysis'
    exts_path = '/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/out'
    # exts = os.listdir(exts_path)

    df = pd.read_csv("/Users/aadyaamaddi/Desktop/MSIT_PE/Spring 2023/14828 Browser Security/project/DoubleX_mod/src/all_exts.csv")
    exts = df["ext_ids"]
    for ext in exts:
        ext_path = os.path.join(exts_path, ext)
        analysis_path = os.path.join(out_path, ext)
        if os.path.exists(analysis_path):
            print("Already analyzed extension: ", ext)
            continue
        print(ext, ext_path, analysis_path)
        try:
            analyze_extension("{}/content_scripts.js".format(ext_path), "{}/background.js".format(ext_path),
                              json_analysis=analysis_path, 
                              chrome=True,
                              war=None, json_apis='all', 
                              manifest_path="{}/manifest.json".format(ext_path))
            print("Finished analysis for extension: ", ext)
        except:
            continue


if __name__ == "__main__":
    main()
