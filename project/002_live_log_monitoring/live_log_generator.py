import os
import json
import time
import argparse
from datetime import datetime

LOG_FORMAT = {
    "standard" : {
        "INFO" : "INFO This is a standard \"INFO\" Log.",
        "WARN" : "WARN This is a standard \"WARN\" Log.",
        "ERROR": "ERROR This is a standard \"ERROR\" Log.",
        500 : "ERROR 500 This is a standard \"ERROR code = 500\" Log.",
        404 : "ERROR 404 This is a standard \"ERROR code = 404\" Log.",
        "DB_CONN_FAIL" : "ERROR DB_CONN_FAIL This is a standard \"ERROR code = DB_CONN_FAIL\" Log.",
        "TIMEOUT" : "ERROR TIMEOUT This is a standard \"ERROR code = TIMEOUT\" Log."
    },
    "json" : [
            {
                "level" : "INFO",
                "message" : "This is a JSON 'INFO' Log."
            },
            {
                "level" : "WARN",
                "message" : "This is a JSON 'WARN' Log."
            },
            {
                "level" : "ERROR",
                "code" : 500,
                "message" : "This is a JSON 'ERROR code = 500' Log."
            },
            {
                "level" : "ERROR",
                "code" : 404,
                "message" : "This is a JSON 'ERROR code = 404' Log."
            },
            {
                "level" : "ERROR",
                "code" : "DB_CONN_FAIL",
                "message" : "This is a JSON 'ERROR code = DB_CONN_FAIL' Log."
            },
            {
                "level" : "ERROR",
                "code" : "TIMEOUT",
                "message" : "This is a JSON 'ERROR code = TIMEOUT' Log."
            }
        ],
    "apache" : {
        200 : "192.168.1.10 - - [08/Jun/2026:14:22:15 +0900] \"GET /index.html HTTP/1.1\" 200 1024",
        404 : "192.168.1.15 - - [08/Jun/2026:14:22:18 +0900] \"GET /favicon.ico HTTP/1.1\" 404 209",
        302 : "192.168.1.20 - - [08/Jun/2026:14:22:25 +0900] \"POST /login HTTP/1.1\" 302 512",
        403 : "192.168.1.30 - - [08/Jun/2026:14:22:40 +0900] \"GET /admin HTTP/1.1\" 403 128",
        500 : "192.168.1.35 - - [08/Jun/2026:14:22:45 +0900] \"POST /api/order HTTP/1.1\" 500 256",
    }
}

def create_log(log):
    path = os.path.dirname(__file__)

    play_count = 1
    log_list = log["log"] if ".jsonl" in log["log_path"] else list(log["log"].keys())
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(f"{path}/logs/{log["log_path"]}", "a") as file:
            if ".json" in log["log_path"]:
                log_line = log["log"][play_count-1].copy()
                log_line["time"] = now
                json.dump(log_line, file)
                file.write("\n")
                
            else:
                select_log = log["log"][log_list[play_count-1]]
                if "standard" in log["log_path"]:
                    file.write(f"{now} {select_log}\n")
                else:
                    file.write(f"{select_log}\n")

        play_count %= len(log_list)
        if play_count == 0:
            print("준비된 모든 Log가 출력되었습니다. 계속 진행하시겠습니까?")
            select = input("입력 (YES/NO) : ").lower()
            while select != "yes" and select != "no":
                print("잘못된 입력입니다. 다시 시도해주십시오.")
                select = input("입력 (YES/NO) : ").lower()
            if select == 'no':
                print("Log 출력 종료")
                break

        play_count += 1
        time.sleep(3)

def select_form(form):
    result = {}
    if form == "standard":
        result["log_path"] = "standard.log"

    elif form == "json":
        result["log_path"] = "json.jsonl"

    elif form == "apache":
        result["log_path"] = "apache.log"
    
    result["log"] = LOG_FORMAT[form]
    return result

parse = argparse.ArgumentParser(description="Saves the specified logs to a file sequentially according to the specified format.")
parse.add_argument("format", choices=["standard", "json", "apache"],
                   help="standard : This is the default option.\n" \
                        "json : This is an option for JSON logging.\n"
                        "apache : This is the Apache web server log style format.\n"
)

args = parse.parse_args()
form = select_form(args.format)
create_log(form)