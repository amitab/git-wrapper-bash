class Vertex:
    def __init__(self, key, data):
        self.data = data
        self.key = key
        self.edges = {
            'in': set(),
            'out': set()
        }
    
    def add_edge(self, vertex):
        self.edges['out'].add(vertex)
        vertex.edges['in'].add(self)
    
    def get_parents(self):
        return self.edges['in']
    
    def get_children(self):
        return self.edges['out']
        
    def in_degree(self):
        return len(self.edges['in'])
        
    def out_degree(self):
        return len(self.edges['out'])
    
class VertexSet:
    def __init__(self):
        self.vertices = {}
    
    def add_verex(self, key, data):
        if not self.key_exists(key):
            self.vertices[key] = Vertex(key, data)
            
    def add_edge(self, key1, key2):
        self.vertices[key1].add_edge(self.vertices[key2])
        
    def key_exists(self, key):
        return key in self.vertices.keys()
        
    def get_vertex(self, key):
        return self.vertices[key]

class GitDAG:
    def __init__(self):
        self.vertices = VertexSet()
        
    def add_verex(self, data, key):
        self.vertices.add_verex(key, data)
    
    def add_edge(self, key1, key2):
        self.vertices.add_edge(key1, key2)
        
    def find_fork_of_vertex(self, key):
        vertex = self.vertices.get_vertex(key)
        while True:
            # print "Examining parent: " + ancestor
            if vertex.out_degree() > 1:
                return vertex.key
            elif vertex.in_degree() == 0:
                return None
            else:
                vertex = iter(vertex.get_parents()).next()
                
        return fork
        
    def display(self):
        print self.vertices.keys()
        print self.edges