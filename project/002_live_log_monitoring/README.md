# Sensor Light

CLI 기반으로 실시간으로 발생되는 Log를 효율적으로 모니터링 하기 위한 도구입니다.

## Overview

Sensor Light는 Python으로 구현한 실시간 로그 모니터링 프로그램입니다.

tail -f 방식으로 로그 파일의 변경을 감시하며,
여러 로그 포맷을 동일한 인터페이스로 분석하도록 설계했습니다.

지원 포맷

- Standard Log
- JSON Log (JSONL)
- Apache Access Log

## Purpose

이 프로젝트는 다음 기술을 학습하기 위해 제작했습니다.

- 실시간 파일 모니터링
- 로그 파싱
- 정규표현식 활용
- argparse 기반 CLI 제작
- 여러 로그 포맷을 하나의 구조로 처리하는 Parser 설계

## Features

- 새로 추가되는 로그를 실시간으로 모니터링 (tail -f 방식)
- 다양한 로그 형식 지원 (Standard, JSONL, Apache)
- ERROR 로그만 출력 및 각 ERROR CODE 개수 집계 (--error-only)
- 각 Log Level 별 통계를 주기적으로 출력 (INFO, WARN, ERROR)

## Project 
```
002_live_log_monitoring
├── logs
│   ├── apache.log
│   ├── json.jsonl
│   └── standard.log
├── README.md
├── live_log_generator.py
└── sensor_light.py
```

## 사용법
### Normal Mode
```bash
python sensor_light.py logs/standard.log
```

### 출력
```text
2026-06-30 14:38:21 INFO This is a standard "INFO" Log.
2026-07-01 14:28:08 ERROR 404 This is a standard "ERROR code = 404" Log.
```
#### 10초마다 출력
```text
===== Statistics =====
INFO : 1
WARN : 0
ERROR : 1
======================
```

### Error Only Mode
```bash
python sensor_light.py standard.log --error-only
```
### 출력
```text
2026-07-01 14:26:30 ERROR 500 This is a standard "ERROR code = 500" Log
2026-07-01 14:26:39 ERROR TIMEOUT This is a standard "ERROR code = TIMEOUT" Log.
```
#### 10초마다 출력
```text
===== Error Code =====
500  : 1
TIMEOUT  : 1
======================
```

## Design

### 1. 각 로그 포맷마다 Parser를 별도의 함수로 분리

- parse_standard_log()

- parse_json_log()

- parse_apache_log()

각 로그 포맷마다 별도의 Parser 함수를 구현했습니다.

새로운 로그 포맷을 지원할 때는 기존 코드를 수정하지 않고 새로운 Parser만 추가하면 되도록 설계했습니다.

이를 통해 monitor_log()는
로그 형식과 관계없이 동일한 인터페이스로 Parser를 호출할 수 있도록 설계했습니다.

### 2. HTTP Status Code 활용
Apache 로그는 Log Level(INFO/WARN/ERROR) 대신 HTTP Status Code를 사용하기 때문에 로그 통계를 수집하는데 어려움이 있었습니다.

따라서

- 100~299 → INFO

- 300~399 → WARN

- 400~599 → ERROR

로 변환하여 프로그램 내부에서 동일한 방식으로 처리했습니다.

## What I Learned

이번 프로젝트를 통해 다음 내용을 배웠습니다.

- 서로 다른 로그 포맷을 동일한 인터페이스로 처리하는 설계의 중요성
- 정규표현식을 활용하여 위치가 다른 데이터를 추출하는 방법
- 실시간 파일 모니터링(tail -f 방식)의 동작 원리


## Future Work

- Docker json-file 로그 포맷 지원
- Nginx Access Log 지원
- MySQL Log 지원
- 로그 필터 옵션 추가