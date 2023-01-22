#!/usr/bin/python3.7 
# -*- coding: utf-8 -*-

import time
startTime = time.time()
import argparse
import datetime
import json
import os
import random
import requests
import sys

from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import unquote
from urllib.parse import urlencode



version = '0.1b'

#-----------------------------------#
#         cdx-query by av1d         #
#-----------------------------------#
# https://github.com/av1d/cdx-tools #
#-----------------------------------#




def banner():
    info1  = "+---------------------------+"
    info2  = "\n|  cdx-query v" + version + " by av1d  |\n"
    banner = info1 + info2 + info1
    return banner


def sep():
    return "------------\n"


def setArgs():
    parser=argparse.ArgumentParser(
        description=banner(),
        usage=(
                'use "python %(prog)s --help" for more information'
        ),
        formatter_class = argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '-u',
        '--url',
        metavar='URL',
        required=True,
        help=
                "The URL to search for.\n"
                + sep(),
    )
    parser.add_argument(
        '--out',
        metavar='FILE',
        required=False,
        help=
                "Output the CDX server response to this filename in JSON.\n"
                + sep(),
    )
    parser.add_argument(
        '--text',
        metavar='FILE',
        required=False,
        help=
                "Output the original URLs to this filename as text.\n"
                + sep(),
    )
    parser.add_argument(
        '--way',
        metavar='FILE',
        required=False,
        help=
                "Output the full Wayback Machine URLs to this filename.\n"
                + sep(),
    )
    parser.add_argument(
        '-f',
        '--from',
        metavar='FROM_DATE',
        required=False,
        help=
                "Search FROM this date. 1-14 digits.\n" \
                "Example: --from 2004 or use a Wayback timestamp: " \
                "--from 20040601150932\n" \
                "Timestamp format: yyyyMMddhhmmss\n" \
                "Omit --to and --from for all dates.\n"
                + sep(),
    )
    parser.add_argument(
        '-t',
        '--to',
        metavar='TO_DATE',
        required=False,
        help=
                "Search up TO this date.\n" \
                "Same settings as --from \n"
               + sep(),
    )
    parser.add_argument(
        '--host',
        action='store_true',
        required=False,
        help=
                "Return results only from example.com instead of *.example.com\n"
                + sep(),
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        required=False,
        help=
                "Don't print URLs to screen (faster, less memory usage).\n"
                + sep(),
    )
    parser.add_argument(
        '-l',
        '--limit',
        metavar='NUMBER',
        required=False,
        help=
                "Limit to first N results (example: --limit 50).\n" \
                "Limit to last N results  (example: --limit -50) \n"
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

    global args  # dict.
    args = vars(parser.parse_args())  # all args end up as URL params

    ### OUTPUT FILES

    global outputFile  # str.
    if args['out'] != None:
        checkFileExistence(args['out'])  # check if file exists
        outputFile = args['out']  # assign filename to var
        del args['out']  # delete the key from dictionary
    else:
        outputFile = ""

    global textOutput  # str.
    if args['text'] != None:
        checkFileExistence(args['text'])  # check if exists
        textOutput = args['text']
        del args['text']
    else:
        textOutput = ""
        del args['text']

    global wayOut  # str.
    if args['way'] != None:
        checkFileExistence(args['way'])  # check if exists
        wayOut = args['way']
        del args['way']
    else:
        wayOut = ""
        del args['way']

    ### SYNTAX CHECKING

    if args['to'] != None and args['from'] != None:
        if int(args['to']) - int(args['from']) < 0:  # if dates are backwards
            print(
                    "Error: --to date is less than --from date."
            )
            sys.exit(1)

    try:  # check timestamps
        if args['to'] != None:  # convert to int, if fail it's not so exit
            toDateInt = int(args['to'])
        if args['from'] != None:
            fromDateInt = int(args['from'])
    except:
        print("Error: Dates must be integers.\n")
        sys.exit(1)

    if args['to'] != None:  # check date format
        if int(args['to']) < 1000:
            print(
                    "Error: date must be 4-14 digits.\n"
            )
            sys.exit(1)

    if args['from'] != None:
        if int(args['from']) < 1000:
            print(
                    "Error: date must be 4-14 digits.\n"
            )
            sys.exit(1)

    if args['url'] != None:  # remove scheme from URL
        if (
            "http://" in args['url'] or
            "https://" in args['url']
        ):
            if "http://" in args['url']:
                args['url'] = args['url'].replace("http://", "")
            if "https://" in args['url']:
                args['url'] = args['url'].replace("https://", "")

    # ADD PARAMETERS TO URL AND MODIFY ARGS DICT

    if args['host'] == False:  # return results from host and all subhosts *.example.com 
        args['matchType'] = "domain"
        del args['host']
    else:  # return results from host example.com
        args['matchType'] = "host"
        del args['host']

    args['output'] = "json"

    if args['limit'] == None:
        del args['limit']

    global beQuiet  # bool. print URLs to screen or not
    if args['quiet'] == True:
        beQuiet = True
        del args['quiet']
    else:
        beQuiet = False

    # Remove arguments with values of None and False so they're not
    # converted to URL parameters. 'filtered' is the final dictionary w/ URL params
    global filtered  # dict.
    filtered = {k: v for k, v in args.items() if v is not None}
    filtered = {k: v for k, v in filtered.items() if v is not False}


def checkFileExistence(filename):

    if os.path.isfile(filename):
        fileExists = input(
                            "File: "
                            + str(filename)
                            + " exists. Overwrite (y/n)? "
        )
        if fileExists.lower() != "y":
            sys.exit(0)
        else:
            return True


def cdxToDict(cdx_response):

    global dictList  # list
    dictList = []

    cdx_response = json.loads(json.dumps(cdx_response))

    count = 0
    for line in cdx_response:
        
        d = dict()
        ind = 0
        for data in cdx_response:
            d[ind] = data
            ind+=1

        keys = d[0]

        cdx_dict = {}
        for i in keys:
            cdx_dict[i] = None

        val = d[count]

        count_index = 0
        for key in cdx_dict:
            cdx_dict[key] = val[count_index]
            count_index += 1

        dictList.append(cdx_dict)       
        count += 1

    dictList.pop(0)  # remove the list of keys
    final_out = '[' + ',\n'.join(json.dumps(i) for i in dictList) + ']\n'

    return(final_out)


def fetchResponse():  # download and save

    URL = "https://web.archive.org/cdx/search/cdx?" + filtered

    if args["url"] != None:

        print("Fetching: " + URL + "\n")
        print("This may take awhile...")

        clientVersion = "cdx-tools/" + version
        headers = {"User-Agent": clientVersion}

        try:
            response = requests.get(
                                        URL,
                                        headers=headers,
                                        timeout=30,
                                        stream=True
            )

        except requests.exceptions.Timeout:
            raise SystemExit("Connection timed out")
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        status_code = str(response.status_code)

        if status_code != "200":  # exit unless 200
            print("Received HTTP status: " + status_code)
            sys.exit(0)

        cdx_response = json.loads(response.text)

        global num_lines  # int.  lines returned count
        # subtract 1 to ignore the first line which has the JSON keys:
        num_lines = sum(1 for line in cdx_response) - 1

        cdx_out = cdxToDict(cdx_response)

        if beQuiet == False:  # if printing URLs to screen
            dataLines = cdx_response[1:]  # remove first line containing keys
            for line in dataLines:
                print(line[2])  # 'original' (url) field

        if outputFile != "":  # JSON output
            print("Saving as: " + outputFile)
            with open(outputFile, 'w') as out_file:
                out_file.write(cdx_out)
                print("Done.")  

        if wayOut != "":  # if saving Wayback links
            with open(wayOut, 'w') as f:
                for line in dataLines:
                    url_string = line[2]
                    timestamp  = line[1]
                    if "https://" in url_string:  # remove scheme
                        url_string =  url_string.replace("https://", "")
                    if "http://" in url_string:
                        url_string =  url_string.replace("http://", "")
                    wayback = "https://web.archive.org/web/"
                    outURL = (str(wayback) + str(timestamp) + "/" + str(url_string))
                    f.write(outURL + "\n")


def main():


    try:  # check if any args so we can handle -v specially
        catchArg = sys.argv[1]
    except:  # exit if not
        print("Expected at least one argument. --help for help.")
        sys.exit(1)
    if catchArg == "-v" or catchArg == "--version":  # if args, see if -v
        print("cdx-filter v" + version)
        sys.exit(0)

    setArgs()
    fetchResponse()

    executionTime = (time.time() - startTime)
    
    print(
            "\n" + str(num_lines) + " lines returned" +
            "\nExecution time: " + str(executionTime) + " seconds\n"
    )


if __name__ == '__main__':
    main()
