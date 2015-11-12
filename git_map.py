import os
import re
import git
import itertools
from dag import GitDAG

class Branch:
    def __init__(self, ref, id = None, type = None, fork = None):
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

        self.ref = ref
        self.name = ref.name
        self.commits = itertools.chain([ref.commit], ref.commit.iter_parents(first_parent=True))
        self.id = id
        self.fork = fork
        if type:
            self.type = type
        else:
            self.type = self.calc_type()

        self.has_upstream_branch = True if self.ref.tracking_branch() else False

    def calc_type(self):
        for type, info in self.branch_regex.items():
            if info['regex'].search(self.name):
                return type
                
    def is_remote_branch(self):
        if isinstance(self.ref, git.RemoteReference):
            return True
        else:
            return False
            
    def get_upstream_branch(self):
        return self.ref.tracking_branch()
        
    def get_upstream_branch_name(self):
        remote = self.ref.tracking_branch()
        if not remote:
            return None
        else:
            return remote.name
            
    def register(self, db):
        print "Registering branch " + self.name
        resp = db.insert('branch', (self.name, self.fork, self.type,))
        self.id = resp.lastrowid
        return self.id

    def unregister(self, db):
        print "Un-Registering branch " + self.name
        db.delete('branch', (self.name, self.type,))

class GitMap:
    def __init__(self, repo):
        self.repo = git.Repo(os.getcwd())
        self.branches = {}
        self.dag = GitDAG()
        self.map_build = False
        
        self.load_refs()
        
    def load_refs(self):
        for ref in self.repo.refs:
            if not isinstance(ref, git.TagReference) and ref.name.find('stash') == -1:
                self.branches[ref.name] = Branch(ref)
            
    def build_branch_map(self):
        self.load_refs()
        self.make_map()
        
        for name, branch in self.branches.items():
            if branch.name.find('master') >= 0:
                branch.fork = None
            else:
                branch.fork = self.dag.find_fork_of_vertex(branch.ref.commit.hexsha)
            # print name + " => " + str(branch.fork)
        self.map_build = True
    
    def make_map(self):
        for name, branch in self.branches.items():
            prev_commit = None
            for commit in branch.commits:
                self.dag.add_verex({}, commit.hexsha)
                if prev_commit:
                    self.dag.add_edge(commit.hexsha, prev_commit.hexsha)
                prev_commit = commit

# g = GitMap()