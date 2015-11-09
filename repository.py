import re
import os
import git
from db import DB
import subprocess
import sqlite3

from git_map import GitMap

class Repository:
    def execute_cmd(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return process.communicate()[0].strip()
        
    def calc_branch_type(self, branch):
        for type, info in self.branch_regex.items():
            if info['regex'].search(branch):
                return type

    def __init__(self):
        self.repo = git.Repo(os.getcwd())
        
        self.branch_regex = {
            'bug': {
                'exp': '[bB][uU][gG]',
                'regex': re.compile('[bB][uU][gG]')
            },
            'wl': {
                'exp': '[wW][lL]',
                'regex': re.compile('[wW][lL]')
            }
        }

        self.repo_path = self.repo.working_dir
        self.repo_name = self.repo.working_dir.split('/')[-1]
        self.db = DB(os.path.dirname(os.path.realpath(__file__)) + '/' + self.repo_name + '.db')
        
        if self.db.is_new:
            self.git_map = GitMap()
            self.setup_repo_db()
        else:
            self.git_map = None
            
        self.load_current_branch()
            
    def setup_repo_db(self):
        for name, branch in self.git_map.branches.items():
            data = self.calculate_branch_details(name)
            self.register_branch(name, data['type'], data['last_remote_commit'])
            
    def clean_cache(self):
        try:
            self.db.clean
        except:
            print "Unable to clean cache. Plox delete manually: " + self.db_file_path

    def calculate_branch_details(self, branch_name):
        if not self.git_map:
            self.git_map = GitMap()
            self.clean_cache()
            self.setup_repo_db()
            
        branch = self.git_map.branches[branch_name]
        last_remote_commit = branch.fork
        
        type = self.calc_branch_type(branch_name)
            
        return {
            'name': branch,
            'last_remote_commit': last_remote_commit,
            'type': type
        }

    def calculate_current_branch_details(self):
        current_branch = self.repo.head.ref.name
        return self.calculate_branch_details(current_branch)

    def fetch_branch(self, branch):
        data = self.db.fetchone('branch', (branch,))

        if not data:
            return None
        else:
            return {
                'name': data[1],
                'last_remote_commit': data[2],
                'type': data[3]
            }

    def register_branch(self, branch, type, last_remote_commit):
        print "Registering branch " + branch
        self.db.insert('branch', (branch, last_remote_commit, type,))

    def unregister_branch(self, branch, type):
        print "Un-Registering branch " + branch
        self.db.delete('branch', (branch, type,))

    def load_current_branch(self):
        self.current_branch = self.repo.head.ref.name
        data = self.fetch_branch(self.current_branch)

        if not data:
            data = self.calculate_current_branch_details()

        self.branch_type = data['type']
        self.last_remote_commit = data['last_remote_commit']

    def checkout_to_branch(self, branch):
        try:
            info = self.repo.git.checkout(branch)
            print "Switched to branch " + branch + "\n" + info
        except git.exc.GitCommandError, e:
            print "ERROR: " + str(e)
            return False
        return True

    def new_branch(self, new_branch, type, parent_branch = None):
        if not parent_branch:
            parent_branch = self.current_branch
            
        if not self.has_upstream_branch(parent_branch):
            print "Cannot fork local branch from another local branch!"
            return
        
        if not self.checkout_to_branch(parent_branch):
            print "Unable to checkout to " + parent_branch
            return

        print "Creating new branch " + new_branch + " from " + parent_branch
        last_remote_commit = self.repo.head.ref.commit.hexsha
        try:
            self.repo.git.checkout('HEAD', b = new_branch)
            self.register_branch(new_branch, type, last_remote_commit)
            self.load_current_branch()
        except git.exc.GitCommandError, e:
            print "ERROR: " + str(e)

    def delete_branch(self, branch, type):
        if self.current_branch == branch:
            self.checkout_to_branch('master')
            
        try:
            self.repo.git.branch('-D', branch)
            self.unregister_branch(branch, type)
            print "Success"
        except git.exc.GitCommandError, e:
            print "ERROR: " + str(e)
            print "ERROR deleting " + branch

    def list_branches(self, type):
        branches = filter(lambda y: self.branch_regex[type]['regex'].search(y), map(lambda x: x.name, self.repo.heads))
        for branch in branches:
            if branch == self.current_branch:
                print '* ' + branch
            else:
                print branch

    def has_upstream_branch(self, branch):
        for remote in self.repo.remotes:
            for ref in remote.refs:
                if ref.name == remote.name + '/' + branch:
                    return  remote.name + '/' + branch
        return None
    
    def get_upstream_branch(self, branch):
        return self.repo.head.ref.tracking_branch().name
    
    def get_current_upstream_branch(self):
        return self.get_upstream_branch(self.current_branch)

    def current_has_upstream_branch(self):
        return self.has_upstream_branch(self.current_branch)

    # MAIN REPO FUNCTIONS:
    def checkout(self, data):
        branch = data[0]
        self.checkout_to_branch(branch)
        self.load_current_branch()

    def diff(self, data):
        if self.last_remote_commit:
            cmd = ['git', 'diff', self.last_remote_commit + '..']
        elif self.current_has_upstream_branch():
            cmd = ['git', 'diff', self.get_current_upstream_branch() + ".." + self.current_branch]
        else:
            cmd = ['git', 'diff']
        subprocess.call(cmd)
        
    def parent(self, data):
        print self.last_remote_commit

    def patch(self, data):
        if self.last_remote_commit:
            cmd = ['git', 'diff', self.last_remote_commit + '..']
        elif self.current_has_upstream_branch():
            cmd = ['git', 'diff', self.get_current_upstream_branch() + ".." + self.current_branch]
        else:
            cmd = ['git', 'diff']
        diff = self.execute_cmd(cmd)
        
        if diff == "":
            print "No Diff Bruh"
            return;
        
        try:
            patch_dir = self.repo_path + '/patches'
            patch_file = patch_dir + '/' + self.current_branch.split('/')[-1] + '.diff'
            if not os.path.exists(patch_dir):
                os.makedirs(patch_dir)
            
            file = open(patch_file, 'w+')
            file.write(diff)
        except:
            print "Error creating patch"
            
        print "Patch created at: " + patch_file
        
    def changes(self, data):
        if not self.last_remote_commit:
            cmd = ['git', 'diff', '--name-status']
        else:
            cmd = ['git', 'diff', '--name-status', self.last_remote_commit + '..']
        changes = self.execute_cmd(cmd)
        
        for change in sorted(changes.split('/n')):
            print change
    
    def clean(self, data):
        self.clean_cache()

    # WORKLOG FUNCTIONS:
    def list_worklogs(self, data):
        self.list_branches('wl')
        
    def delete_worklog(self, data):
        branch = data[0]
        self.delete_branch(branch, 'wl')
        
    def new_worklog(self, data):
        new_branch = data[0]
        
        if len(data) == 2:
            parent = data[1]
            self.new_branch(new_branch, 'wl', parent_branch = parent)
        else:
            self.new_branch(new_branch, 'wl')
        
    # BUG FUNCTIONS:
    
    def list_bugs(self, data):
        self.list_branches('bug')
        
    def delete_bug(self, data):
        branch = data[0]
        self.delete_branch(branch, 'bug')
        
    def new_bug(self, data):
        new_branch = data[0]
        
        if len(data) == 2:
            parent = data[1]
            self.new_branch(new_branch, 'bug', parent_branch = parent)
        else:
            self.new_branch(new_branch, 'bug')
    
