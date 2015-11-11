#!/bin/sh

function __g() {
	local cur=${COMP_WORDS[COMP_CWORD]}
	local prev=${COMP_WORDS[COMP_CWORD-1]}
	local __bug_regex="[bB][uU][gG]"
  local __wl_regex="[wW][lL]"

	case "$prev" in
	"g")
		COMPREPLY=( $(compgen -W "checkout diff parent patch changes bug wl clean history" -- $cur) )
	;;
	"bug" | "wl")
		COMPREPLY=( $(compgen -W "new delete list" -- $cur) )
	;;
	"delete")
		if [ "${COMP_WORDS[COMP_CWORD-2]}" == "bug" ]; then
			COMPREPLY=( $(compgen -W "$(git branch | grep -e $__bug_regex | cut -c2-)" -- $cur) )
		elif [ "${COMP_WORDS[COMP_CWORD-2]}" == "wl" ]; then
			COMPREPLY=( $(compgen -W "$(git branch | grep -e $__wl_regex | cut -c2-)" -- $cur) )
		fi
	;;
	"checkout")
		COMPREPLY=( $(compgen -W "$(git branch | cut -c2-)" -- $cur) )
	;;
	*)
		if [ "${COMP_WORDS[COMP_CWORD-2]}" == "new" ]; then
			COMPREPLY=( $(compgen -W "$(git branch | grep -v $__wl_regex | grep -v $__bug_regex | cut -c2-)" -- $cur) )
		fi
  ;;
	esac

}
complete -F __g g
