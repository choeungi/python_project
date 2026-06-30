import argparse
import os
import re
import json
from datetime import datetime, timedelta

ERROR_CODE_REGEX = re.compile(r"(?<=ERROR\s)\w+")
APACHE_REGEX = re.compile(
        r"(?P<ip>\d+\.\d+\.\d+\.\d+) - - "
        r"\[(?P<date>[^\:]+):(?P<time>[^\]]+)\] "
        r"\"(?P<method>\w+) (?P<url>[^ ]+) (?P<protocol>[^\"]+)\" "
        r"(?P<status>\d+) "
        r"(?P<size>\d+)"
    )
def select_mode(filename_extention: str):
    if filename_extention == "standard":
        return parse_standard_log
    elif filename_extention == "json":
        return parse_json_log
    elif filename_extention == "apache":
        return parse_apache_log

def counter(log: dict, count: dict):
    if log["level"] == "INFO":
        count["INFO"] += 1
    elif log["level"] == "WARN":
        count["WARN"] += 1
    if log["level"] == "ERROR":
        count["ERROR"] += 1

def print_statistics(play_time: datetime, count: dict, error_only: bool, error_code: dict|None) -> datetime:
    now = datetime.now()
    diff = now - play_time

    if diff.seconds >= 10:
        if error_only:
            if error_code:
                print("===== Error Code =====")
                for key, value in error_code.items():
                    print(f"{key} : {value}")
                print("======================")
        else:
            print("===== Statistics =====")
            print(f"INFO : {count["INFO"]}")
            print(f"WARN : {count["WARN"]}")
            print(f"ERROR : {count["ERROR"]}")
            print("======================")
        return now

    return play_time

def count_error_code(parse: dict, error_code: dict|None):
    if not isinstance(error_code, dict):
        return
    
    search_code = parse.get["code"]

    if search_code == None:
        log_text = " ".join(parse.values())
        search_code = ERROR_CODE_REGEX.search(log_text)
    
        if not search_code:
            search_code = "UNKNOWN"
        else:
            search_code = search_code.group()
    
    if search_code not in error_code:
        error_code[search_code] = 1
    else:
        error_code[search_code] += 1

def parse_standard_log(log: str) -> dict:
    line = log.strip().split()

    if len(line) < 3:
        return None

    log_format = {
        "date": line[0],
        "time": line[1],
        "level": line[2],
        "messages": " ".join(line[3:])
    }
    return log_format

def parse_json_log(log: str):
    conversion = json.loads(log)
    parse_date_time = conversion["time"].split(" ")

    log_format = {
        "date": parse_date_time[0],
        "time": parse_date_time[1],
        "level": conversion["level"],
        "messages": conversion["message"]
    }
    log_format["code"] = conversion["code"] if "code" in list(conversion.keys()) else None

    return log_format

def parse_apache_log(log: str):
    
    partition = APACHE_REGEX.search(log).groupdict()
    log_format = {
        "date" : partition["date"],
        "time" : partition["time"],
        "messages" : f"{partition["ip"]} : {partition["protocol"]} {partition["method"]} {partition["url"]} {partition["status"]} {partition["size"]}(Byte)"
    }
    partition["status"] = int(partition["status"])
    if partition["status"] >= 400:
        log_format["level"] = "ERROR"
        log_format["code"] = partition["status"]
    elif partition["status"] >= 300:
        log_format["level"] = "WARN"
    else:
        log_format["level"] = "INFO"

    return log_format

def monitor_log(path: str, file_size_temp:int, error_only: bool, error_code: dict|None, mode) -> int:
    with open(path, "r") as file:
        file.seek(file_size_temp)

        log_line = file.read()
        for line in log_line.splitlines():
            log_parse = mode(line)

            if log_parse:
                counter(log_parse, count)

            if error_only:
                if log_parse["level"] == "ERROR":
                    print(line.strip("\n"))
                    count_error_code(log_parse, error_code)
            else:
                print(line.strip("\n"))

        return os.path.getsize(path)

parse = argparse.ArgumentParser(description="Monitors log files and outputs changes.")
parse.add_argument("log_path", help="This is the path to the log file to be monitored.")
parse.add_argument("--error-only",
                   action="store_true",
                   required=False,
                   help="This is an option to output only logs where the log level is Error.")
args = parse.parse_args()

path = args.log_path

count = {
    "INFO" : 0,
    "WARN" : 0,
    "ERROR" : 0
}
error_code = None

if args.error_only:
    error_code = {}
    
filename_extention = os.path.splitext(path)[0].split("/")[-1]
mode = select_mode(filename_extention)

play_time = datetime.now()
timer = int(input("모니터링을 수행할 시간을 입력하세요.(단위: 분) : "))
end_time = play_time + timedelta(minutes=timer)

file_size_temp = os.path.getsize(path)

while datetime.now() < end_time:
    current_file_size = os.path.getsize(path)
    if current_file_size > file_size_temp:
        file_size_temp = monitor_log(path, file_size_temp, args.error_only, error_code, mode)

    play_time = print_statistics(play_time, count, args.error_only, error_code)