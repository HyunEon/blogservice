# 사용할 Python은 3.12 (ARM64 아키텍처 지원)
FROM python:3.12-slim

# 컨테이너 내에서 작업할 디렉토리 설정
WORKDIR /app

# pipenv 설치
RUN pip install pipenv

# Pipfile과 Pipfile.lock 복사
COPY Pipfile* ./

# Pipenv 사용하여 의존성 설치
# --deploy: Pipfile.lock 기준으로 설치하여 일관성 확보
# --system: 컨테이너의 기본 Python 환경에 바로 설치 (가상 환경 생성 방지)
RUN pipenv install --deploy --system

# static collect
RUN python manage.py collectstatic --noinput

# 현재 Django 프로젝트 소스 코드 전체를 컨테이너 안으로 복사
COPY . .

# 컨테이너가 시작될 때 실행될 명령어 정의 (Gunicorn) : 워커의 갯수는 일반적으로 [CPU 코어 수 × 2 + 1] 공식을 사용한다고 함.
CMD ["gunicorn", "blog_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]