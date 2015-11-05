#!/bin/sh

curr_dir="$(dirname ${BASH_SOURCE[0]})"

source "$curr_dir/autocomplete.sh"
alias g="python $curr_dir/main.py"
