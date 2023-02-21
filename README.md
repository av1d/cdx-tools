# cdx-tools
A collection of tools for working with the Wayback Machine CDX server.
The best way to understand it is to issue the --help argument or [read this](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md)

If you find a bug or something can be made better don't hesitate to tell me.
This software is currently private and still in testing, do not distribute it to anybody.

Quick start:

`python cdq.py --url alice.org --out alice.txt`

`python cdf.py -i alice.txt --scan=.exe,.zip --make-list files.txt`

Then you can download the files with wget using something like:

`wget --convert-links -x -nH --cut-dirs=2 -i files.txt`

Tip: rename the files to cdq and cdf then chmod +x and place in /usr/local/bin so you can activate them from any directory by just typing cdq or cdf.
