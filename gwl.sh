#!/bin/sh

function __gwl() {
  curr_branch=$(git rev-parse --abbrev-ref HEAD)
  parent_branch=$(git show-branch -a 2>/dev/null | grep '\*' | grep -v "$curr_branch" | head -n1 | sed 's/.*\[\(.*\)\].*/\1/' | sed 's/[\^~].*//')
  local __wl_regex="[wW][lL]#\?"

  case "$1" in
    "new")
      git checkout master
      if [ "$2" != "" ]; then
        git checkout -b "$2" 2>/dev/null
        if [ $? -ne 0 ]; then
          echo "WL $2 is alive!"
          git checkout "$2"
        else
          if [ "$3" != "" ]; then
            git config branch.$curr_branch.description "$3"
          fi
        fi
      else
        echo "Usage g wl new [branch]"
      fi
    ;;
    "delete")
      if [ "$2" != "" ]; then
        git checkout -d "$2" 2>/dev/null
        if [ $? -ne 0 ]; then
          echo "wl $2 not found!"
          git checkout "$2"
        else
          echo "wl $2 squashed!"
        fi
      else
        echo "Usage g wl delete [branch]"
      fi
    ;;
    "checkout")
      if [ "$2" != "" ]; then
  			git checkout "$2"
  		else
  			echo "Usage g wl checkout [branch]"
  		fi
    ;;
    "list")
      wls=($(git branch | grep $__wl_regex | cut -c2-))
  		for wl in "${wls[@]}"; do
  			num=$(grep -o "[0-9]\+$" <<< $wl)
  			desc=$(git config branch.$wl.description)
  			echo "wl#$num: $desc"
  		done
    ;;
    "edit-description")
      if [ "$3" != "" ]; then
        git config branch.$2.description "$3"
      else
        git config branch.$curr_branch.description "$2"
      fi
    ;;
    "show-description")
      git config branch.$curr_branch.description
    ;;
    "*")
    ;;
  esac
}
