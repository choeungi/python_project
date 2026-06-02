import os
import sys
import re
import argparse

def build_log_text(log: dict) -> str:
    return " ".join(log.values())

def parse_log_line(division: str) -> dict | None:
    partition = division.strip().split()
    if len(partition) < 3:
        return None
    
    log_format = {
        "date": partition[0],
        "time": partition[1],
        "log_level": partition[2],
        "messages": " ".join(partition[3:])
    }

    return log_format

def run_mode(file_path: str, context: dict, mode) -> list:
    with open(file_path, "r") as file:
        context["program_error"] = []
        for num, line in enumerate(file, start=1):
            line = parse_log_line(line)
            if line:
                context["line_num"] = num
                mode(line, context)
            else:
                context["program_error"].append(num)

def filter_by_level(line: dict, context: dict):
    log_level = line["log_level"]
    if context["pattern"] == log_level:
        log_text = build_log_text(line)
        print(f"[{context['line_num']}] {log_text}")

def summarize_logs(line: dict, context: dict):
    log_level = line["log_level"]
    if log_level == "INFO":
        context["count"]["info_count"] +=  1
    elif log_level == "WARN":
        context["count"]["warn_count"] += 1
    elif log_level == "ERROR":
        context["count"]["error_count"] += 1

def analyze_statistics(line: dict, context: dict):
    regex = context["regex"]
    level = line["log_level"]
    log_text = build_log_text(line)

    if level == "ERROR":
        code = regex.search(log_text)
        if not code:
            context["table"]["UNKNOWN"] = context["table"]["UNKNOWN"] + 1 if "UNKNOWN" in context["table"] else 1
        else:
            code = code.group()
            if code not in context["table"]:
                context["table"][code] = 1
            else:
                context["table"][code] += 1

def search_logs(line: dict, context: dict):
    log_text = build_log_text(line)
    search = context["pattern"].search(log_text)
    if search:
        print(f"[{context['line_num']}] {log_text}")

def print_summary(context: dict):
    print("===== 로그 요약 =====")
    print(f"INFO: {context['count']['info_count']}")
    print(f"WARN: {context['count']['warn_count']}")
    print(f"ERROR: {context['count']['error_count']}")

def print_statistics(context: dict):
    code_list = list(context["table"].keys())

    if not code_list:
        print("발생한 ERROR가 없습니다.")
        return
    else:
        rank = sorted(context["table"].items(), key=lambda x: x[1], reverse=True)
        max_value = max(context["table"].values())

        print("===== ERROR 코드 통계 =====")
        for result in range(min(5, len(rank))):
            print(f"{rank[result][0]} : {context['table'][rank[result][0]]}")
        
        print("\n가장 많이 발생한 에러: ")
        for most in rank:
            if context["table"][most[0]] == max_value:
                print(f"{most[0]} ({context['table'][most[0]]}회)")

        if len(rank) > 5:
            print(f"\n기타 {len(rank) - 5}개 에러 코드 존재")

arg = argparse.ArgumentParser(description="Specific log line search to User want", formatter_class=argparse.RawTextHelpFormatter)
arg.add_argument("file_path", help="Log file path")
arg.add_argument("mode",
                 choices=["search", "level", "summary", "statistics"],
                 help="search : Find logs containing a specific string using regular expressions (This option requires the use of [pattern].)\n" \
                      "level : Log level filter (This option requires the use of [pattern].)\n" \
                      "summary : Each log count summary\n" \
                      "statistics : Error code statistics"
                      )
arg.add_argument("pattern", nargs="?", help="Specify the patterns required for log search and filtering.")

args = arg.parse_args()
context = {}

if args.mode == "level":
    if not args.pattern:
        arg.print_help()
        exit()
    mode = filter_by_level
    context["pattern"] = args.pattern.upper()
    
elif args.mode == "summary":
    if args.pattern:
        arg.print_help()
        exit()
    mode = summarize_logs
    
    context["count"] = {
        "info_count": 0,
        "warn_count": 0,
        "error_count": 0
    }

elif args.mode == "statistics":
    if args.pattern:
        arg.print_help()
        exit()
    mode = analyze_statistics
    context["table"] = {}
    context["regex"] = re.compile(r"(?<=ERROR\s)\w+")

elif args.mode == "search":
    if not args.pattern:
        arg.print_help()
        exit()
    mode = search_logs
    context["pattern"] = re.compile(fr"{args.pattern}", re.IGNORECASE)

file_path = args.file_path
retry = 0
while retry < 3:
    try:
        run_mode(file_path, context, mode) 
        break   
    except FileNotFoundError as e:
        retry += 1
        print("파일을 찾을 수 없습니다. 다시 입력해주시길 바랍니다")
        file_path = input("Retry input file path : ")

if mode == summarize_logs:
    print_summary(context)

if mode == analyze_statistics:
    print_statistics(context)

if len(context["program_error"]) > 0:
    print("\n===== System Messages =====")
    print("잘못된 Log가 포함되어 있습니다.")
    print(f"문제 발생 Log 번호 : {context['program_error']}")