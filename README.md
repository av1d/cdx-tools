# cdx-tools
A collection of tools for working with the Wayback Machine CDX server which ses only Python built-ins, no obscure modules required.
This set of tools allows you to heavily refine all results returned from any query.
These tools are focused for archivists and researchers seeking particular items but they implement most of the Wayback CDX server funcitons so you can do almost anything to the API besides pagination and resuming sessions.

The objective is to scan hosts for specific strings and filetypes in order to find items of interest.

Features: 
Query allows you to pull URLs from certain time ranges, HTTP status codes, mimetypes, with filtering by fields.
You can search subdomains, URL prefixes and apply regex to your searches. Output is saved as JSON.
Filter allows you to scan the output of 'query' and seek specific strings, mimetypes, URLs, HTTP status codes and so on.
It can generate HTML, plain text and JSON so the user can filter results repeatedly. The resulting text files are usable with wget.


The best way to fully understand it is to issue the --help argument or [read this](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md)

If you find a bug or something can be made better don't hesitate to post an issue / pull request.
This software is currently private and still in testing, do not distribute it to anybody.

Quick start:

`python cdq.py --url alice.org --out alice.txt`

`python cdf.py -i alice.txt --scan=.exe,.zip --make-list files.txt`

Then you can download the files with wget using something like:

`wget --convert-links -x -nH --cut-dirs=2 -i files.txt`

Tip: rename the files to cdq and cdf then chmod +x and place in /usr/local/bin so you can activate them from any directory by just typing cdq or cdf.

This project is not affiliated with The Internet Archive.
This software comes without warranty, use at your own risk.
