#!/bin/sh

function __g() {
	local cur=${COMP_WORDS[COMP_CWORD]}
	local prev=${COMP_WORDS[COMP_CWORD-1]}
	local __bug_regex="[bB][uU][gG]#\?"
  local __wl_regex="[wW][lL]#\?"

	case "$prev" in
	"g")
		COMPREPLY=( $(compgen -W "checkout diff parent patch changes bug wl" -- $cur) )
	;;
	"bug" | "wl")
		COMPREPLY=( $(compgen -W "new delete list" -- $cur) )
	;;
	"delete")
    if [ "${COMP_WORDS[COMP_CWORD-2]}" == "bug" ]; then
      COMPREPLY=( $(compgen -W "$(git branch | grep $__bug_regex | cut -c2-)" -- $cur) )
    fi
	;;
	*)
  ;;
	esac

}
complete -F __g g
