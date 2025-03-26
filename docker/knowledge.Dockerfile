# Context of build - project root

# --------------------------------------------
# Build
# --------------------------------------------
FROM python:3.11-slim AS builder
WORKDIR /build

# Updating pip and installing dependencies for build wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel build


# Building editable packages to wheel
COPY ./common/requirements.txt ./common/requirements.txt
RUN pip wheel --no-cache-dir -r ./common/requirements.txt -w /build/wheels

COPY ./common ./common
RUN cd common && python -m build && cd ..

# Building service requirements to wheel
COPY ./services/knowledge/requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt -w /build/wheels


# --------------------------------------------
# Run
# --------------------------------------------
FROM python:3.11-slim AS final
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip

# Installing wheels from build stage
COPY --from=builder /build/common/dist /tmp/wheels
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir /tmp/wheels/*.whl

COPY ./services/knowledge .

CMD ["python", "manage.py"]
