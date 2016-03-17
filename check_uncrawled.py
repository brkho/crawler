# Checks the results of process_list.py to see what percentage of results are
# reachable and what percentage of results are PDFs.
#
# Brian Ho
# brian@brkho.com

import requests
import sys

# Prints an error to standard output and terminates execution.
def print_error(msg):
    print 'ERROR: {}'.format(msg)
    sys.exit(1)

# Main starting point for the script.
def main():
    if len(sys.argv) != 2:
        print_error('Incorrect number of arguments.')
    filename = sys.argv[1]
    with open(filename) as f:
        lines = f.readlines()

    pdfs = 0
    total = 0
    status_codes = {}
    for i, line in enumerate(lines):
        if 'CRAWLED: DOCPAIR NOT CRAWLED' in line:
            total += 1
            source = lines[i-2].strip()[9:]
            target = lines[i-1].strip()[9:]
            if 'pdf' in source.lower() and 'pdf' in target.lower():
                print '(PDF)  {}'.format(source)
                pdfs += 1
            else:
                try:
                    r = requests.get(source, allow_redirects=False, timeout=5)
                    status_code = r.status_code
                except Exception:
                    status_code = -1
                if status_code not in status_codes:
                    status_codes[status_code] = 0
                print '({})  {}'.format(status_code, source)
                status_codes[status_code] += 1

    print '\nPDFs: {}\nNon-PDFs: {}\nTotal: {}\n'.format(pdfs, total - pdfs,
        total)
    print 'Non-PDF Status Codes:'
    for status_code in sorted(list(status_codes.keys())):
        if status_code == -1:
            print 'Timeout:\t{}'.format(status_codes[status_code])
        else:
            print '{}:\t{}'.format(status_code, status_codes[status_code])

if __name__ == "__main__":
    main()