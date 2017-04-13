#!/usr/bin/python

from sys import argv
from io import open

# The following code block is not needed,
# but we want to see which module is used
# and if and why it fails.
try:
    import pygraphviz
    from networkx.drawing.nx_agraph import write_dot
    print("Using package pygraphviz")
except ImportError:
    try:
        import pydotplus
        from networkx.drawing.nx_pydot import write_dot
        print("Using package pydotplus")
    except ImportError:
        print()
        print("Both pygraphviz and pydotplus were not found ")
        print("see http://networkx.github.io/documentation"
              "/latest/reference/drawing.html for info")
        print()
        raise

from networkx import MultiDiGraph, draw

#
# Find cross reference table in linker map file
#
def find_cref(inmap):
    while True:
        l = inmap.readline()
        if l.strip() == 'Cross Reference Table':
            break;
        if len(l) == 0: return False
    while True:
        l = inmap.readline()
        if len(l) == 0: return False
        words = l.split()
        if len(words) == 2:
            if words[0] == 'Symbol' and words[1] == 'File':
                return True

#
# Interpret a cross reference table
#
def read_cref(inmap):
    modules = MultiDiGraph()
    while True:
        l = inmap.readline()
        words = l.split()
        if len(words) == 2:
            last_symbol = words[0]
            last_module = words[1]
        elif len(words) == 1:
            modules.add_edge(words[0], last_module, label=last_symbol);
        elif len(l) == 0:
            break
    return modules

# when this file is executed
if __name__ == "__main__":
    if len(argv) != 3:
        print "Usage: "+argv[0]+" <linker.map> <output.dot>"
        exit()

    infile = argv[1]
    outfile = argv[2]

    print "Reading "+infile+" ..."
    inmap = open(infile, 'r')
    if find_cref(inmap):
        graph = read_cref(inmap)
        draw(graph)
        print "Writing "+outfile+" ..."
        write_dot(graph, outfile)
    else:
        print "Error: Cross reference table not found in map file."

