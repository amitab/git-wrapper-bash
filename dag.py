class Vertex:
    def __init__(self, key, ref = None):
        self.key = key
        self.edges = {
            'in': set(),
            'out': set()
        }
        self.refs = []
        self.add_ref(ref)
        
    def add_ref(self, ref):
        if ref:
            self.refs.append(ref)
    
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
        
    def to_string(self):
        return self.key + " => " + str(self.refs)
        
    def is_amibigious(self):
        if len(self.refs) > 1:
            return True
        else:
            return false
    
class VertexSet:
    def __init__(self):
        self.vertices = {}
    
    def add_verex(self, key, ref):
        if not self.key_exists(key):
            self.vertices[key] = Vertex(key, ref)
        else:
            self.vertices[key].add_ref(ref)
            
    def add_edge(self, key1, key2):
        self.vertices[key1].add_edge(self.vertices[key2])
        
    def key_exists(self, key):
        return key in self.vertices.keys()
        
    def get_vertex(self, key):
        return self.vertices[key]
        
    def to_string(self):
        data = ""
        for vertex in self.vertices.values():
            data = data + vertex.to_string() + "\n"
        return data

class GitDAG:
    def __init__(self):
        self.vertices = VertexSet()
        
    def add_verex(self, key, ref = None):
        self.vertices.add_verex(key, ref)
    
    def add_edge(self, key1, key2):
        self.vertices.add_edge(key1, key2)
        
    def find_fork_of_vertex(self, key):
        vertex = self.vertices.get_vertex(key)
        while True:
            # print "Examining parent: " + ancestor
            if len(vertex.refs) > 0 and key != vertex.key:
                return vertex.key
            elif vertex.out_degree() > 1:
                return vertex.key
            elif vertex.in_degree() == 0:
                return None
            else:
                vertex = iter(vertex.get_parents()).next()
                
        return fork
        
    def display(self):
        print self.vertices.to_string()