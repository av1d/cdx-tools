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
import textwrap
import urllib.parse

from pathlib import Path
from requests.utils import quote


version = '1.2b'

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
                "Input file which contains valid JSON retrieved from \n" +
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
                "Case sensitive filtering on strings.\n" +
                "Affects all search methods.\n" +
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
                "Strings to scan for.\n" +
                "Example usage:\n" +
                "--scan=.exe,.JPG,.zip,\"/cgi-bin/x.cgi?\",\"space space\"\n" +
                "Items are comma-separated, no spaces.\n" +
                "Enclose strings with spaces and special characters in\n" +
                "single or double quotes.\n"
                + sep(),
    )
    parser.add_argument(
        '-f',
        '--field',
        nargs='+',
        required=False,
        help=
                "Specifies which field in CDX file to search.\n" +
                "Syntax:  --field [key] [string]\n" +
                "Example: --field mimetype text/html\n" +
                "Use with --outfile to save JSON result.\n"
                + sep(),
    )
    parser.add_argument(
        '-x',
        '--exclude',
        type=str,
        metavar='NEGATIVE_STRINGS',
        required=False,
        help=
                "Do not return results for URLs containing these words.\n" +
                "Example usage:\n" +
                "--exclude=www,.exe,cgi-bin\n" +
                "Items are comma-separated, no spaces.\n" +
                "Enclose strings with spaces and special characters in\n" +
                "single or double quotes.\n"
                + sep(),
    )
    parser.add_argument(
        '-t',
        '--textfile',
        metavar='TEXTFILE',
        required=False,
        help=
                "Use a plain text list containing one string per line \n" +
                "as search terms to use on the CDX data.\n"
                + sep(),
    )
    parser.add_argument(
        '-j',
        '--json',
        metavar='IN_FILE',
        required=False,
        help=
                "Load a valid JSON file containing custom keys with\n" +
                "comma-separated values as search strings to search\n" +
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
                "Makes a basic HTML file with links containing all results which\n" +
                "open in a new window when clicked.\n"
                + sep(),
    )
    parser.add_argument(
        '-k',
        '--json-out',
        metavar='OUT_FILE',
        required=False,
        help=
                "Save results to JSON file.\n" +
                "Output can be scanned again to refine.\n"
                + sep(),
    )
    parser.add_argument(
        '-e',
        '--enumerate',
        metavar='OUT_FILE',
        required=False,
        help=
                "Subdomain enumeration.\n" +
                "Create a list of all subhosts.\n"
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
    if args['scan']      != None:
        argCount += 1
    if args['textfile']  != None:
        argCount += 1
    if args['json']      != None:
        argCount += 1
    if args['field']     != None:
        argCount += 1
    if args['enumerate'] != None:
        argCount += 1
    if argCount > 1:
        print(
                "Error: you can only use one of:\n" +
                "--scan, --textfile, --json, --field or --enumerate\n"
        )
        sys.exit(1)

    if (
            args['scan']      == None and
            args['textfile']  == None and
            args['json']      == None and
            args['field']     == None and
            args['enumerate'] == None
    ):
            print(
                    "Error: you must specify one of:\n" +
                    "--scan, --textfile, --json, --field or --enumerate\n"
            )
            sys.exit(1)

    if (args['enumerate'] != None and args['infile'] == None):
            print("Error: you must specify an --infile when using --enumerate.\n")
            sys.exit(1)

    if (args['make_list'] == args['infile']):
        print(
                "Error: You cannot use the same output name as the input file."
        )
        sys.exit(1)

    if (
         args['make_list'] != None and
         args['field']     != None
    ):
            print(
                    "Error: You cannot use --field with --make-list"
            )
            sys.exit(1)

    if (
         args['make_html'] != None and
         args['field']     != None
    ):
            print(
                    "Error: You cannot use --field with --make-html"
            )
            sys.exit(1)

    if (
         args['json_out'] != None and
         args['field']     != None
    ):
            print(
                    "Error: You cannot use --field with --json-out," +
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
    if args['enumerate'] != None:
        checkFileExistence(args['enumerate'], "enumerate")

    ##  MISC OPTIONS

    global case_sensitive  # bool. case-sensitive or not
    global makeList        # bool. for plain text lists
    global makeHTML        # bool. for HTML generation
    global infile          # str.  input CDX/JSON file
    global outfile         # str.  output file
    global listfile        # str.  plain text list file
    global htmlfile        # str.  html filename
    global enumfile        # str.  output file for subhost enumeration
    global jsonOutFile     # bool. if outputting JSON

    if args['enumerate'] != None:
        enumfile = args['enumerate']
    else:
        enumfile = ""

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
    if filearg == "enumerate":
        theFile = args['enumerate']
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
    data = """        <!DOCTYPE html>
        <html lang="en">
        <head>
        <title>Wayback Machine Links</title>
        <meta charset="UTF-8">
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
        </head>
        <body>
        <ul>
    """
    data = textwrap.dedent(data)
    with open(htmlfile, 'a') as f:
        f.write(data + "\n")


def generateOutput(url_string, timestamp):

    wayback = "https://web.archive.org/web/"
    outURL = (
                str(wayback) +
                str(timestamp) +
                "/" +
                str(url_string)
    )

    if makeList == True:
        with open(listfile, 'a') as f:
            f.write(outURL + "\n")

    if makeHTML == True:
        ht1 = '<li><a href="'
        ht2 = outURL
        ht3 = '" target="_blank">'
        ht4 = '</a></li>'
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
    global neg_match

    originalString = url_string

    for key in options.keys():
        currentKey = options[key]
        for string in currentKey:

            if case_sensitive == False:
                string        = string.lower()
                url_string    = url_string.lower()

            if neg_words:  # if negative keywords were specified
                checkNegMatch(url_string)

            if neg_match == False:
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
    neg_match = False



def checkNegMatch(url_string):
    global neg_match
    for word in neg_words:
        if word in url_string:
            neg_match = True



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
    global neg_words
    neg_words = []
    global neg_match
    neg_match = False

    if args['make_html'] != None:
        formatHTML()


    ##  --exclude negative keywords.  build list of negative search keywords
    if args['exclude'] != None:
        neg_words = args['exclude'].split(',')  # split input string into list
        options['exclude'] = neg_words          # add the list to the dict to scan

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

    ##  --enumerate search
    if args['enumerate'] != None:
        global subhostlist
        subhostList = []
        count = 0
        for line in data:
            fileURL = data[count][dictKey]
            theHost = urllib.parse.urlsplit(fileURL)
            theHost = theHost.netloc
            if theHost not in subhostList:
                subhostList.append(theHost)
            count += 1
        with open(str(args['enumerate']), 'w') as f:
            for line in subhostList:
                f.write(line + "\n")
        print(
              "Found " + (str(len(subhostList))) + " hosts.\n" +
              "List saved to: " + str(args['enumerate']) + "\n"
        )
        sys.exit(0)

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

        data = """
               </ul>
               <!-- list generated with cdx-tools https://github.com/av1d/cdx-tools/ -->
               </body>
               </html>
               """
        data = textwrap.dedent(data)
        with open(htmlfile, 'a') as f:
            f.write(data + "\n")

        print(
                "\n"
                + "HTML file list saved as " + str(args['make_html'])
        )

    if "~" in args['scan']:  # warn on tilde usage in case Wayback saved encoded URL
        print(
              "\nI see you used a ~ in your search query.\n"
            + "You may also want to search ussing the URL encoded version, too.\n"
            + "Replace the tilde (~) with %7E to search encoded variations.\n"
            )

    # do we need to warn for other encoded characters?


if __name__ == '__main__':
    main()
