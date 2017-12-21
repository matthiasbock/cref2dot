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
def find_cref_table(inmap):
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
def read_cref_table(
        inmap,
        strip_paths=["/usr", "lib/STM32Cube_FW_F4_V1.16.0"],
        simplify_paths=["libgcc.a", "libc_nano.a", "libnosys.a"],
        hide_aeabi_symbols=True
        ):

    # Helper function to simplify filenames in order to increase graph clarity
    def process_filename(last_module):
        # Strip certain file paths
        for key in strip_paths:
            if last_module.find(key) > -1:
                s = last_module.split("/")
                print(last_module + " - " + s[len(s)-1])
                last_module = s[len(s)-1]
        # Remove symbol names (in round brackets) from certain libraries
        for key in simplify_paths:
            if last_module.find(key) > -1:
                s = last_module.split("(")
                print(last_module + " - " + s[0])
                last_module = s[0]
        return last_module

    # Create new graph
    modules = MultiDiGraph()

    # Parse all table lines
    redundant_associations = []
    while True:
        l = inmap.readline()
        words = l.split()

        if len(words) == 2:
            # New symbol A, which is defined in file B
            last_symbol = words[0]
            last_module = process_filename(words[1])

        elif len(words) == 1:
            # One more file uses the previous symbol
            filename = process_filename(words[0])

            # References of a file to itself are not particularly interesting
            if filename != last_module:
                if last_symbol.find("__aeabi") > -1 and hide_aeabi_symbols:
                    t = (filename, last_module)
                    if not (t in redundant_associations):
                        redundant_associations.append(t)
                        modules.add_edge(filename, last_module);
                else:
                    modules.add_edge(filename, last_module, label=last_symbol);

        elif len(l) == 0:
            # End of table
            break

    # Return the generated graph
    return modules


#
# Invoke dot to export dot-file to PDF
#
def dot_to_pdf(dot_filename, pdf_filename):
    print("Using dot to export " + dot_filename + " to "+pdf_filename + "...")
    Popen(split("dot " + dot_filename + "-Tpdf " + pdf_filename)).wait()
    print("PDF export completed.")


#
# Main program
#
if __name__ == "__main__":
    if len(argv) != 3:
        print "Usage: "+argv[0]+" <linker.map> <output.dot/pdf>"
        exit()

    infile = argv[1]
    outfile = argv[2]

    print "Reading "+infile+" ..."
    inmap = open(infile, 'r')
    if find_cref_table(inmap):
        graph = read_cref_table(inmap)
        draw(graph)
        print "Writing "+outfile+" ..."
        write_dot(graph, outfile)

        #if dot_filename[-4:] != ".dot":
        #    print("Unknown file extension. Should be '.dot'.")
        #    return
        #pdf_filename = dot_filename[-4:] + ".pdf"

    else:
        print "Error: Cross reference table not found in map file."

