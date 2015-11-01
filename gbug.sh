#!/bin/sh

function __gbug() {
  curr_branch=$(git rev-parse --abbrev-ref HEAD)
  parent_branch=$(git show-branch -a 2>/dev/null | grep '\*' | grep -v "$curr_branch" | head -n1 | sed 's/.*\[\(.*\)\].*/\1/' | sed 's/[\^~].*//')
  local __bug_regex="[bB][uU][gG]#\?"

  case "$1" in
    "new")
      if [ "$2" != "" ]; then
        git checkout -b "$2" 2>/dev/null
        if [ $? -ne 0 ]; then
          echo "Bug $2 is alive!"
          git checkout "$2"
        else
          if [ "$3" != "" ]; then
            git config branch.$curr_branch.description "$3"
          fi
        fi
      else
        echo "Usage g bug new [branch]"
      fi
    ;;
    "delete")
      if [ "$2" != "" ]; then
        git checkout -d "$2" 2>/dev/null
        if [ $? -ne 0 ]; then
          echo "Bug $2 not found!"
          git checkout "$2"
        else
          echo "Bug $2 squashed!"
        fi
      else
        echo "Usage g bug delete [branch]"
      fi
    ;;
    "checkout")
      if [ "$2" != "" ]; then
  			git checkout "$2"
  		else
  			echo "Usage g bug checkout [branch]"
  		fi
    ;;
    "list")
      bugs=($(git branch | grep $__bug_regex | cut -c2-))
  		for bug in "${bugs[@]}"; do
  			num=$(grep -o "[0-9]\+$" <<< $bug)
  			desc=$(git config branch.$bug.description)
  			echo "BUG#$num: $desc"
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
