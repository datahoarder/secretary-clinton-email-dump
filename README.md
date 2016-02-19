# Analyzing Secretary Hillary Clinton's Emails

The Wall Street Journal has done an excellent service by downloading the individual email files from the State Department's listing and making them [accessible via their own search app](http://graphics.wsj.com/hillary-clinton-email-documents/). Even better, they've packaged the emails in convenient zip files.


# Getting your own copies of the Clinton emails

To get the data yourself, run the [getdata.py](getdata.py) via the command-line interpreter: 

~~~
$ python getdata.py
~~~

Here's what happens:

- The landing page for [WSJ's document search is downloaded](http://graphics.wsj.com/hillary-clinton-email-documents/), via the __Requests__ library.
- The HTML is parsed via the __lxml__ library, and the footnote links are extracted.
- The URLs from each link is extracted, e.g.
  
        http://graphics.wsj.com/hillary-clinton-email-documents/zips/Clinton_Email_August_Release.zip

- A local filename is derived from the URL, e.g.

        ./data/docs/zips/Clinton_Email_August_Release.zip

- If the zip file doesn't exist locally, it is downloaded.
- Every zip file is unpacked into its own separate directory of pdfs.
- Each PDF is processed via __pdftotext__ (from the Poppler library), and the raw text (which is embedded in each PDF by the State Department's optical-character-recognition software) is extracted into its own text file.
find ./data/docs/text/ -name "**/*.txt" -print0 | xargs


# Searching the Clinton emails

Use __grep__ to look for patterns (though I prefer __ag__, the silver searcher, for more regex power):

### Dollar amounts

~~~sh
ag '\$\d+' data/docs/text/HRC_Email_296/*.txt
~~~

    data/docs/text/HRC_Email_296/C05739846.txt
    43:             Department is asking permission from Congress to transfer $1.3 billion from funds that had been allocated for
    44:             spending in Iraq. This includes $553 million for additional Marine security guards; $130 million for diplomatic
    45:             security personnel; and $691 million for improving security at installations abroad.

    data/docs/text/HRC_Email_296/C05739864.txt
    107:                     families by providing payments of 2,000 Dinars (approximately $1,500) per month to
    243:                      militiamen and their families by providing payments of 2,000 Dinars (approximately $1,500) per


### Ignore emails that include articles

~~~sh
$ ag 'Associated Press|New York Times|Washington Post' \
      -L data/docs/text/HRC_Email_296/*.txt
~~~

## Grep all the emails

~~~sh
$ ag -i 'benghazi' data/docs/text
~~~



# Extract the senders' email address and find top 10 senders

~~~sh
$ find data/docs/text/ -name "*.txt" -print0 \
     | xargs -0 ag -o --noheading --nofilename '^From: {3,}.+' \
     | ag -o '(?<=<).+?(?=>)' \
     | tr [:upper:] [:lower:]  \
     | tr -d ' ' \
     | LC_ALL=C sort \
     | LC_ALL=C uniq -c \
     | LC_ALL=C sort -rn \
     | head 10
~~~

Result:

~~~
7270 hrod17@clintonemail.com
3923 millscd@state.gov
3017 abedinh@state.gov
2782 sullivanjj@state.gov
 626 jilotylc@state.gov
 498 hanleymr@state.gov
 396 valmorou@state.gov
 291 sullivann@state.gov
 257 colemancl@state.gov
 242 millscd?state.gov
~~~

What's with the `LC_ALL=C` in the previous command? Apparently the text encoding isn't all quite right. Without the flag, you will get this error:


      sort: string comparison failed: Illegal byte sequence
      sort: Set LC_ALL='C' to work around the problem.
      sort: The strings compared were `abedinh\342\251state.gov' and `abedinh@state.gov'.
