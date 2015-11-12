import re
import os
import git
import subprocess
import sqlite3

from db import DB
from git_map import GitMap
from git_map import Branch

class Repository:
    def execute_cmd(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return process.communicate()[0].strip()

    def __init__(self):
        self.repo = git.Repo(os.getcwd())

        self.repo_path = self.repo.working_dir
        self.repo_name = self.repo.working_dir.split('/')[-1]
        self.db = DB(os.path.dirname(os.path.realpath(__file__)) + '/' + self.repo_name + '.db')
        self.git_map = GitMap(self.repo)
        
        if self.db.is_new:
            self.git_map.build_branch_map()
            self.setup_repo_db()
            
        self.load_current_branch()
            
    def setup_repo_db(self):
        for name, branch in self.git_map.branches.items():
            data = self.calculate_branch_details(name)
            
    def clean_cache(self):
        try:
            self.db.clean()
        except:
            print "Unable to clean cache. Plox delete manually: " + self.db_file_path
            
    def get_branch_by_name(self, name):
        if name in self.git_map.branches:
            return self.git_map.branches[name]
        else:
            return None
            
    def get_ref_by_name(self, name):
        if name in self.repo.refs:
            return self.repo.refs[name]
        else:
            return None

    def calculate_branch_details(self, branch_name):
        if not self.git_map.map_build:
            self.git_map.build_branch_map()
            
        branch = self.get_branch_by_name(branch_name)
        
        if branch:
            branch.register(self.db)
            return branch
        else:
            return None

    def calculate_current_branch_details(self):
        current_branch = self.repo.head.ref.name
        return self.calculate_branch_details(current_branch)

    def fetch_branch(self, branch_name):
        data = self.db.fetchone('branch', (branch_name,))

        if not data:
            return None
        else:
            branch = self.get_branch_by_name(branch_name)
            branch.fork = data[2]
            return branch

    def load_current_branch(self):
        self.current_branch = self.repo.head.ref.name
        data = self.fetch_branch(self.current_branch)

        if not data:
            data = self.calculate_current_branch_details()
            
        self.branch = data

    def checkout_to_branch(self, branch):
        try:
            info = self.repo.git.checkout(branch.name)
            print "Switched to branch " + branch.name + "\n" + info
        except git.exc.GitCommandError, e:
            print "ERROR: " + str(e)
            return False
        return True

    def new_branch(self, new_branch, type, parent_branch = None):
        if not parent_branch:
            parent_branch = self.branch
            
        if not parent_branch.has_upstream_branch:
            print "Cannot fork local branch from another local branch!"
            return
        
        if not self.checkout_to_branch(parent_branch):
            print "Unable to checkout to " + parent_branch.name
            return

        print "Creating new branch " + new_branch + " from " + parent_branch.name

        try:
            self.repo.git.checkout('HEAD', b = new_branch)
            self.load_current_branch()
        except git.exc.GitCommandError, e:
            print "ERROR: " + str(e)

    def delete_branch(self, branch, type):
        if self.branch.name == branch.name:
            self.checkout_to_branch(self.get_branch_by_name('master'))
            
        try:
            self.repo.git.branch('-D', branch.name)
            branch.unregister(self.db)
            print "Success"
        except git.exc.GitCommandError, e:
            print "ERROR: " + str(e)
            print "ERROR deleting " + branch

    def list_branches(self, type):
        branches = filter(lambda y: y.type == type, self.git_map.branches.values())
        for branch in branches:
            if not branch.is_remote_branch():
                if branch.name == self.branch.name:
                    print '* ' + branch.name
                else:
                    print branch.name

    # MAIN REPO FUNCTIONS:
    def checkout(self, data):
        branch = self.get_branch_by_name(data[0])
        self.checkout_to_branch(branch)
        self.load_current_branch()

    def diff(self, data):
        if self.branch.fork:
            cmd = ['git', 'diff', self.branch.fork + '..']
        elif self.branch.has_upstream_branch:
            cmd = ['git', 'diff', self.branch.get_upstream_branch_name() + ".." + self.branch.name]
        else:
            cmd = ['git', 'diff']
        subprocess.call(cmd)
        
    def parent(self, data):
        print self.branch.fork

    def patch(self, data):
        if self.branch.fork:
            cmd = ['git', 'diff', self.branch.fork + '..']
        elif self.branch.has_upstream_branch:
            cmd = ['git', 'diff', self.branch.get_upstream_branch_name() + ".." + self.branch.name]
        else:
            cmd = ['git', 'diff']
        diff = self.execute_cmd(cmd)
        
        if diff == "":
            print "No Diff Bruh"
            return;
        
        try:
            patch_dir = self.repo_path + '/patches'
            patch_file = patch_dir + '/' + self.branch.name.split('/')[-1] + '.diff'
            if not os.path.exists(patch_dir):
                os.makedirs(patch_dir)
            
            file = open(patch_file, 'w+')
            file.write(diff)
        except:
            print "Error creating patch"
            
        print "Patch created at: " + patch_file
        
    def changes(self, data):
        if not self.branch.fork:
            cmd = ['git', 'diff', '--name-status']
        else:
            cmd = ['git', 'diff', '--name-status', self.branch.fork + '..']
        changes = self.execute_cmd(cmd)
        
        for change in sorted(changes.split('/n')):
            if change != "":
                print change
    
    def clean(self, data):
        self.clean_cache()
        
    def history(self, data):
        if self.branch.fork:
            cmd = ['git', 'log', self.branch.fork + '..']
        elif self.branch.has_upstream_branch:
            cmd = ['git', 'log', self.branch.get_upstream_branch_name() + ".." + self.branch.name]
        else:
            cmd = ['git', 'log']
        subprocess.call(cmd)

    # WORKLOG FUNCTIONS:
    def list_worklogs(self, data):
        self.list_branches('wl')
        
    def delete_worklog(self, data):
        branch = self.get_branch_by_name(data[0])
        self.delete_branch(branch, 'wl')
        
    def new_worklog(self, data):
        new_branch = self.get_branch_by_name(data[0])
        
        if len(data) == 2:
            parent = self.get_branch_by_name(data[1])
            self.new_branch(new_branch, 'wl', parent_branch = parent)
        else:
            self.new_branch(new_branch, 'wl')
        
    # BUG FUNCTIONS:
    
    def list_bugs(self, data):
        self.list_branches('bug')
        
    def delete_bug(self, data):
        branch = self.get_branch_by_name(data[0])
        self.delete_branch(branch, 'bug')
        
    def new_bug(self, data):
        new_branch = data[0]
        
        if len(data) == 2:
            parent = self.get_branch_by_name(data[1])
            self.new_branch(new_branch, 'bug', parent_branch = parent)
        else:
            self.new_branch(new_branch, 'bug')
    
