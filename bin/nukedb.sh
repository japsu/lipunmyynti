#!/bin/bash
echo "Ei nuketeta tietokantaa."
exit 1

set -e
sudo -u postgres dropdb traconkauppa
sudo -u postgres createdb -O traconkauppa -E UNICODE traconkauppa
