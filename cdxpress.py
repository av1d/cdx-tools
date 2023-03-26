#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
startTime = time.time()
import argparse
import ijson
import json
import os
import os.path
import random
import re
import requests
import sys
import textwrap
import urllib.parse

from pathlib import Path
from requests.utils import quote


version = '0.2b'

#-------------------------------------#
#          cdxpress  by av1d          #
#-------------------------------------#
#  https://github.com/av1d/cdx-tools  #
#-------------------------------------#

# This is the express version of cdx-tools and is probably fine for most people.
# though it is meant for quick pulls and lacks extensive features.
# Visit the repo above for tools with much more control.


def banner():
    info1  = "+----------------------------+"
    info2  = "\n|  cdxpress   v" + version + " by av1d  |\n"
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        info3  = "\nQuick start: cdxpress.py --url example.org --scan=.jpg,.png,.js,.css --out links.txt"
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
                'use "cdxpress --help" for more information'
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '-u',
        '--url',
        metavar='URL',
        required=True,
        help=
                "The URL to search.\n"
                + sep(),
    )
    parser.add_argument(
        '-s',
        '--scan',
        type=str,
        metavar='STRINGS',
        required=True,
        help=
                "Strings to scan for.\n" +
                "Example usage:\n" +
                "--scan=.exe,.JPG,.zip,\"/cgi-bin/x.cgi?\",\"space space\"\n" +
                "Items are comma-separated, no spaces.\n" +
                "Enclose strings with spaces and special characters in\n" +
                "single or double quotes.\n" +
                "Leave blank to return ALL files (example: --scan= ).\n"
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
        '-c',
        '--case-sensitive',
        action='store_true',
        required=False,
        help=
                "Case sensitive filtering on search strings.\n" +
                "Default: insensitive.\n"
                + sep(),
    )
    parser.add_argument(
        '-o',
        '--outfile',
        metavar='OUTPUT_FILE',
        required=False,
        help=
                "Plain text output file.\n"
                + sep(),
    )
    parser.add_argument(
        '-f',
        '--from',
        metavar='FROM_DATE',
        required=False,
        help=
                "Search FROM this date. 1-14 digits.\n"
                + "Example: --from 2004 or use a Wayback timestamp:\n"
                + "--from 20040601150932\n"
                + "Timestamp format: yyyyMMddhhmmss\n"
                + "Omit --to and --from for all dates.\n"
                + sep(),
    )
    parser.add_argument(
        '-t',
        '--to',
        metavar='TO_DATE',
        required=False,
        help=
                "Search up TO this date. 1-14 digits.\n"
                + "Example: --to 2004 or use a Wayback timestamp:\n"
                + "--to 20040601150932\n"
                + "Timestamp format: yyyyMMddhhmmss\n"
                +  "Omit --to and --from for all dates.\n"
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


    if args['to'] != None and args['from'] != None:
        if int(args['to']) - int(args['from']) < 0:
            print(
                    "--- Error: --to date is less than --from date."
            )
            sys.exit(1)

    global toDateInt
    global fromDateInt

    try:  # try to convert to int, if fail it's not so exit
        if args['to'] != None:
            toDateInt = int(args['to'])
        if args['from'] != None:
            fromDateInt = int(args['from'])
    except:
        print("--- Error: Dates must be integers.\n")
        sys.exit(1)

    # check date format
    if args['to'] != None:
        if int(args['to']) < 1000:
            print(
                    "--- Error: date must be 4-14 digits.\n"
            )
            sys.exit(1)

    # check date format
    if args['from'] != None:
        if int(args['from']) < 1000:
            print(
                    "--- Error: date must be 4-14 digits.\n"
            )
            sys.exit(1)

    # check if output file already exists...
    if args['outfile'] != None:
        outputFilename = args['outfile']
        if os.path.isfile(outputFilename):
            fileExists = input(
                                "File: " +
                                str(outputFilename) +
                                " exists. Append (y/n)? "
            )
            if fileExists.lower() != "y":
                sys.exit(0)



def generateOutput(url_string, timestamp):

    wayback = "https://web.archive.org/web/"
    outURL = (
                str(wayback) +
                str(timestamp) +
                "/" +
                str(url_string)
    )

    if args['outfile'] != None:
        with open(args['outfile'], 'a') as f:
            f.write(outURL + "\n")
    print(outURL)



def fetchResponse(URL):

    timeoutSEC = 60  # http timeout in seconds

    print("\nFetching: " + URL)
    print("Response timeout set to: " + str(timeoutSEC) + " seconds")

    clientVersion = "cdxpress/" + version
    headers = {"User-Agent": clientVersion}

    #Download the response
    try:
        response = requests.get(
                                    URL,
                                    headers=headers,
                                    timeout=timeoutSEC,
                                    stream=True
        )

    except requests.exceptions.Timeout:
        raise SystemExit("Connection timed out")
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if str(response.status_code) == "200":
        print("Received HTTP status: ", response.status_code, response.reason, " - connected to server.")

    global status_code
    status_code = str(response.status_code)
    if status_code != "200":  # exit unless 200
        print("Received HTTP status: " + status_code)
        sys.exit(0)

    print("\nDownloading the response may take a long time, do not stop the program...\n")

    n = json.loads(response.text)  # parse API response
    
    keys = []  # holds JSON keys

    if not n:  # if list is empty...
        print("\n--- Error: Response file is empty. Likely the URL provided is invalid or is not archived.")
        sys.exit(1)

    for i in n[0]:
        try:
            keys.append(i)  # add the keys to the list
        except:
            print("\n--- Error: An unknown error has occurred. The response is missing the appropriate keys.\n")
            sys.exit(1)

    x = [dict(zip(keys, l)) for l in n]  # create list of dictionaries
    x.pop(0)  # remove first line containing JSON keys
    
    final_out = '[\n' + ',\n'.join(json.dumps(i) for i in x) + '\n]'  # format list
    final_out = json.loads(final_out)
    return(final_out)



def checkMatch(url_string, timestamp):

    global scanLINES  # int.  counter for --scan
    global textLINES  # int.  counter for --textfile
    global neg_match  # bool. track if a negative keyword was found

    originalString = url_string

    for key in options.keys():
        currentKey = options[key]
        for string in currentKey:

            if args['case_sensitive'] == False:
                string        = string.lower()
                url_string    = url_string.lower()

            if neg_words:  # if negative keywords were specified
                checkNegMatch(url_string)

            if neg_match == False:  # if no match on neg word, continue
                if string in url_string:
                    scanLINES += 1
                    generateOutput(originalString, timestamp)
    neg_match = False



def checkNegMatch(url_string):  # check for negative keywords, if specified
    global neg_match  # bool. track if a negative keyword was found
    for word in neg_words:
        if word in url_string:
            neg_match = True



def main():

    if sys.argv[1] == "-v" or sys.argv[1] == "--version":
        print("cdxpress v" + version)
        sys.exit(0)


    setArgs()

    # if user-provided URL doesn't contain a scheme, add it...
    if "://" in args['url']:  # if it has scheme, get the netloc
        theHost = urllib.parse.urlsplit(args['url'])
        thePath = theHost.path
        theHost = theHost.netloc
        if thePath == '' or thePath == '/':
            matchType = "&matchType=domain"
        else:
            matchType = "&matchType=prefix"
    else:  # otherwise, add scheme then get netloc
        theHost = "http://" + str(args['url'])    
        theHost = urllib.parse.urlsplit(theHost)
        thePath = theHost.path
        theHost = theHost.netloc
        if thePath == '' or thePath == '/':
            matchType = "&matchType=domain"
        else:
            matchType = "&matchType=prefix"

    if thePath == '':  # fix an empty path, just for sanity
        thePath = "/"

    cdxURL = "https://web.archive.org/cdx/search/cdx?"
    cdxURL = (
            cdxURL
          + "url="
          + theHost
          + thePath
          + matchType
          + "&collapse=urlkey&output=json&gzip=false&filter=statuscode:200&fl=timestamp,original"
    )

    if args['to'] != None:
        userToDate = "&to=" + str(args['to'])
        cdxURL = cdxURL + userToDate
    if args['from'] != None:
        userFromDate = "&from=" + str(args['from'])
        cdxURL = cdxURL + userFromDate

    data = fetchResponse(cdxURL)  # JSON containing lists of dictionaries from API response


    global scanLINES  #int.  counts found items
    scanLINES = 0
    global neg_words  #list. contains negative search words
    neg_words = []
    global neg_match  #bool. track if a negative keyword was found
    neg_match = False
    global options    #dict. comtains search queries
    options = {}

    ##  --exclude negative keywords.  build list of negative search keywords
    if args['exclude'] != None:
        neg_words = args['exclude'].split(',')  # split input string into list


    ##  --scan search
    if args['scan'] != None:
        scanType = 'scan'
        scanList = args['scan'].split(',')  # split input string into list
        options['scan'] = scanList          # add the list to the dict to scan
        count = 0
        for line in data:
            fileURL       = data[count]['original']
            fileTimestamp = data[count]['timestamp']
            checkMatch(fileURL, fileTimestamp)
            count += 1


    ##  RESULTS
    print("\nScan complete.")

    if args['case_sensitive'] == True:
        msg = "Performed case -SENSITIVE- search."
    else:
        msg = "Performed case insensitive search."
    print(msg)

    if scanType == 'json':
        print("\nResults:")
        print(json.dumps(jsonCounter, indent=4)+"\n")

    executionTime = (time.time() - startTime)

    print(
            "Found: " +
            str(scanLINES) +
            " files." +
            "\nExecution time: " +
            str(executionTime) +
            " seconds"
    )



if __name__ == '__main__':
    main()
