# Processes a list of source and target URLs in the form given by the "x" file.
# This then looks into the crawled websites directories for the domain and
# collects statistics on whether the document pair was actually crawled.
# This script can be envoked by specifying a path to a source/target URL file:
# python process_list.py x > results
#
# Brian Ho
# brian@brkho.com

import datetime
import subprocess
import sys
import tld

# Specifies the prefixes defining the source/target URL file format.
prefixes = ['ID', 'SRC MATCHED WORD', 'SRC TXT', 'TGT TXT', 'SRC URL',
            'TGT URL']

# Specifies the base path to the directory with the crawl data.
crawl_path = '/export/b09/pkoehn/site-crawl/data/??/'

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

# Gets the longest string of ASCII characters in a certain string. This is used
# as a quick and dirty way to approximately determine if a source/target string
# is in the crawled HTML document. This is necessary because we cannot simply
# perform a naive index operation into the HTML because of differences in
# character encoding and HTML entities. This is a bit memory inefficent, but
# whatever.
def get_longest_ascii(text):
    longest = ''
    current = ''
    char_range = range(ord('a'), ord('z') + 1) + range(ord('A'),
        ord('Z') + 1) + [ord(' ')]
    for char in text:
        if (('a' <= char <= 'z') or ('A' <= char <= 'Z') or (char == ' ') and
            (char != '?')):
            current += char
        else:
            if len(current) > len(longest):
                longest = current
            current = ''
    return longest if len(longest) > len(current) else current

# Processes the command line arguments and reads the file into an array. This
# also computes a metric used for approximate matching of source/target text in
# the HTML document. This function errors if the input is invalid.
def process_arguments():
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
    except IOError:
        print_error('Unable to read file \'{}\'.'.format(sys.argv[1]))
    for line in lines:
        line['FUZZY SRC'] = get_longest_ascii(line['SRC TXT'])
        line['FUZZY TGT'] = get_longest_ascii(line['TGT TXT'])
        try:
            domain = tld.get_tld(line['SRC URL'])
        except tld.exceptions.TldDomainNotFound:
            domain = None
        line['DOMAIN'] = domain
    return lines

# Processes the index for a crawl looking for the source and target URLs. This
# then returns the path to the source and the path to the target as a tuple
# along with their HTTP status codes.
def process_index(filename, source_url, target_url):
    source_path = None
    target_path = None
    try:
        with open(filename, 'r') as f:
            for line in f:
                elements = line.split('\t')
                if elements[-3] == source_url and source_path is None:
                    source_path = (elements[-2], elements[3])
                if elements[-3] == target_url and target_path is None:
                    target_path = (elements[-2], elements[3])
    except IOError:
        print 'no index'
        return (None, None)
    return (source_path, target_path)

# Checks to see if a document pair is present in the crawl. If there are
# multiple crawls of the same domain, this uses the most recent crawl.
def check_crawled(doc_pairs):
    for doc_pair in doc_pairs:
        if doc_pair['DOMAIN'] is None:
            doc_pair['STATUS'] = 'NO DOMAIN'
        else:
            p = subprocess.Popen('echo ' + crawl_path + '*' +
                doc_pair['DOMAIN'] + '*', stdout=subprocess.PIPE, shell=True)
            out, _ = p.communicate()
            if '??' in out and '*' in out:
                doc_pair['STATUS'] = 'DOMAIN NOT CRAWLED'
            else:
                paths = [path.strip() for path in out.split(' ')]
                times = [datetime.datetime.strptime(path[-10:], '%Y-%m-%d') for
                    path in paths]
                recent_path = paths[times.index(max(times))]
                source_path, target_path = process_index(
                    recent_path + '/hts-cache/new.txt', doc_pair['SRC URL'],
                    doc_pair['TGT URL'])
                if source_path is None or target_path is None:
                    doc_pair['STATUS'] = 'DOCPAIR NOT CRAWLED'
                else:
                    doc_pair['STATUS'] = 'DOCPAIR CRAWLED'

# Main starting point for the script.
def main():
    doc_pairs = process_arguments()
    print 'Processing {} document pairs.'.format(len(doc_pairs))
    check_crawled(doc_pairs)
    cc = {'NO DOMAIN': 0, 'DOMAIN NOT CRAWLED': 0, 'DOCPAIR NOT CRAWLED': 0,
        'DOCPAIR CRAWLED': 0}
    for doc_pair in doc_pairs:
        print 'ID: {}\nSRC URL: {}\nTGT URL: {}\nCRAWLED: {}\n'.format(
            doc_pair['ID'], doc_pair['SRC URL'], doc_pair['TGT URL'],
            doc_pair['STATUS'])
        cc[doc_pair['STATUS']] += 1

    print '\n\nUnable to resolve domain: {}'.format(cc['NO DOMAIN'])
    print 'Domain not crawled: {}'.format(cc['DOMAIN NOT CRAWLED'])
    print 'Domain crawled but not docpair: {}'.format(cc['DOCPAIR NOT CRAWLED'])
    print 'Domain and docpair crawled: {}'.format(cc['DOCPAIR CRAWLED'])
    print 'Total docpairs: {}'.format(len(doc_pairs))

        # print domain
    # print process_index(doc_pairs[0]['SRC URL'], doc_pairs[0]['TGT URL'])

if __name__ == "__main__":
    main()