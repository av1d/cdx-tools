#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
startTime = time.time()
import argparse
import ijson

import json
import os
import os.path
import re
import sys

from pathlib import Path
from requests.utils import quote
from urllib.parse import urlparse

from pympler.asizeof import asizeof

version = '0.6b'

#-------------------------------------#
#         cdx-filter  by av1d         #
#-------------------------------------#
#  https://github.com/av1d/cdx-tools  #
#-------------------------------------#



def banner():
    info1  = "+----------------------------+"
    info2  = "\n|  cdx-filter v" + version + " by av1d  |\n"
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        info3  = "\n Ultimately, you should read the manual!"
    else:
        info3  = ""
    banner = info1 + info2 + info1 + info3
    return banner


def sep():
    return "------------\n"



def setArgs():
    parser = argparse.ArgumentParser(
        description=banner(),
        usage=(
                'use "python %(prog)s --help" for more information'
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '-i',
        '--infile',
        metavar='JSON_FILE',
        required=True,
        help=
                "Input file which contains valid JSON retrieved from \n" \
                "the CDX server.\n"
                + sep(),
    )
    parser.add_argument(
        '-o',
        '--outfile',
        metavar='OUTPUT_FILE',
        required=False,
        help=
                "Output file. Filetype depends on method used.\n"
                + sep(),
    )
    parser.add_argument(
        '-c',
        '--case-sensitive',
        action='store_true',
        required=False,
        help=
                "Case sensitive filtering on strings.\n" \
                "Affects all search methods.\n" \
                "Default: insensitive.\n"
                + sep(),
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        required=False,
        help=
                "Suppress link output. Faster when saving to file. \n"
                + sep(),
    )
    parser.add_argument(
        '-s',
        '--scan',
        type=str,
        metavar='STRINGS',
        required=False,
        help=
                "Strings to scan for.\n" \
                "Example usage:\n" \
                "--scan=.exe,.JPG,.zip,\"/cgi-bin/x.cgi?\",\"space space\"\n" \
                "Items are comma-separated, no spaces.\n" \
                "Enclose strings with spaces and special characters in\n" \
                "single or double quotes.\n"
                + sep(),
    )
    parser.add_argument(
        '-f',
        '--field',
        nargs='+',
        required=False,
        help=
                "Specifies which field in CDX file to search.\n" \
                "Syntax:  --field [key] [string]\n" \
                "Example: --field mimetype text/html\n" \
                "Use with --outfile to save JSON result.\n"
                + sep(),
    )
    parser.add_argument(
        '-t',
        '--textfile',
        metavar='TEXTFILE',
        required=False,
        help=
                "Use a plain text list containing one string per line \n" \
                "as search terms to use on the CDX data.\n" \
                + sep(),
    )
    parser.add_argument(
        '-j',
        '--json',
        metavar='IN_FILE',
        required=False,
        help=
                "Load a valid JSON file containing custom keys with\n" \
                "comma-separated values as search strings to search\n" \
                "the CDX data with.\n"
                + sep(),
    )
    parser.add_argument(
        '-m',
        '--make-list',
        metavar='OUTPUTFILE',
        required=False,
        help=
                "Makes a plain text list of links containing all results.\n"
                + sep(),
    )
    parser.add_argument(
        '-n',
        '--make-html',
        metavar='OUTPUTFILE',
        required=False,
        help=
                "Makes a basic HTML file with links containing all results which\n"
                + "open in a new window when clicked.\n"
                + sep(),
    )
    parser.add_argument(
        '-k',
        '--json-out',
        metavar='OUT_FILE',
        required=False,
        help=
                "Save results to JSON file.\n" \
                "Output can be scanned again to refine.\n" \
                + sep(),
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        required=False,
        help=
                "Print version information then exit.\n"
                + sep(),
    )

    global args  # dict
    args = vars(parser.parse_args())

    ##  SYNTAX/INPUT/FILE CHECKING

    argCount = 0
    if args['scan']     != None:
        argCount += 1
    if args['textfile'] != None:
        argCount += 1
    if args['json']     != None:
        argCount += 1
    if args['field']    != None:
        argCount += 1
    if argCount > 1:
        print(
                "Error: you can only use one of:\n"
                "--scan, --textfile, --json or --field\n"
        )
        sys.exit(1)

    if (
            args['scan']     == None and
            args['textfile'] == None and
            args['json']     == None and
            args['field']    == None
    ):
            print(
                    "Error: you must specify one of:\n"
                    "--scan, --textfile, --json or --field\n"
            )
            sys.exit(1)

    if (
         args['make_list'] != None and
         args['field']     != None
    ):
            print(
                    "Error: You cannot use --field with --make-list" \
            )
            sys.exit(1)

    if (
         args['make_html'] != None and
         args['field']     != None
    ):
            print(
                    "Error: You cannot use --field with --make-html" \
            )
            sys.exit(1)

    if (
         args['json_out'] != None and
         args['field']     != None
    ):
            print(
                    "Error: You cannot use --field with --json-out," \
                    "use --outfile instead."
            )
            sys.exit(1)


    ##  Check file existence

    if args['infile'] != None:
        checkInputFile('infile')
    if args['textfile'] != None:
        checkInputFile('textfile')
    if args['json'] != None:
        checkInputFile('json')

    if args['outfile'] != None:
        checkFileExistence(args['outfile'], "outfile")
    if args['make_list'] != None:
        checkFileExistence(args['make_list'], "make_list")
    if args['make_html'] != None:
        checkFileExistence(args['make_html'], "make_html")
    if args['json_out'] != None:
        checkFileExistence(args['json_out'], "json_out")

    ##  MISC OPTIONS

    global case_sensitive  # bool. case-sensitive or not
    global makeList        # bool. for plain text lists
    global makeHTML        # bool. for HTML generation
    global infile          # str.  input CDX/JSON file
    global outfile         # str.  output file
    global listfile        # str.  plain text list file
    global htmlfile        # str.  html filename
    global jsonOutFile     # bool. if outputting JSON

    if args['json_out'] != None:
        jsonOutFile = args['json_out']
    else:
        jsonOutFile = ""

    if args['case_sensitive'] == False:
        case_sensitive = False
    else:
        case_sensitive = True

    infile   = args['infile']
    outfile  = args['outfile']
    listfile = args['make_list']
    htmlfile = args['make_html']

    if args['make_list'] != None:
        makeList = True
    else:
        makeList = False

    if args['make_html'] != None:
        makeHTML = True
    else:
        makeHTML = False


def checkInputFile(argument):

    if os.path.exists(args[argument]) == False:
        print(
                "Error: file " + str(args[argument]) + " doesn't exist."
        )
        sys.exit(1)



def checkFileExistence(filename, filearg):

    if filearg == "outfile":
        theFile = args['outfile']
    if filearg == "make_list":
        theFile = args['make_list']
    if filearg == "make_html":
        theFile = args['make_html']
    if filearg == "json_out":
        theFile = args['json_out']
    if os.path.isfile(filename):
        fileExists = input(
                            "File: " +
                            str(theFile) +
                            " exists. Append (y/n)? "
        )
        if fileExists.lower() != "y":
            sys.exit(0)
        else:
            return True


def formatHTML():
    data = """
        <style>
        body, html {
            font-size: 24px;
            color: #fff;
            background-color: #000;
        }
        li {
            padding: 3px;
        }
        a:link {
            color: #ccc;
        }
        a:visited {
            color: #e343e8;
        }
        a:hover, a:active {
            font-weight: bold;
            color: #93ed0c;
            background-color: #152a40;
        }
        </style>
    """
    with open(htmlfile, 'a') as f:
        f.write(data + "\n")


def generateOutput(url_string, timestamp):

    baseURL = urlparse(url_string)
    baseURL = baseURL.netloc  # get domain+tld
    baseURL = baseURL.split(':',1)[0]  # remove ports if any

    if re.findall("^https?:\/\/[A-Za-z0-9:.]*([\/]{1}.*\/?)$", url_string):
        remotePath = re.findall(
                                 "^https?:\/\/[A-Za-z0-9:.]*([\/]{1}.*\/?)$",
                                 url_string
        )[0]  # get path (everthing after the tld)
    else:
        remotePath = "/"  # if nothing then it's just the root

    percent_encode = quote(str(remotePath))  # url-encode the path
    encoded_path = Path(percent_encode)  # create POSIX path
    final_path = str(encoded_path)  # POSIX path to string
    save_path = final_path

    final_path = (
                    baseURL  +
                    final_path
    )

    save_path = (
                    baseURL  +
                    "/" + str(timestamp) +
                    save_path
    )  # add timestamp for organization purposes. ex: example.com/2004/files

    # if path ends in / then we save it as index.html
    if (url_string.endswith("/") or remotePath.endswith("/")):
        final_path = (final_path + "index.html")

    wayback = "https://web.archive.org/web/"
    outURL = (
                str(wayback) +
                str(timestamp) +
                "/" +
                str(final_path)
    )

    if makeList == True:
        with open(listfile, 'a') as f:
            f.write(outURL + "\n")

    if makeHTML == True:
        ht1 = '<li><a href="'
        ht2 = outURL
        ht3 = '" target="_blank">'
        ht4 = '</a><br></li>'
        outHTML = ht1 + ht2 + ht3 + ht2 + ht4
        with open(htmlfile, 'a') as f:
            f.write(outHTML + "\n")


def generateJSONList(data):
    with open(jsonOutFile, 'a') as f:
        f.write(json.dumps(data) + "\n")



def convertListToJSON():

    jlist = []
    with open(jsonOutFile) as f:
        for line in f:
            jlist.append(json.loads(line))
    with open(jsonOutFile, 'w') as fp:
        fp.write(
                    '[\n' +
                    ',\n'.join(json.dumps(i) for i in jlist) +
                    '\n]'
        )



def checkMatch(url_string, timestamp):

    global scanLINES  # int.  counter for --scan
    global textLINES  # int.  counter for --textfile

    originalString = url_string

    for key in options.keys():
        currentKey = options[key]
        for string in currentKey:

            if case_sensitive == False:
                string        = string.lower()
                url_string    = url_string.lower()

            if string in url_string:
                if args['quiet'] == False:
                    print(originalString)

                if scanType == 'json':
                    jsonCounter[key] += 1
                if scanType == 'scan':
                    scanLINES += 1
                if scanType == 'field':
                    fieldLINES += 1
                if scanType == 'textfile':
                    textLINES += 1

                generateOutput(originalString, timestamp)



def loadCDX(infile):

    global dictKey  # str.  holds URL field name from CDX file.

    msg ="File isn't valid JSON or other error.\n"

    try:
        with open(infile, 'r') as f:
            data = json.load(f)
    except:
        print(msg)
        sys.exit(1)

    if 'file_url' in data[0].keys():
        dictKey = 'file_url'
    elif 'original' in data[0].keys():
        dictKey = 'original'
    else:
        dictKey = None
        print("Error: incompatible CDX format.\n" + msg)
        sys.exit(1)

    return data



def loadJSON(input_file):

    global options  # dict
    options = {}

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except:
        print("Error loading or parsing JSON file.\n")
        sys.exit(1)

    keys = data[0].keys()

    for key in data[0]:
        options[key] = data[0][key].split(',')




def main():

    try:
        if sys.argv[1] == "-v" or sys.argv[1] == "--version":
            print("cdx-filter v" + version)
            sys.exit(0)
    except:
        print("Expected at least 1 argument. --help for help.")
        sys.exit(1)


    setArgs()

    global infile
    global outfile

    data = loadCDX(infile)

    global options
    options = {}
    global options_count
    options_count = {}
    global scanLINES
    scanLINES = 0
    global textLINES
    textLINES = 0
    global scanType
    scanType = None

    global currentCDXline  # str.  used for JSON output

    if args['make_html'] != None:
        formatHTML()

    ##  --textfile search
    if args['textfile'] != None:
        scanType = 'textfile'
        textInputFile = args['textfile']
        with open(textInputFile, 'r') as tfile:
            allstrings = tfile.read()  # read is probably fine for this
            parseLines = allstrings.split('\n')  # remove empty/space/newline
            textStrings = [line for line in parseLines if line.strip()]
            options['textfile'] = textStrings  # copy list to options dict
        count = 0
        for line in data:  # for each line in the CDX file
            fileURL       = data[count][dictKey]  # assign keys
            fileTimestamp = data[count]['timestamp']
            checkMatch(fileURL, fileTimestamp)  # scan
            if jsonOutFile != "":  # if generating JSON
                generateJSONList(line)  # write line to temp file
            count += 1
        if jsonOutFile != "":  # if generating JSON
            convertListToJSON()  # write final JSON file

    ##  --json search
    if args['json'] != None:
        scanType = 'json'
        loadJSON(args['json'])
        global jsonCounter
        jsonCounter = {}
        for key in options.keys():
            jsonCounter[key] = 0  # fill dict with 0's to start counter at
        count = 0
        for line in data:  # for each line in the CDX file
            fileURL       = data[count][dictKey]  # assign keys
            fileTimestamp = data[count]['timestamp']
            checkMatch(fileURL, fileTimestamp)  # scan
            if jsonOutFile != "":  # if generating JSON
                generateJSONList(line)  # write line to temp file
            count += 1
        if jsonOutFile != "":  # if generating JSON
            convertListToJSON()  # write final JSON file

    ##  --scan search
    if args['scan'] != None:
        scanType = 'scan'
        scanList = args['scan'].split(',')  # split input string into list
        options['scan'] = scanList          # add the list to the dict to scan
        count = 0
        for line in data:
            fileURL       = data[count][dictKey]
            fileTimestamp = data[count]['timestamp']
            checkMatch(fileURL, fileTimestamp)
            if jsonOutFile != "":  # if generating JSON
                generateJSONList(line)  # write line to temp file
            count += 1
        if jsonOutFile != "":  # if generating JSON
           convertListToJSON()  # write final JSON file

    ##  --field search
    if args['field'] != None:
        scanType = 'field'
        fieldList = args['field']  # get list of provided fields to search
        fieldLINES = 0  # hit counter
   
        if args['outfile'] != None:  # if --outfile specified
            fieldOUT = True
        else:
            fieldOUT = False

        count = 0

        for line in data:
            if case_sensitive == False:  # if case insensitive
                searchVal = fieldList[1].lower()
                dataLine  = data[count][fieldList[0]].lower()
            else:  # case sensitive
                searchVal = fieldList[1]
                dataLine  = data[count][fieldList[0]]
            if searchVal == dataLine:
                if args['quiet'] == False:  # if not suppressing output
                    print(line)  # print it
                if fieldOUT == True:  # if --outfile specified
                    with open(args['outfile'], 'a') as f:
                        f.write(json.dumps(line) + "\n")
                fieldLINES += 1
            count += 1

        if fieldOUT == True:
            flist = []
            with open(args['outfile']) as f:
                for line in f:
                    flist.append(json.loads(line))
            with open(args['outfile'], 'w') as fp:
                fp.write(
                            '[\n' +
                            ',\n'.join(json.dumps(i) for i in flist) +
                            '\n]'
                )


    ##  RESULTS
    print("\nScan complete.")

    if case_sensitive == True:
        msg = "Performed case -sensitive- search."
    else:
        msg = "Performed case insensitive search."
    print(msg)

    if scanType == 'json':
        print("\nResults:")
        print(json.dumps(jsonCounter, indent=4)+"\n")

    countType = 0
    if scanType == 'scan':
        countType = scanLINES
    if scanType == 'textfile':
        countType = textLINES
    if scanType == 'field':
        countType = fieldLINES
    if scanType == 'json':
        for jsonkey in jsonCounter:
            countType += jsonCounter[jsonkey]

    executionTime = (time.time() - startTime)

    print(
            "Found: " +
            str(countType) +
            " files." +
            "\nExecution time: " +
            str(executionTime) +
            " seconds"
    )

    if args['make_list'] != None:
        print(
                "\n"
                + "To use the generated list with wget, issue this command:\n"
                + "wget -i " + str(args['make_list']) + "\n"
                + "To omit files being saved into folders with timestamps, use this:\n"
                + "wget --convert-links -x -nH --cut-dirs=2 -i "
                + str(args['make_list'])
        )

    if args['make_html'] != None:
        print(
                "\n"
                + "HTML file list saved as " + str(args['make_html'])
        )



if __name__ == '__main__':
    main()
