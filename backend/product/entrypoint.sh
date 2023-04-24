#!/bin/sh

if [ "$DATABASE_INIT" = "1" ]; then
    echo "Waiting for Database..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
        sleep 0.3
    done

    echo "Database started"

    if [ -n $DATABASE_INIT_COMMAND ]; then
        eval "$DATABASE_INIT_COMMAND"
    else
        echo -e "\nInit command is not found"
    fi
fi

GRPC_DIR="${GRPC_TOOLS_DIR:-./grpc_tools}"

[ -d ${GRPC_DIR} ] || mkdir -p ${GRPC_DIR}

python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./${GRPC_DIR} \
    --pyi_out=./${GRPC_DIR} \
    --grpc_python_out=./${GRPC_DIR} \
    ./proto/product.proto

echo -e "\nThe files were generated in the path ${GRPC_DIR}"

exec "$@"