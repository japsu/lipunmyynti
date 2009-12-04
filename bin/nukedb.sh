#!/bin/bash
set -e
dropdb -U tracon_dev tracon_dev
createdb -U tracon_dev -E UNICODE tracon_dev
