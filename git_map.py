import os
import git
from dag import GitDAG

class GitMap:
    def __init__(self):
        self.repo = git.Repo(os.getcwd())
        self.refs = []
        self.dag = GitDAG()
        
        self.build_branch_map()
        
    def load_refs(self):
        for ref in self.repo.refs:
            item = {
                'ref': ref,
                'commits': []
            }
            #item['commits'].extend(ref.commit.iter_parents(first_parent=True))
            self.refs.append(item)
            
    def build_branch_map(self):
        self.load_refs()
        self.make_map()
        
        for ref in self.refs:
            ref['fork'] = self.dag.find_fork_of_vertex(ref)
            # print ref['ref'].name + ' -> ' + str(ref['fork'])
            if ref['fork'] != None:
                index = ref['commits'].index(ref['fork']) + 1
                del ref['commits'][index:]
            # print ref['ref'].name + ' -> ' + str(ref['commits'])
    
    def make_map(self):
        for ref in self.refs:   
            prev_commit = ref['ref'].commit
            self.dag.add_verex({}, prev_commit.hexsha)
            ref['commits'].append(prev_commit.hexsha)
            commit_gen = ref['ref'].commit.iter_parents(first_parent=True)
            
            for index, commit in enumerate(commit_gen):
                ref['commits'].append(commit.hexsha)
                self.dag.add_verex({}, commit.hexsha)
                self.dag.add_edge(commit.hexsha, prev_commit.hexsha)
                prev_commit = commit
                