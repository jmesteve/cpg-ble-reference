import argparse
import csv
import configparser
import difflib
import hashlib
import json
import os
import pandas as pd
import re
import shutil
import subprocess
import sys

from pathlib import Path



blocks_ids = {}

global block_patterns
global template_excel 


def config_init(repository):
    sys.set_int_max_str_digits(1000000)
    config = configparser.ConfigParser()
    config.optionxform = str

    cwd = os.path.dirname(__file__)
    config_path =  os.path.join(cwd, "config.ini")
    config.read(config_path)

    config_path =  os.path.join(cwd, "config_local.ini")
    config.read(config_path)

    global block_patterns
    global template_excel 

    config_default = config["DEFAULT"]
    if config.has_section(repository):
        config_repo = config[repository]
    else:
        config_repo = {}
    platform = config_repo.get("platform") or config_default.get("platform")
    baseline = config_repo.get("baseline") or config_default.get("baseline")
    level_max = config_repo.get("level_max") or config_default.get("level_max")
    version_default = config_repo.get("version_default") or config_default.get("version_default")
    template_excel = config_repo.get("template_excel") or config_default.get("template_excel")
    reports_root = config_repo.get("reports_root") or config_default.get("reports_root")
    reports = config_repo.get("reports") or config_default.get("reports")
    block_patterns = config_repo.get("block_patterns") or config_default.get("block_patterns")
    feats = config_repo.get("feats") or config_default.get("feats")
    snippet_feats = config_repo.get("snippet_feats") or config_default.get("snippet_feats")
    defaults = {
        "platform" : json.loads(platform),
        "baseline" : json.loads(baseline),
        "level_max" : json.loads(level_max),
        "version_default" : json.loads(version_default),
        "template_excel" : json.loads(template_excel),
        "reports_root": json.loads(reports_root),
        "reports" : json.loads(reports),
        "block_patterns" : json.loads(block_patterns),
        "feats" : json.loads(feats),
        "snippet_feats": json.loads(snippet_feats) 
    }
    block_patterns = defaults.get("block_patterns")
    template_excel = defaults.get("template_excel")

    return defaults


def open_json(filename):
    with open(filename) as inputfile:
        df = json.load(inputfile)
    blocks = [df.get("symbols")]
    return blocks


def parser_artifacts(artifacts, output, level=0, parent=None, level_max=None):
    for artifact in artifacts:
        uuid = "{:02}-{}".format(level, hashlib.md5(artifact.get("name").encode("UTF-8")).hexdigest())
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


def to_excel(csv_file, report_directory, repository, feat, report):
    origin = Path(template_excel)
    destination = Path("{}/{}_{}_summary.xlsx".format(report_directory, report, repository))
    if not os.path.exists(destination):
        shutil.copy2(origin, destination)
    writer = pd.ExcelWriter(destination, engine='openpyxl', mode='a', if_sheet_exists="replace")
    csv = pd.read_csv(csv_file)
    df1 = pd.DataFrame(csv)
    df1.to_excel(writer, sheet_name=feat.upper(), index=None, header=True)
    writer.close()


def to_file(filename, data):
    filename.parent.mkdir(exist_ok=True, parents=True)
    with open(filename, 'w', newline='', encoding="utf-8") as output_file:
        print(data)
        output_file.write(data)
        
        
def generate_report(summary, report, feat, level_max, report_destination, baseline=None):
    filename = Path("{}/{}.json".format(report_destination, report))
    input = open_json(filename)
    output = {}
    output_filename = Path("{}/{}.csv".format(report_destination, report))
    parser_artifacts(input, output, level_max=level_max)
    to_csv(output_filename, output)
    for key, value in output.items():
        if summary.get(key):
            summary[key][feat] = value.get("size")
            if baseline and summary[key].get(baseline) and summary[key][baseline] > 0:
                size_percent = round(((value.get("size")/summary[key][baseline]) - 1)*100, 2)
            else:
                size_percent = 0 
            size_percent_name = "{}(%)".format(feat)
            summary[key][size_percent_name] = size_percent
        else:
            summary[key] = {"uuid": key,
                            "level": value.get("level"),
                            "name": value.get("name"),
                            feat: value.get("size")
                            }
                
        
def generate_summary(report, feat, repository, report_directory, report_destination):
    output_filename = Path("{}/{}.csv".format(report_destination, report))
    to_excel(output_filename, report_directory, repository, feat, report)


def generate_autoconf(build_directory, report_destination):
    autoconf_path = Path("{}/zephyr/include/generated/zephyr/autoconf.h".format(
        build_directory))
    shutil.copy2(autoconf_path, report_destination)


def compare_autoconf(report_destination, report_destination_baseline):
    autoconf_path = Path("{}/autoconf.h".format(
        report_destination))
    autoconf_baseline= Path("{}/autoconf.h".format(
        report_destination_baseline))
    f1 = open(autoconf_baseline, "r")
    f2 = open(autoconf_path,"r")
    diff = difflib.ndiff(f1.readlines(), f2.readlines())
    delta = ''.join(diff)
    f1.close()
    f2.close()
    diff_autoconf = Path("{}/autoconf_diff.h".format(
        report_destination))
    with open(diff_autoconf, 'w', newline='') as inputfile:
        inputfile.write(delta)


def generate_build(repository, build, feat, platform_path, extra_config=None, snippet_feat=None):
    cmd = "west build"
    if snippet_feat:
        cmd = "{} -S {}".format(cmd, snippet_feat)
    cmd = "{} -s {} -b {} --pristine --build-dir {} -- -DFILE_SUFFIX={}".format(
        cmd, repository, platform_path, build, feat)
    if extra_config:
        cmd = "{} -DEXTRA_CONF_FILE='{}.conf'".format(cmd, extra_config)
    result = subprocess.run(cmd, capture_output=True, timeout=500)
    stdout = result.stdout.decode("utf-8")
    print(stdout)


def build_memory_report(report, memory_repository, report_destination):
    cmd = "west build -d {} -t {}_report".format(memory_repository, report)
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    stdout = result.stdout.decode("utf-8")
    output_data = Path("{}/{}.data".format(report_destination, report))
    to_file(output_data, stdout)
    json_path = Path("{}/{}.json".format(memory_repository, report))
    shutil.copy2(json_path, report_destination)


def args_procedure():
    parser=argparse.ArgumentParser(description="Memory report help")
    parser.add_argument("-r", "--repository", required = True)
    parser.add_argument("-f", "--feats", required = False, nargs='+')
    parser.add_argument("-p", "--platform", required = False)
    parser.add_argument("-c", "--platform-code", required = False, type=str)
    parser.add_argument("-l", "--level-max", required = False, type=int)
    parser.add_argument("-b", "--baseline", required = False, type=str)
    parser.add_argument("-s", "--snippet", required = False, type=str)
    parser.add_argument("-e", "--extra-config", required = False, type=str)
    parser.add_argument("-v", "--version", required = False, type=str)
    parser.add_argument("--only-report", action="store_true")
    parser.add_argument("--only-summary", action="store_true")
    if len(sys.argv) == 1:
        parser.print_help()

    args, unknowns = parser.parse_known_args()
    return args


if __name__ == '__main__':

    args = args_procedure()
    
    repository = args.repository.strip()
    defaults = config_init(repository)

    if args.level_max:
        level_max = args.level_max
    else:
        level_max = defaults.get("level_max")
    if args.platform:
        platform = args.platform.strip()
    else:
        platform = defaults.get("platform")
    if args.baseline:
        baseline = args.baseline.strip()
    else: 
        baseline = defaults.get("baseline")
    if args.extra_config:
        extra_config = args.extra_config.strip()
    else:
        extra_config = None
    if args.version:  
        version = args.version.strip()
    else:
        version = defaults.get("version_default")
    if args.snippet:
        snippet = args.snippet.strip()
    else:
        snippet = None
    only_summary = args.only_summary
    only_report = args.only_report
    
    if args.platform_code == None:
        platform_code = platform.split("/")[1]
    else:
        platform_code = args.platform_code
    if args.feats != None:
        feats = args.feats
    else:
        feats = defaults.get("feats")


    for report in defaults["reports"]:    
        summary = {}
        for feat in feats:
            report_id = "{}_{}".format(platform_code, feat)
            if extra_config:
                report_id = "{}_{}".format(report_id, extra_config)
            report_dir_name = "{}/{}/{}".format(defaults["reports_root"], version, repository)
            report_directory = Path(report_dir_name)
            report_destination = Path("{}/{}".format(report_dir_name, report_id))
            build_directory = Path("{}/build_{}".format(repository, report_id))
            memory_directory = Path("{}/{}".format(build_directory, repository))

            if report == "rom":
                if only_summary == False and only_report == False:
                    if snippet == None and defaults.get("snippet_feats"):
                        snippet = defaults["snippet_feats"].get(feat)
                    else:
                        snippet = None
                    generate_build(repository, build_directory, feat, platform, extra_config, snippet)   

                if only_summary == False:
                    generate_autoconf(memory_directory, report_destination)
                    if baseline:
                        report_baseline_id = "{}_{}".format(platform_code, baseline)
                        if extra_config:
                            report_baseline_id = "{}_{}".format(report_baseline_id, extra_config)
                        report_destination_baseline = Path("{}/{}".format(report_dir_name, report_baseline_id))
                        compare_autoconf(report_destination, report_destination_baseline)
                    build_memory_report(report, memory_directory, report_destination)

            generate_report(summary, report, feat, level_max, report_destination, baseline)
            generate_summary(report, feat, repository, report_directory, report_destination)
        output_filename = Path("{}/{}_{}_summary.csv".format(report_directory, report, repository))
        to_csv(output_filename, summary)
        to_excel(output_filename, report_directory, repository, "Summary", report)