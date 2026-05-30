import os
import sys
import re
from collections import Counter

if len(sys.argv) < 3:
    print("사용법 : python log_librarian.py <파일경로> <옵션> <패턴>")
    exit()

file_path = sys.argv[1]
option = sys.argv[2]

if option == "-l":
    if len(sys.argv) < 4:
        print("-l 옵션 사용법: python log_librarian.py <파일경로> -l <로그레벨>")
        exit()
    mode = "level"
    pattern = sys.argv[3].upper()
elif option == "-s":
    if len(sys.argv) >= 4:
        print("-s 옵션 사용법: python log_librarian.py <파일경로> -s")
        exit()
    mode = "summary"
elif option == "-t":
    if len(sys.argv) >= 4:
        print("-t 옵션 사용법: python log_librarian.py <파일경로> -t")
        exit()
    mode = "statistics"
    statistic_regex = re.compile(r"(?<=ERROR\s)\w+")
else:
    mode = "search"
    search_regex = re.compile(fr"{sys.argv[2]}", re.IGNORECASE)
    
info_count = 0
warn_count = 0
error_count = 0

with open(file_path, "r") as file:
    table = {}
    for num, line in enumerate(file, start=1):
        line = line.strip()
        if mode == "search":
            search = re.search(search_regex, line)
            if search:
                print(f"[{num}] {line}")
        
        parts = line.split()
        if len(parts) > 2:
            level = parts[2]
            if mode == "level" and pattern == level:
                print(f"[{num}] {line}")
            if level == "INFO":
                info_count += 1
            elif level == "WARN":
                warn_count += 1
            elif level == "ERROR":
                error_count += 1

                if mode == "statistics":
                    code = re.search(statistic_regex, line)
                    if not code:
                        table["UNKNOWN"] = table["UNKNOWN"] + 1 if "UNKNOWN" in table else 1
                        continue
                    code = code.group()
                    if code not in table:
                        table[code] = 1
                    else:
                        table[code] += 1

    if mode == "summary":
        print("===== 로그 요약 =====")
        print(f"INFO: {info_count}")
        print(f"WARN: {warn_count}")
        print(f"ERROR: {error_count}")
    
    if mode == "statistics":
        code_list = list(table.keys())

        if not code_list:
            print("발생한 ERROR가 없습니다.")
            exit()
        else:
            rank = sorted(table.items(), key=lambda x: x[1], reverse=True)
            max_value = max(table.values())

            print("===== ERROR 코드 통계 =====")
            for result in range(min(5, len(rank))):
                print(f"{rank[result][0]} : {table[rank[result][0]]}")
            
            print("\n가장 많이 발생한 에러: ")
            for most in rank:
                if table[most[0]] == max_value:
                    print(f"{most[0]} ({table[most[0]]}회)")

            if len(rank) > 5:
                print(f"\n기타 {len(rank) - 5}개 에러 코드 존재")
        


