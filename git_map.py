import os
import git
import itertools
from dag import GitDAG

class Branch:
    def __init__(self, ref):
        self.ref = ref
        self.name = ref.name
        self.commits = itertools.chain([ref.commit], ref.commit.iter_parents(first_parent=True))

class GitMap:
    def __init__(self):
        self.repo = git.Repo(os.getcwd())
        self.branches = {}
        self.dag = GitDAG()
        
        self.build_branch_map()
        
    def load_refs(self):
        for ref in self.repo.refs:
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
    
    def make_map(self):
        for name, branch in self.branches.items():
            prev_commit = None
            for commit in branch.commits:
                self.dag.add_verex({}, commit.hexsha)
                if prev_commit:
                    self.dag.add_edge(commit.hexsha, prev_commit.hexsha)
                prev_commit = commit

# g = GitMap()