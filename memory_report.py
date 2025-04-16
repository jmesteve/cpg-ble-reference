import argparse
import csv
import difflib
import json
import os
import pandas as pd
import re
import shutil
import subprocess
import sys

from pathlib import Path


reports = ["rom", "ram"]
blocks_ids = {}
block_patterns = [ "sym_*", "__compound_literal*", "CSWTCH.*"]

feats = ["std1", "stdz1", "opt1",
         "feat1", "feat2", "feat3", "feat4", "feat5",
         "feat6", "feat7", "feat8", "feat9", "feat10"]


global counter
counter = 0


def open_json(filename):
    with open(filename) as inputfile:
        df = json.load(inputfile)
    blocks = [df.get("symbols")]
    return blocks


def parser_artifacts(artifacts, output, level=0, parent=None, level_max=None):
    for artifact in artifacts:
        global counter
        counter += 1
        uuid = (level * 10000) + counter
        data = {
            "uuid": uuid,
            "parent": parent,
            "level": level,
            "identifier": artifact.get("identifier"),
            "name": artifact.get("name"),
            "size": artifact.get("size"),
        }
        if level_max == None or level <= level_max:
            if block_patterns == None:
                output[uuid] = data
            else:
                pattern_finded = False
                for bp in block_patterns:
                    pattern = re.search(bp, artifact.get("name"))
                    if pattern:
                        pattern_finded = True
                        block_uuid = "{}{}".format(bp, level)
                        blocks_id = blocks_ids.get(block_uuid)
                        if output.get(blocks_id) == None:
                            blocks_ids[block_uuid] = uuid
                            output[uuid] = {
                                "uuid": uuid,
                                "parent": parent,
                                "level": level,
                                "identifier": bp,
                                "name": bp,
                                "size": artifact.get("size"),
                            }
                        else:
                            output[blocks_id]["size"] += artifact.get("size")
                        
                if pattern_finded == False:
                    output[uuid] = data

        if artifact.get("children"):
            parser_artifacts( artifact.get("children"), output, level=level+1, 
                              parent=uuid, level_max=level_max)
        
    
def to_csv(filename, data):
    data_list = []
    for key, value in data.items():
        data_list.append(value)
    data_list.sort(key=lambda k : k['uuid'])
    data_sorted = sorted(data_list, key=lambda k : k['uuid']) 
    keys = data_sorted[0].keys()
    filename.parent.mkdir(exist_ok=True, parents=True)
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_sorted)


def to_excel(csv_file, repository, feat, report):
    template_excel = Path("templates/Memory_Optimization_Template1.xlsx")
    excel_file = Path("reports/{}/{}_{}_summary.xlsx".format(repository, report, repository))
    if not os.path.exists(excel_file):
        shutil.copy(template_excel, excel_file)
    writer = pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists="replace")
    csv =pd.read_csv(csv_file)
    df1 = pd.DataFrame(csv)
    df1.to_excel(writer, sheet_name=feat.upper(), index=None, header=True)
    writer.close()


def to_file(filename, data):
    filename.parent.mkdir(exist_ok=True, parents=True)
    with open(filename, 'w', newline='', encoding="utf-8") as output_file:
        print(data)
        output_file.write(data)


def generate_reports(level_max, memory_repository, report_directory, only_summary=False):
    for report in reports:
        if only_summary == False:
            cmd = "west build -d {} -t {}_report".format(memory_repository, report)
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            stdout = result.stdout.decode("utf-8")
            output_filename = Path("{}/{}.data".format(report_directory, report))
            to_file(output_filename, stdout)
        filename = Path("{}/{}.json".format(memory_repository, report))
        input = open_json(filename)
        output = {}
        global counter
        counter = 0
        parser_artifacts(input, output, level_max=level_max)
        output_filename = Path("{}/{}.csv".format(report_directory, report))
        to_csv(output_filename, output)
        to_excel(output_filename, repository, feat, report)


def generate_autoconf(build_directory, report_directory):
    autoconf_path = Path("{}/zephyr/include/generated/zephyr/autoconf.h".format(
        build_directory))
    shutil.copy2(autoconf_path, report_directory)


def compare_autoconf(report_directory, report_directory_baseline):
    autoconf_path = Path("{}/autoconf.h".format(
        report_directory))
    autoconf_baseline= Path("{}/autoconf.h".format(
        report_directory_baseline))
    f1 = open(autoconf_baseline, "r")
    f2 = open(autoconf_path,"r")
    diff = difflib.ndiff(f1.readlines(), f2.readlines())
    delta = ''.join(diff)
    f1.close()
    f2.close()
    diff_autoconf = Path("{}/autoconf_diff.h".format(
        report_directory))
    with open(diff_autoconf, 'w', newline='') as inputfile:
        inputfile.write(delta)


def generate_build(repository, build, feat, platform_path):
    cmd = "west build -s {} -b {} --build-dir {} -- -DFILE_SUFFIX={}".format(
        repository, platform_path, build, feat)
    result = subprocess.run(cmd, capture_output=True, timeout=500)
    stdout = result.stdout.decode("utf-8")
    print(stdout)


def args_procedure():
    parser=argparse.ArgumentParser(description="Memory report help")
    parser.add_argument("-r", "--repository", required = True)
    parser.add_argument("-f", "--feats", required = False, nargs='+')
    parser.add_argument("-p", "--platform", required = True)
    parser.add_argument("-c", "--platform-code", required = False, type=str)
    parser.add_argument("-l", "--level-max", required = False, type=int)
    parser.add_argument("-b", "--baseline", required = False, type=str)
    parser.add_argument("--only-summary", action="store_true")
    if len(sys.argv) == 1:
        parser.print_help()

    args, unknowns = parser.parse_known_args()
    return args


if __name__ == '__main__':

    args = args_procedure()

    repository = args.repository.strip()
    level_max = args.level_max
    platform = args.platform.strip()
    baseline = args.baseline.strip()
    only_summary = args.only_summary
    
    if args.platform_code == None:
        platform_code = platform.split("/")[1]
    else:
        platform_code = args.platform_code
    if args.feats != None:
        feats = args.feats

    for feat in feats:
        report_directory = Path("reports/{}/{}_{}".format(repository, platform_code, feat))
        build_directory = Path("{}/build_{}_{}".format(repository, platform_code, feat))
        memory_directory = Path("{}/{}".format(build_directory, repository))

        if only_summary == False:
            generate_build(repository, build_directory, feat, platform)   

        generate_reports(level_max, memory_directory, report_directory, only_summary)

        if only_summary == False:
            generate_autoconf(memory_directory, report_directory)
            if baseline:
                report_directory_baseline = Path("reports/{}/{}_{}".format(repository, platform_code, baseline))
                compare_autoconf(report_directory, report_directory_baseline)
