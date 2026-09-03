FROM python:3.14-bookworm AS python-base

# python
# ENV variables are also available in the later build stages
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # uv
    # https://docs.astral.sh/uv/reference/environment/
    # compile bytecode during installation for faster startup
    UV_COMPILE_BYTECODE=1 \
    # copy packages from the cache mount instead of hard linking them
    UV_LINK_MODE=copy \
    # use the Python of the base image instead of downloading one
    UV_PYTHON_DOWNLOADS=never \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    \
    # dagster
    # where our code is stored
    DAGSTER_APP=/opt/dagster/app/


# prepend venv to path
ENV PATH="$VENV_PATH/bin:$PATH"


# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base AS builder-base

# install uv by copying the binary from the official image
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /bin/

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY pyproject.toml uv.lock ./

# install runtime deps into the virtual environment (`.venv` inside $PYSETUP_PATH),
# the project itself is not installed as it is provided by $DAGSTER_APP at runtime
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project


# `development` image is used during development / testing
FROM python-base AS development
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /bin/
WORKDIR $PYSETUP_PATH

# copy in our built venv
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# will become mountpoint of our code
WORKDIR $DAGSTER_APP


# `production` image used for runtime
FROM python-base AS production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Copy our code into the image
COPY . $DAGSTER_APP

WORKDIR $DAGSTER_APP
