# Processes a list of source and target URLs in the form given by the "x" file.
# This then looks into the crawled websites directories for the domain and
# collects statistics on whether the document pair was actually crawled.
# This script can be envoked by specifying a path to a source/target URL file:
# python process_list.py x > results
#
# Brian Ho
# brian@brkho.com

import sys

# Specifies the prefixes defining the source/target URL file format.
prefixes = ['ID', 'SRC MATCHED WORD', 'SRC TXT', 'TGT TXT', 'SRC URL',
            'TGT URL']

# Prints an error to standard output and terminates execution.
def print_error(msg):
    print 'ERROR: {}'.format(msg)
    sys.exit(1)

# Matches a prefix of a line in the source/target URL file and returns the
# remainder as a string.
def match_line(prefix, line):
    if line.find(prefix) != 0:
        print_error('Source/target file is in an invalid format.')
    return line[len(prefix):]

# Processes the command line arguments and reads the file into an array. This
# function errors if the input is invalid.
def process_arguemnts():
    if len(sys.argv) != 2:
        print_error('Invalid number of arguments.')
    try:
        lines = []
        count = 0
        with open(sys.argv[1], 'r') as f:
            for line in f:
                if count == 0:
                    doc_pair = {}
                elif count == len(prefixes):
                    count = 0
                    lines.append(doc_pair)
                    continue
                output = match_line(prefixes[count] + ': ', line.rstrip('\n'))
                doc_pair[prefixes[count]] = output
                count += 1
        return lines
    except IOError:
        print_error('Unable to read file \'{}\'.'.format(sys.argv[1]))

def main():
    doc_pairs = process_arguemnts()
    print 'Processing {} document pairs.'.format(len(doc_pairs))

if __name__ == "__main__":
    main()