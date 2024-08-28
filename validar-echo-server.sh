#!/bin/bash

TEST_MESSAGE="Mensaje de prueba"

RESULT=$(docker run --rm --network tp0_testing_net busybox:latest sh -c "echo ${TEST_MESSAGE} | nc server 12345")

if [ "$RESULT" == "$TEST_MESSAGE" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
