#!/bin/sh

function __g() {
	local cur=${COMP_WORDS[COMP_CWORD]}
	local prev=${COMP_WORDS[COMP_CWORD-1]}
	local __bug_regex="[bB][uU][gG]"
  local __wl_regex="[wW][lL]"
  
  if [ "${COMP_WORDS[COMP_CWORD-3]}" == "new" ]; then
		COMPREPLY=( $(compgen -W "$(git branch | grep -v $__wl_regex | grep -v $__bug_regex | cut -c2-)" -- $cur) )
		return 0
	fi

	case "$prev" in
	"g")
		COMPREPLY=( $(compgen -W "checkout diff parent patch changes new delete list clean history" -- $cur) )
	;;
	"new" | "delete" | "list")
		COMPREPLY=( $(compgen -W "bug wl" -- $cur) )
	;;
	"checkout")
		COMPREPLY=( $(compgen -W "$(git branch | cut -c2-)" -- $cur) )
	;;
	"bug")
	  if [ "${COMP_WORDS[COMP_CWORD-2]}" != "new" ]; then
	    COMPREPLY=( $(compgen -W "$(git branch | grep -e $__bug_regex | cut -c2-)" -- $cur) )
	  fi
	;;
	"wl")
	  if [ "${COMP_WORDS[COMP_CWORD-2]}" != "new" ]; then
	    COMPREPLY=( $(compgen -W "$(git branch | grep -e $__wl_regex | cut -c2-)" -- $cur) )
	  fi
	;;
	*)
  ;;
	esac

}
complete -F __g g
