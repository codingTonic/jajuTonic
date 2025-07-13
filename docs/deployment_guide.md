# AWS Elastic Beanstalk 배포 가이드

이 문서는 Flask 애플리케이션을 AWS Elastic Beanstalk(EB)에 배포하는 과정을 안내합니다.

## 목차
1.  [사전 준비물](#1-사전-준비물)
2.  [AWS CLI 및 EB CLI 설치](#2-aws-cli-및-eb-cli-설치)
3.  [프로젝트 배포 준비](#3-프로젝트-배포-준비)
4.  [EB 애플리케이션 초기화](#4-eb-애플리케이션-초기화)
5.  [EB 환경 생성](#5-eb-환경-생성)
6.  [환경 변수 설정](#6-환경-변수-설정)
7.  [애플리케이션 배포](#7-애플리케이션-배포)
8.  [로그 확인 및 문제 해결](#8-로그-확인-및-문제-해결)

---

### 1. 사전 준비물
-   AWS 계정
-   IAM 사용자 (EB 및 관련 서비스에 대한 권한 보유)
-   Python 및 pip 설치
-   Git 설치

### 2. AWS CLI 및 EB CLI 설치

**AWS CLI 설치**
```bash
pip install awscli
```

**AWS CLI 설정**
AWS IAM 사용자의 `Access Key ID`와 `Secret Access Key`를 사용하여 AWS CLI를 설정합니다.
```bash
aws configure
```
-   `AWS Access Key ID`: [Your Access Key]
-   `AWS Secret Access Key`: [Your Secret Key]
-   `Default region name`: [e.g., ap-northeast-2]
-   `Default output format`: [e.g., json]

**EB CLI 설치**
```bash
pip install awsebcli --upgrade
```

### 3. 프로젝트 배포 준비
-   `requirements.txt` 파일 생성 (완료)
-   `app.py` -> `application.py` 이름 변경 (완료)
-   `gunicorn` 추가 (완료)
-   `.gitignore` 파일 생성 (완료)

### 4. EB 애플리케이션 초기화

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 EB 애플리케이션을 초기화합니다.
```bash
eb init -p python-3.9 <your-application-name>
```
-   `<your-application-name>`을 원하는 애플리케이션 이름으로 변경하세요 (예: `saju-analyzer`).
-   리전 선택, 애플리케이션 이름 입력 등의 과정을 안내에 따라 진행합니다.
-   SSH 키 관련 질문에는 `y`를 선택하고 키 페어를 생성하거나 기존 키를 선택하는 것이 좋습니다 (추후 서버 직접 접속에 필요).

### 5. EB 환경 생성

다음 명령어로 배포 환경을 생성합니다. 환경 이름은 URL에 포함됩니다.
```bash
eb create <your-environment-name>
```
-   `<your-environment-name>`을 원하는 환경 이름으로 변경하세요 (예: `saju-analyzer-prod`).
-   이 과정은 약 5-10분 정도 소요됩니다. AWS에서 필요한 리소스(EC2 인스턴스, 보안 그룹 등)를 생성합니다.
-   완료되면 `CNAME` URL이 출력되며, 이 주소로 애플리케이션에 접속할 수 있습니다.

### 6. 환경 변수 설정

보안에 민감한 정보들(API 키, 비밀번호 등)은 코드가 아닌 EB 환경 변수로 설정해야 합니다.

1.  **AWS 콘솔 접속**: Elastic Beanstalk 서비스 페이지로 이동합니다.
2.  **환경 선택**: 생성된 환경(예: `saju-analyzer-prod`)을 클릭합니다.
3.  **구성(Configuration)**: 왼쪽 메뉴에서 `구성`을 클릭합니다.
4.  **소프트웨어(Software)** 카테고리에서 `편집(Edit)`을 클릭합니다.
5.  **환경 속성(Environment properties)** 섹션으로 스크롤합니다.
6.  다음 환경 변수들을 추가합니다:
    -   `SECRET_KEY`: Flask 세션 및 CSRF 보호에 사용할 강력한 비밀 키
    -   `GMAIL_ADDRESS`: 이메일 전송에 사용할 Gmail 주소
    -   `GMAIL_APP_PASSWORD`: Gmail 앱 비밀번호 (16자리)
    -   `OPENAI_API_KEY`: OpenAI API 키
7.  페이지 하단의 `적용(Apply)` 버튼을 클릭하여 변경 사항을 저장합니다. (환경 업데이트에 몇 분 소요)

### 7. 애플리케이션 배포

로컬에서 코드를 수정한 후, 다음 명령어로 간단하게 배포할 수 있습니다.
```bash
eb deploy
```
-   `git`으로 관리되는 파일들이 압축되어 EB 환경에 업로드되고, 새로운 버전으로 애플리케이션이 재시작됩니다.

### 8. 로그 확인 및 문제 해결

배포 후 문제가 발생하면 로그를 확인하여 원인을 파악할 수 있습니다.

**실시간 로그 스트리밍**
```bash
eb logs --stream
```

**최근 100줄 로그 확인**
```bash
eb logs
```

**웹 서버(nginx/apache) 로그 확인**
-   `/var/log/nginx/access.log`
-   `/var/log/nginx/error.log`

**애플리케이션 로그 확인**
-   `/var/log/web.stdout.log` (Gunicorn 및 애플리케이션 출력)

**"502 Bad Gateway" 오류 발생 시**
-   가장 흔한 오류 중 하나로, 애플리케이션이 정상적으로 시작되지 못했다는 의미입니다.
-   `web.stdout.log`를 확인하여 파이썬 코드 오류나 라이브러리 설치 문제를 파악해야 합니다.
-   `requirements.txt`에 모든 라이브러리가 포함되었는지 다시 한번 확인하세요.

---

이제 이 가이드에 따라 AWS에 애플리케이션을 성공적으로 배포할 수 있습니다. 