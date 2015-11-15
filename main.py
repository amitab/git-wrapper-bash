import sys
import subprocess
from repository import Repository

status = subprocess.call(["git", "status"], stdout=subprocess.PIPE)
if status != 0:
    print "Not a Git repo!"
    exit()

repo = Repository()

main_options = {
    'checkout': repo.checkout,
    'diff': repo.diff,
    'patch': repo.patch,
    'parent': repo.parent,
    'changes': repo.changes,
    'clean': repo.clean,
    'history': repo.history,
    'new': repo.new_custom,
    'delete': repo.delete_custom,
    'list': repo.list_custom
}

main_options[sys.argv[1]](sys.argv[2:])