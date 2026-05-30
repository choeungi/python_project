import os
import sys
import re
from datetime import datetime

if len(sys.argv) < 3:
    print("사용법 : python log_librarian.py <파일경로> <옵션> <패턴>")
    exit()

def build_log_text(log: dict) -> str:
    return " ".join(log.values())

def parse_log_line(division: str) -> dict:
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

def filter_by_level(line: dict, context: dict):
    log_level = line["log_level"]
    if context["pattern"] == log_level:
        log_text = build_log_text()
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
        code = re.search(regex, log_text)
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
    search = re.search(context["pattern"], log_text)
    if search:
        print(f"[{context['line_num']}] {log_text}")

file_path = sys.argv[1]
option = sys.argv[2]

context = {}

if option == "-l":
    if len(sys.argv) < 4:
        print("-l 옵션 사용법: python log_librarian.py <파일경로> -l <로그레벨>")
        exit()
    mode = filter_by_level
    context["pattern"] = sys.argv[3].upper()
    
elif option == "-s":
    if len(sys.argv) >= 4:
        print("-s 옵션 사용법: python log_librarian.py <파일경로> -s")
        exit()
    mode = summarize_logs
    
    context["count"] = {
        "info_count": 0,
        "warn_count": 0,
        "error_count": 0
    }

elif option == "-t":
    if len(sys.argv) >= 4:
        print("-t 옵션 사용법: python log_librarian.py <파일경로> -t")
        exit()
    mode = analyze_statistics
    context["table"] = {}
    context["regex"] = re.compile(r"(?<=ERROR\s)\w+")

else:
    mode = search_logs
    context["pattern"] = re.compile(fr"{sys.argv[2]}", re.IGNORECASE)
    
with open(file_path, "r") as file:
    program_error = []
    for num, line in enumerate(file, start=1):
        line = parse_log_line(line)
        if line:
            context["line_num"] = num
            mode(line, context)
        else:
            program_error.append(num)

if mode == summarize_logs:
    print("===== 로그 요약 =====")
    print(f"INFO: {context['count']['info_count']}")
    print(f"WARN: {context['count']['warn_count']}")
    print(f"ERROR: {context['count']['error_count']}")

if mode == analyze_statistics:
    code_list = list(context["table"].keys())

    if not code_list:
        print("발생한 ERROR가 없습니다.")
        exit()
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

if len(program_error) > 0:
    print("\n===== System Messages =====")
    print("잘못된 Log가 포함되어 있습니다.")
    print(f"문제 발생 Log 번호 : {program_error}")
    