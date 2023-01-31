#!/usr/bin/python3.7 
# -*- coding: utf-8 -*-

import time
startTime = time.time()
import argparse
import datetime
import json
import logging
import os
import random
import requests
import sys
import threading
import urllib.parse

from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import unquote
from urllib.parse import urlencode



version = '0.8b'

#-----------------------------------#
#         cdx-query by av1d         #
#-----------------------------------#
# https://github.com/av1d/cdx-tools #
#-----------------------------------#


 ########################################
  ####  VISUAL
   ###
    ##
def banner():
    info1  = "+---------------------------+"
    info2  = "\n|  cdx-query v" + version + " by av1d  |\n"
    info3  = "\nQuickstart: cdxq.py --url example.com/path/ --out results.txt\n"
    banner = info1 + info2 + info1 + info3
    return banner


def sep():
    return "------------\n"


def progress():
    sys.stdout.write(".")
    sys.sleep(1)


 #########################################
  ####  ARGUMENT PARSING / SYNTAX CHECKING
   ###
    ##
def setup():
    ######################################
    ## ARGPARSE
    parser=argparse.ArgumentParser(
        description=banner(),
        usage=(
                'use "python %(prog)s --help" for more information'
        ),
        formatter_class = argparse.RawTextHelpFormatter,
    )
    # URL
    parser.add_argument(
        '-u',
        '--url',
        metavar='URL',
        required=True,
        help=
                "The URL to search for.\n"
                + sep(),
    )
    # output file
    parser.add_argument(
        '-out',
        '--out',
        metavar='FILE',
        required=False,
        help=
                "Output the CDX server response to this filename.\n"
                + sep(),
    )
    # From date
    parser.add_argument(
        '-f',
        '--from',
        metavar='FROM_DATE',
        required=False,
        help=
                "Search FROM this date. 1-14 digits.\n" \
                "Example: --from 2004 or use a Wayback timestamp:\n" \
                "--from 20040601150932\n" \
                "Timestamp format: yyyyMMddhhmmss\n" \
                "Omit --to and --from for all dates.\n"
                + sep(),
    )
    # to date
    parser.add_argument(
        '-t',
        '--to',
        metavar='TO_DATE',
        required=False,
        help=
                "Search up TO this date. 1-14 digits.\n" \
                "Example: --to 2004 or use a Wayback timestamp:\n" \
                "--to 20040601150932\n" \
                "Timestamp format: yyyyMMddhhmmss\n" \
                "Omit --to and --from for all dates.\n"
               + sep(),
    )
    # matchType
    parser.add_argument(
        '-m',
        '--matchtype',
        choices=[
                    'exact',
                    'prefix',
                    'host',
                    'domain'
        ],
        required=False,
        help=
                "exact  - return results matching exactly:\n archive.org/about/.\n" \
                "prefix - return results for all results\n under the path archive.org/about/.\n" \
                "host   - return results from host archive.org.\n" \
                "domain - return results from host archive.org and\n all subhosts *.archive.org.\n\n" \
                "Default is 'domain' if the argument is omitted.\n"
                + sep(),
    )
    # collapse
    parser.add_argument(
        '-c',
        '--collapse',
        metavar='VALUE',
        required=False,
        help=
                "To use collapsing, add one or more collapse=field or\n" \
                "collapse=field:N where N is the first N characters of\n field to test.\n" \
                "Ex: --collapse digest - only show unique captures by\n digest (note that\n" \
                "only adjacent digest are collapsed, duplicates elsewhere\n in the cdx are not affected).\n" \
                "Ex: --collapse urlkey - only show unique urls in a prefix\n query (filtering out captures\n" \
                "except first capture of a given url). This is similar to\n the old prefix query in\n" \
                "wayback (note: this query may be slow at the moment).\n" \
                "timestamp:N - example: timestamp:10 - show at most 1\n capture per hour\n" \
                "(compare the first 10 digits of the timestamp field.\n" \
                "Default is 'urlkey'\n"
                + sep(),
    )
    # field order
    parser.add_argument(
        '-o',
        '--order',
        nargs='+',
        required=False,
        help=
                "\nField order - specifies which fields to return.\n" \
                "Valid options: key, timestamp, url, mimetype, statuscode,\n" \
                "digest, flags, length, offset, filename.\n\n" \
                "Fields should be space-separated.\n" \
                "Default is return all fields if argument is omitted.\n"
                + sep(),
    )
    # inlude mimetypes
    parser.add_argument(
        '-i',
        '--include',
        metavar='mimetype',
        required=False,
        help=
                "Return only this mimetype.\n" \
                "Example: --include text/html\n" \
                "Default is all types shown if omitted.\n"
                + sep(),
    )
    # exclude mimetypes
    parser.add_argument(
        '-e',
        '--exclude',
        metavar='mimetype',
        required=False,
        help=
                "Exclude this mimetype from results.\n" \
                "Example: --exclude text/html\n"
                + sep(),
    )
    # limit first
    parser.add_argument(
        '-l',
        '--limit',
        metavar='NUMBER',
        required=False,
        help=
                "Limit to first/last N results.\n" \
                "Example (limit first 100): --limit 100\n" \
                "Example (limit last 50):   --limit -50\n"
                + sep(),
    )
    # exclude HTTP status
    parser.add_argument(
        '-x',
        '--no-stat',
        metavar='HTTP_STATUS_CODE',
        required=False,
        help=
                "Exclude results with this HTTP status code.\n" \
                "Example: --no-stat 404\n"
                + sep(),
    )
    # include HTTP status
    parser.add_argument(
        '-y',
        '--yes-stat',
        metavar='HTTP_STATUS_CODE',
        required=False,
        help=
                "Show only results with this HTTP status code.\n" \
                "Example: --yes-stat 200\n"
                + sep(),
    )
    # fast latest
    parser.add_argument(
        '-fast',
        '--fastlatest',
        action='store_true',
        required=False,
        help=
                "May be set to return some number of latest\n" \
                "results for an exact match and is faster than \n" \
                "the standard last results search. \n" \
                "Use with --limit\n"
                + sep(),
    )
    # regex
    parser.add_argument(
        '-r',
        '--regex',
        metavar='[!]field:regex',
        required=False,
        help=
                "field is one of the named CDX fields (listed in \n" \
                "the JSON query) or an index of the field.\n" \
                "Optional ! before query will return results that \n" \
                "do NOT match the regex. Regex is any standard \n" \
                "Java regex pattern. Entire value should be enclosed\n" \
                "in single quotes. Example: --regex='!field:regex' \n"
                + sep(),
    )
    # skip count
    parser.add_argument(
        '--showskipcount',
        action='store_true',
        required=False,
        help=
                "It is possible to track how many CDX lines were\n" \
                "skipped due to Filtering and Collapsing by adding\n" \
                "the special skipcount counter with --showskipcount.\n" \
                "An optional endtimestamp count can also be used to\n" \
                "print the timestamp of the last capture by adding:\n" \
                "--lastskiptimestamp.\n"
                + sep(),
    )
    # skip timestamp
    parser.add_argument(
        '--lastskiptimestamp',
        action='store_true',
        required=False,
        help=
                "See above.\n"
                + sep(),
    )
    # dupe count
    parser.add_argument(
        '--showdupecount',
        action='store_true',
        required=False,
        help=
                "Using showDupeCount will only show unique captures.\n"
                + sep(),
    )

    global args
    args = vars(parser.parse_args())

    ###################################
    ##  check output file
    ##

    if args['out'] != None:
        global outputFile
        checkFileExistence(args['out'])  # check if file exists
        outputFile = args['out']         # assign filename to var
        del args['out']                  # delete the key from dictionary
    else:
        outputFile = ""

    ###################################
    ##  Syntax checking
    ##   
        
    # --order choices is handled here instead because argparse is messy.
    if args['order'] != None:
        orderChoices=[
                        'key',
                        'timestamp',
                        'url',
                        'mimetype',
                        'statuscode',
                        'digest',
                        'flags',
                        'length',
                        'offset',
                        'filename',
        ]
        for option in args['order']:
            if option not in orderChoices:
                print(
                        "Error: --order must only contain the " \
                        "following space-separated values:\n" \
                        "key, timestamp, url, mimetype, statuscode, digest, " \
                        "flags, length, offset, filename."
                )  # note: 'url' is changed later in code to actual 'original' param
                sys.exit(1)

    if args['include'] != None or args['exclude'] != None:
        if (args['include']) and (args['exclude']):
            print(
                    "Error: --include and --exclude cannot be " \
                    "used at the same time."
            )
            sys.exit(1)

    if args['to'] != None and args['from'] != None:
        if int(args['to']) - int(args['from']) < 0:
            print(
                    "Error: --to date is less than --from date."
            )
            sys.exit(1)

    if args['yes_stat'] != None or args['no_stat'] != None:
        if args['yes_stat'] != None and args['no_stat'] != None:
            print(
                    "Error: --yes-stat and --no-stat cannot be " \
                    "used at the same time."
            )
            sys.exit(1)


    # check date (timestamp).
    try:  # try to convert to int, if fail it's not so exit
        if args['to'] != None:
            toDateInt = int(args['to'])
        if args['from'] != None:
            fromDateInt = int(args['from'])
    except:
        print("Error: Dates must be integers.\n")
        sys.exit(1)

    # check date format
    if args['to'] != None:
        if int(args['to']) < 1000:
            print(
                    "Error: date must be 4-14 digits.\n"
            )
            sys.exit(1)

    # check date format
    if args['from'] != None:
        if int(args['from']) < 1000:
            print(
                    "Error: date must be 4-14 digits.\n"
            )
            sys.exit(1)

    ##################################
    ##  Special argument handling
    ##  these args become variables

    global inexclude  # str
    inexclude = None

    global regex  # str
    regex = None

    # mimetypes
    if args['include'] != None:
        inexclude = "mimetype:" + str(args['include'])
        del args['include']  # we don't need it in the dictionary after this
    if args['exclude'] != None:
        inexclude = "!mimetype:" + str(args['exclude'])
        del args['exclude']

    # --regex
    if args['regex'] != None:
        regex = args['regex']  # assign to var for later
        del args['regex']  # we don't need it in the dictionary after this

    # remove scheme from URL being searched, encode if it contains params
    if args['url'] != None:

        if (
               "http://" in args['url'] or
               "https://" in args['url']
        ):
            if "http://" in args['url']:
                args['url'] = args['url'].replace("http://", "")
            if "https://" in args['url']:
                args['url'] = args['url'].replace("https://", "")

    if "/" in args['url']:  # if / after we stripped scheme
        if args['matchtype'] == None:
            print(
                "/ found in URL. You should likely be using the argument -m prefix \n"
                "if the URL looks like: example.com/something/ instead of example.com\n"
                "Otherwise, remove the slash to avoid this message.\n"
            )
            sys.exit(0)

    if "?" in args['url']:  # if URL contains a query we must encode it.
        args['url'] = urllib.parse.quote_plus(args['url'])

    ###################################
    ##  Set default params
    ##
    ##  for ease of use

    args['output'] = 'json'
    args['gzip'] = 'false'

    if args['matchtype'] == None:  # pay attn to letter case
        args['matchType'] = 'domain'
        del args['matchtype']
    else:
        args['matchType'] = args['matchtype']
        del args['matchtype']

    if args['fastlatest'] == False:  # pay attn to letter case
        del args['fastlatest']
    else:
        args['fastLatest'] = 'true'
        del args['fastlatest']

    if args['showskipcount'] == False:  # pay attn to letter case
        del args['showskipcount']
    else:
        args['showSkipCount'] = 'true'
        del args['showskipcount']

    if args['lastskiptimestamp'] == False:  # pay attn to letter case
        del args['lastskiptimestamp']
    else:
        args['lastSkipTimestamp'] = 'true'
        del args['lastskiptimestamp']

    if args['showdupecount'] == False:  # pay attn to letter case
        del args['showdupecount']
    else:
        args['showDupeCount'] = 'true'
        del args['showdupecount']

    if args['collapse'] == None:  # set default "urlkey"
        args['collapse'] = 'urlkey'

    # if we didn't specify statuscode or order, we'll specify fields to return
    # so that it's quicker. We don't need statuscode field because if not
    # specified, the default statuscode when not specified is http 200,
    # so it is pointless to not use this.
    if args['no_stat'] == None or args['yes_stat'] == None:
        if args['order'] == None:
            args['order'] = ['timestamp', 'url']

    if args['yes_stat'] == None:   # set default http 200 status
        args['filter'] = 'statuscode:200'
        del args['yes_stat']

    try:  # try because if 'None', key will be deleted and this will throw exception
        if args['yes_stat'] != None:
            args['filter'] = "statuscode:" + str(args['yes_stat'])
            del args['yes_stat']
    except:
        pass

    if args['no_stat'] != None:
        args['filter'] = "!statuscode:" + str(args['no_stat'])
        del args['no_stat']

    # build order parameter
    if args['order'] != None:
        # replaces "url" with proper param name "original" for user-friendliness:
        orderList     = ['original' if x=='url' else x for x in args['order']]
        orderList     = ','.join(orderList)  # comma sep. list
        args['order'] = orderList            # assign list to key
        args['fl']    = args.pop('order')    # rename key

    # clean up anything else set to None or False so they don't end up as params
    global filtered  # dict.
    filtered = {k: v for k, v in args.items() if v is not None}
    filtered = {k: v for k, v in filtered.items() if v is not False}


 ########################################
  ####  FILE NAMES
   ###
    ##
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


 ########################################
  ####  URL CONSTRUCTION
   ###
    ##
def constructURL():

    global URL  # str.  final URL
    
    searchurl = "https://web.archive.org/cdx/search/cdx?"
    
    mainParams = filtered  # modified dict with no 'None' or 'False' values
    mainParams = urlencode(mainParams)
    parameters = mainParams

    # The CDX API needs different occurrences of "filter" for each 
    # filter and dictionaries can't share the same key.
    # So, we will handle it separately and add it to
    # the URL manually after everything else has been done. Order
    # doesn't matter. Less confusing to me to handle it this way.

    # if both --include or --exclude and --regex:
    if inexclude != None and regex != None:
        addonParams1 = "&filter=" + str(inexclude)
        addonParams2 = "&filter=" + str(regex)
        parameters = mainParams + addonParams
    else:  # check if only one was specified
        if inexclude !=None:                           # if --include or --exclude
            addonParams = "&filter=" + str(inexclude)  # contruct parameter string
            parameters = mainParams + addonParams      # concatenate old + new
    
        if regex != None:
            addonParams = "&filter=" + str(regex)
            parameters = mainParams + addonParams

    
    encodedURL = parameters           # URL with percent encoding
    rawURL     = unquote(encodedURL)  # URL without percent encoding
    URL        = searchurl + rawURL   # final URL


 ########################################
  ####  Convert API response
   ###  Turn the JSON response into one dictionary per line.
    ##  The result is still valid JSON.
def cdxToDict(cdx_response):

    n = json.loads(cdx_response)
    
    keys = []  # holds JSON keys
    for i in n[0]:
        keys.append(i)  # add the keys to the list
    
    x = [dict(zip(keys, l)) for l in n]  # create list of dictionaries
    x.pop(0)  # remove first line containing JSON keys
    
    final_out = '[\n' + ',\n'.join(json.dumps(i) for i in x) + '\n]'  # format list

    return(final_out)


 ########################################
  ####  FETCH RESPONSE
   ###
    ##
def fetchResponse():

    timeoutSEC = 120  # http timeout in seconds

    if args["url"] != None:  # create a unique filename

        print("Fetching: " + URL)
        print("Timeout set to: " + str(timeoutSEC) + " seconds")
        print("Fetching the response may take a long time, do not stop the program...")

        # construct user agent header
        clientVersion = "cdx-query/" + version
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

        print(response.status_code, response.reason)

        status_code = str(response.status_code)
        if status_code != "200":  # exit unless 200
            print("Received HTTP status: " + status_code)
            sys.exit(0)

        with open('cdx.tmp', 'w') as f:  # save in case it crashes processing
            f.write(str(response.content))

        print("Request complete. Saved to temp file cdx.temp. Processing...")

        cdx_out = cdxToDict(response.text)

        if outputFile != "":

            print("Saving as: " + outputFile)

            with open(outputFile, 'w') as out_file:  # save it
                out_file.write(cdx_out)

                print("Done.")  


 ########################################
  ####  MAIN
   ###
    ##
def main():

    logging.basicConfig(
        format="%(pathname)s line%(lineno)s: %(message)s",
        level=logging.INFO
    )

    setup()
    constructURL()
    fetchResponse()

    executionTime = (time.time() - startTime)
    
    print(
            "\nExecution time: "
            + str(executionTime)
            + " seconds"
    )



if __name__ == '__main__':
    main()
