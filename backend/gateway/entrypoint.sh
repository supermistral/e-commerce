#!/bin/sh

GRPC_DIR="${GRPC_TOOLS_DIR:-./src/grpc_tools}"

export GRPC_TOOLS_DIR=${GRPC_DIR}
[ -d ${GRPC_DIR} ] || mkdir -p ${GRPC_DIR}

python -m grpc_tools.protoc \
    -I./proto \
    --python_out=${GRPC_DIR} \
    --pyi_out=${GRPC_DIR} \
    --grpc_python_out=${GRPC_DIR} \
    ./proto/**/*.proto

echo "\nThe files were generated in the path ${GRPC_DIR}"

exec "$@"