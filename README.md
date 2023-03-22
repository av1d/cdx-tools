# cdx-tools
A collection of tools for working with the Wayback Machine CDX server which uses only Python built-ins, no obscure modules required.
This set of tools allows you to heavily refine all results returned from any query.
These tools are focused for archivists and researchers seeking particular items but they implement most of the Wayback CDX server funcitons so you can do almost anything to the API besides pagination and resuming sessions.

The objective is to scan hosts for specific strings and filetypes in order to find items of interest.

There are currently 3 tools with distinct purposes: cdx-query, cdx-filter and cdxpress.

cdxpress is the short and sweet version to be used if you are quickly looking for a particular string on a domain. For example, you want to find all .exe and .zip files on example.org, or perhaps any occurrence of the word "cgi-bin", or both. This will only return results with HTTP 200 status (file is actually present).
cdxpress features:
* finds files and strings in URLs
* case insensitive / case sensitive search
* negative keywords (exclude word)
* writes output to plain text file and prints results to screen
* supports to/from Wayback Machine dates (4 digit years up to 14 digit timestamps)

An example to pull all .exe, .zip, .index.html and anything containing "/cgi-bin/" from example.org (fictitious example, doesn't actually pull these files):  
`cdxpress --url example.org --scan=.exe,.zip,index.html,"/cgi-bin/"`  

Unlike cdx-query and cdx-filter, cdxpress doesn't offer any control over any other parameters, advanced filtering or list generation.

cdx-query offers precise refinement over every parameter sent to the CDX server. It supports every function on the API except for the advanced features (pagination and resuming search by session).
It saves the output as valid JSON which can then be used with cdx-filter. The options are too numerous to list here, so just do `cdx-query --help` to see all available features.

cdx-filter is a poweful tool which offers an extremely high level of refinement of results. It can also process wayback_machine_downloader output files. It offers various types of list generation (plain text, HTML, JSON), has the ability to search through JSON fields, URL strings and much much more.
Again, the features are too numerous to list here, simply issue `cdx-filter --help` to see them all.


General features: 
cdx-query allows you to pull URLs from certain time ranges, HTTP status codes, mimetypes, with filtering by fields.
You can search subdomains, URL prefixes and apply regex to your searches. Output is saved as JSON.
Filter allows you to scan the output of 'query' and seek specific strings, mimetypes, URLs, HTTP status codes and so on.
It can generate HTML, plain text and JSON so the user can filter results repeatedly. The resulting text files are usable with wget.

cdx-filter allows you to highly refine anything, search JSON keys, return certain status codes, filenames, subhost enumeration and much more.
It outputs files compatible with itself so they can be re-refined.

The best way to fully understand either is to issue the --help argument or [read this](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md)

If you find a bug or something can be made better don't hesitate to post an issue / pull request.

Quick start for cdx-query & cdx-filter:

`python cdq.py --url alice.org --out alice.txt`

`python cdf.py -i alice.txt --scan=.exe,.zip --make-list files.txt`

Then you can download the files with wget using something like:

`wget --convert-links -x -nH --cut-dirs=2 -i files.txt`

Tip: rename the files to cdq and cdf then chmod +x and place in /usr/local/bin so you can activate them from any directory by just typing cdq or cdf.

Windows binaries will be made available soon.

This project is not affiliated with The Internet Archive.
This software comes without warranty, use at your own risk.
