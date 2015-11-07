import sys
import subprocess
from repository import Repository

status = subprocess.call(["git", "status"], stdout=subprocess.PIPE)
if status != 0:
    print "Not a Git repo!"
    exit()

repo = Repository()

bug_options = {
    'new': repo.new_bug,
    'delete': repo.delete_bug,
    'list': repo.list_bugs
}

worklog_options = {
    'new': repo.new_worklog,
    'delete': repo.delete_worklog,
    'list': repo.list_worklogs
}

main_options = {
    'checkout': repo.checkout,
    'diff': repo.diff,
    'patch': repo.patch,
    'parent': repo.parent,
    'changes': repo.changes,
    'clean': repo.clean
}

if(sys.argv[1] == 'bug'):
    bug_options[sys.argv[2]](sys.argv[3:])
elif(sys.argv[1] == 'wl'):
    worklog_options[sys.argv[2]](sys.argv[3:])
else:
    main_options[sys.argv[1]](sys.argv[2:])