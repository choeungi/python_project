import argparse
import os
import re
from datetime import datetime, timedelta

ERROR_CODE_REGEX = re.compile(r"(?<=ERROR\s)\w+")

def parse_log_line(log: str) -> dict:
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

def counter(log: dict, count: dict):
    if log["level"] == "INFO":
        count["INFO"] += 1
    elif log["level"] == "WARN":
        count["WARN"] += 1
    if log["level"] == "ERROR":
        count["ERROR"] += 1

def monitor_log(path: str, file_size_temp:int, error_only: bool, error_code=None,) -> int:
    with open(path, "r") as file:
        file.seek(file_size_temp)

        log_line = file.read()
        for line in log_line.splitlines():
            log_parse = parse_log_line(line)

            if log_parse:
                counter(log_parse, count)

            if args.error_only:
                if log_parse["level"] == "ERROR":
                    print(line.strip("\n"))
                    count_error_code(log_parse, error_code)
            else:
                print(line.strip("\n"))

        return os.path.getsize(path)

def print_statistics(play_time: datetime, count: dict) -> datetime:
    now = datetime.now()
    diff = now - play_time

    if diff.seconds >= 10:
        print("===== Statistics =====")
        print(f"INFO : {count["INFO"]}")
        print(f"WARN : {count["WARN"]}")
        print(f"ERROR : {count["ERROR"]}")
        print("======================")
        return now

    return play_time

def count_error_code(parse: dict, error_code: dict):
    if error_code == None:
        return
    
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

if args.error_only:
    error_code = {}

play_time = datetime.now()
timer = int(input("모니터링을 수행할 시간을 입력하세요.(단위: 분) : "))
end_time = play_time + timedelta(minutes=timer)

file_size_temp = os.path.getsize(path)

while datetime.now() < end_time:
    current_file_size = os.path.getsize(path)
    if current_file_size > file_size_temp:
        file_size_temp = monitor_log(path, file_size_temp, error_code)

    play_time = print_statistics(play_time, count)