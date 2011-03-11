#!/bin/bash
set -e
sudo -u postgres dropdb traconkauppa
sudo -u postgres createdb -O traconkauppa -E UNICODE traconkauppa
