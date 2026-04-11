# Python 3.12 (ARM64 지원)
FROM python:3.12-slim

# uv 설치를 위한 바이너리 복사 (공식 권장 방식)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 바이트코드 생성을 억제하여 이미지 용량 최적화 및 런타임 성능 유지
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 의존성 파일 복사 (uv.lock이 있다면 함께 복사)
COPY pyproject.toml uv.lock* ./

# 의존성 설치
# --system: 컨테이너 시스템 환경에 직접 설치 (가상환경 생략)
# --frozen: uv.lock 파일의 내용과 일치하도록 강제
# --no-cache: 이미지 레이어 최적화를 위해 캐시 삭제
RUN uv sync --frozen --no-cache --non-interactive --system

# Django 소스 코드 복사
COPY . .

# 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 컨테이너가 시작될 때 실행될 명령어 정의 (Gunicorn) : 워커의 갯수는 일반적으로 [CPU 코어 수 × 2 + 1] 공식을 사용한다고 함.
CMD ["gunicorn", "blog_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-level", "debug", "--error-logfile", "-"]