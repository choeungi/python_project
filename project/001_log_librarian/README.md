# Log Librarian

CLI 기반 로그 분석 도구로, 로그 검색·레벨 필터링·통계 분석 기능을 제공합니다.
(DevOps 환경에서 로그 기반 시스템 모니터링과 분석 과정을 학습하기 위해 제작한 프로젝트입니다.)

## 주요 기능

### Search
정규표현식을 사용하여 특정 패턴이 포함된 로그를 검색합니다.

### Level Filter
지정한 Log Level(INFO, WARN, ERROR)에 해당하는 로그만 필터링하여 출력합니다.

### Summary
각 Log Level의 총 발생 횟수를 집계하여 요약 정보를 출력합니다.

### Statistics
ERROR 로그의 코드를 분석하여 코드별 발생 횟수와 가장 많이 발생한 ERROR를 출력합니다.  
ERROR 코드가 많을 경우 상위 항목만 출력하고 나머지는 요약하여 표시합니다.

## 사용 방법

```bash
python txt_log_reader.py <파일경로> <옵션> <패턴 또는 Log Level>
```

### 인자 설명

#### `<파일경로>`

분석할 로그 파일의 경로

#### `<옵션>`

* `[미지정] <패턴>`

  * 정규표현식을 사용한 로그 검색

* `-l <Log Level>`

  * 지정한 Log Level에 해당하는 로그 출력

* `-s`

  * Log Level별 발생 횟수 요약

* `-t`

  * ERROR 코드 통계 정보 출력

### Search 패턴 예시

```text
ERROR
ERROR \d+
\d+
```
## 실행 예시

### Search
정규표현식을 사용하여 특정 패턴의 로그를 검색합니다.

#### 입력

```bash
python log_librarian.py sample.log "ERROR \d+"
```

#### 출력

```text
[3] 2026-04-27 09:02:33 ERROR 500 /api/user
[4] 2026-04-27 09:03:45 ERROR 404 /api/login
[6] 2026-04-27 09:05:17 ERROR 500 /api/order
[11] 2026-04-27 09:10:22 ERROR 403 /api/admin
[12] 2026-04-27 09:11:35 ERROR 500 /api/payment
[16] 2026-04-27 09:15:23 ERROR 404 /api/product
[19] 2026-04-27 09:18:55 ERROR 500 /api/cart
```


### Level Filter

#### 입력

```bash
python log_librarian.py sample.log -l ERROR
```

#### 출력

```text
[3] 2026-04-27 09:02:33 ERROR 500 /api/user
[4] 2026-04-27 09:03:45 ERROR 404 /api/login
[6] 2026-04-27 09:05:17 ERROR 500 /api/order
[8] 2026-04-27 09:07:40 ERROR DB_CONN_FAIL Database connection failed
[9] 2026-04-27 09:08:55 ERROR TIMEOUT External API timeout
[11] 2026-04-27 09:10:22 ERROR 403 /api/admin
[12] 2026-04-27 09:11:35 ERROR 500 /api/payment
[14] 2026-04-27 09:13:59 ERROR
[16] 2026-04-27 09:15:23 ERROR 404 /api/product
[17] 2026-04-27 09:16:37 ERROR DB_CONN_FAIL Retry failed
[19] 2026-04-27 09:18:55 ERROR 500 /api/cart
[21] 2026-04-27 09:13:59 ERROR
```

### Summary

#### 입력

```bash
python log_librarian.py sample.log -s
```

#### 출력

```text
===== 로그 요약 =====
INFO: 5
WARN: 4
ERROR: 12
```

### Statistics
ERROR 코드는 발생 횟수 기준으로 정렬됩니다.

#### 입력

```bash
python log_librarian.py sample.log -t
```

#### 출력
```text
===== ERROR 코드 통계 =====
500 : 4
404 : 2
DB_CONN_FAIL : 2
UNKNOWN : 2
TIMEOUT : 1

가장 많이 발생한 에러: 
500 (4회)

기타 1개 에러 코드 존재
```

## Log 형식
<날짜> <시간> <Log Level> <Code> <Message>

## 배운점
* CLI 기반 도구를 만드는 방법
  * sys.argv 을 사용하여 터미널에서 입력한 인자값을 다룰 수 있게 되었습니다
* 프로그램에서 기능을 분리하는 방법
  * 프로그램의 기능을 역할별로 분리하며 코드 구조를 설계하는 방법을 익혔습니다.
* regex (정규표현식)
  * 정규표현식의 패턴과 사용 방법을 터득하며 더 높은 수준의 문자열 검색을 할 수 있게 되었습니다.
* 시스템 자원의 I/O 효율을 고려하여 프로그램을 설계 하는 법
  * 로그 파일 전체를 메모리에 올리지 않고 한 줄씩 읽어 처리하며 I/O 및 메모리 사용 효율을 고려하는 방법을 익혔습니다.

## 한계
1. 특정 Log 형식에 의존하기 때문에 다양한 로그를 읽지는 못합니다.
2. 현재는 Text 기반 로그 파일만 지원하여 확장성이 부족합니다.

## 개선 방향
1. JSON 로그 파일 또한 지원할 수 있도록 만들어 해당 프로그램의 한계를 극복할 수 있도록 합니다.
2. regex를 확장하여 더 복잡한 로그 또한 분석 할 수 있도록 합니다.
3. 시간 기반으로 Log를 분석하여 기간 별로 정리하거나 최근 발생한 Log만 출력 할 수 있도록 합니다.
4. 선택한 옵션에 필요한 로직만 실행되도록 구조를 개선하여 프로그램의 효율성을 높일 예정입니다.