#!/bin/sh

set -eu

python3 1_merging_into_traffic_morning_clear.py
python3 1_merging_into_traffic_morning_congested.py
python3 1_merging_into_traffic_rainy_congested.py
python3 1_merging_into_traffic_night_congested.py
# python3 1_merging_into_traffic_morning_clear.py
# python3 1_merging_into_traffic_morning_congested.py
# python3 1_merging_into_traffic_rainy_congested.py
# python3 1_merging_into_traffic_night_congested.py
