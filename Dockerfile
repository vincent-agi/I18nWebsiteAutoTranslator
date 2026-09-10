# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13

# ---- builder ---------------------------------------------------------------
# Builds the package into an isolated venv that the runtime stage copies as-is.
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /src
# Only the files hatchling needs to build the wheel (see pyproject.toml).
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install . \
    && find /opt/venv -name '__pycache__' -type d -prune -exec rm -rf {} + \
    && find /opt/venv -name 'tests' -type d -prune -exec rm -rf {} +

# ---- runtime -------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL org.opencontainers.image.title="i18n-translator" \
      org.opencontainers.image.description="Translate JSON i18n files with the DeepL API, keeping the key structure intact." \
      org.opencontainers.image.source="https://github.com/vincent-agi/I18nWebsiteAutoTranslator" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /opt/venv /opt/venv

# Non-root by default; /work is the bind-mount point for the JSON files.
RUN useradd --create-home --user-group --uid 10001 app \
    && mkdir /work && chown app:app /work
USER app
WORKDIR /work

ENTRYPOINT ["i18n-translate"]
CMD ["--help"]
