#!/bin/sh

function __g() {
	local cur=${COMP_WORDS[COMP_CWORD]}
	local prev=${COMP_WORDS[COMP_CWORD-1]}
	local __bug_regex="[bB][uU][gG]#\?"

	case "$prev" in
	"g")
		COMPREPLY=( $(compgen -W "diff patch bug update undo-update changes parent" -- $cur) )
	;;
	"bug")
		COMPREPLY=( $(compgen -W "new delete checkout list edit-description show-description" -- $cur) )
	;;
	"checkout" | "delete")
    if [ "${COMP_WORDS[COMP_CWORD-2]}" == "bug" ]; then
      COMPREPLY=( $(compgen -W "$(git branch | grep $__bug_regex | cut -c2-)" -- $cur) )
    fi
	;;
	"edit-description")
    if [ "${COMP_WORDS[COMP_CWORD-2]}" == "bug" ]; then
      COMPREPLY=( $(compgen -W "$(git branch | grep $__bug_regex | cut -c2-)" -- $cur) )
    fi
	;;
	*)
  ;;
	esac

}
complete -F __g g
