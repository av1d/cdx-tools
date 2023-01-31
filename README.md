# cdx-tools
A collection of tools for working with the Wayback Machine CDX server.
The best way to understand it is to issue the --help argument or [read this](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md)

If you find a bug or something can be made better don't hesitate to tell me.
This software is private, do not distribute it to anybody.

Quick start:

`python3 cdq.py --url alice.org --out alice.txt`

`python cdf.py -i alice.txt --scan=.exe,.zip --outfile files.txt`

Tip: rename the files to cdq and cdf then chmod +x and place in /usr/local/bin so you can activate them from any directory by just typing cdq or cdf.
