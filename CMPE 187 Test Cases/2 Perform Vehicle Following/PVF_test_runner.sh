#!/bin/sh

set -eu

python3 2_perform_vehicle_following_Close_Fast.py
python3 2_perform_vehicle_following_Close_Slow.py
python3 2_perform_vehicle_following_Unexp_Stop.py
python3 2_perform_vehicle_following_Stop_Go.py
# python3 2_perform_vehicle_following_Close_Fast.py
# python3 2_perform_vehicle_following_Close_Slow.py
# python3 2_perform_vehicle_following_Unexp_Stop.py
# python3 2_perform_vehicle_following_Stop_Go.py
