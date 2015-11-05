#!/bin/sh

function g() {
	curr_branch=$(git rev-parse --abbrev-ref HEAD)
	parent_branch=$(git show-branch -a 2>/dev/null | grep '\*' | grep -v "$curr_branch" | head -n1 | sed 's/.*\[\(.*\)\].*/\1/' | sed 's/[\^~].*//')
	
	parent_branch=${parent_branch#origin/}

  case "$1" in
  "parent")
    echo $parent_branch
  ;;
  "diff")
    git diff $parent_branch..$curr_branch
  ;;
  "patch")
		mkdir patches &>/dev/null
		default=${curr_branch##*/}
    if [ "$2" != "" ]; then
      git diff $parent_branch..$curr_branch > patches/$2.diff
    else
      git diff $parent_branch..$curr_branch > patches/$default.diff
    fi
  ;;
  "bug")
    __gbug "${@:2}"
  ;;
  "wl")
    __gwl "${@:2}"
  ;;
  "undo-update")
    git merge --abort
  ;;
  "update")
    git checkout $parent_branch
	git pull
	git checkout $curr_branch
	git merge $parent_branch
  ;;
  "undo-update")
    git merge --abort
  ;;
	"changes")
		git diff --name-status $parent_branch..$curr_branch | sort -k1
	;;
  *)
  echo "usage: g diff
         g patch [patch file name]
         g bug [arguments]

  [arguments]
    g bug new [branch name] [branch description]
    g bug [delete | checkout] [branch name]
    g bug [list | show-description | edit-description | update | undo-update]"
  ;;
	esac
}
