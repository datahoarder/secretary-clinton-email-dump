# Analyzing Secretary Hillary Clinton's Emails

The Wall Street Journal has done an excellent service by downloading the individual email files from the State Department's listing and making them [accessible via their own search app](http://graphics.wsj.com/hillary-clinton-email-documents/). Even better, they've packaged the emails in convenient zip files.

Why do you need your own copies of the emails when the[ WSJ's application works so well](http://graphics.wsj.com/hillary-clinton-email-documents/)? It's a great tool, but it's still not as flexible as using regular expressions, which allow us to search by _pattern_, including:

- Look for all instances in which a `$` is followed by numbers (to quickly locate places where money is mentioned)
- Look for all instances of...anything...in which the email does _not_ include an article from the New York Times/Washington Post/WSJ/etc.
- Extract the "From:" field of each email to quickly find out who the most frequent senders were.

The algorithms in this repo are pretty general and can be replicated with any number of tools or languages. But to get my example code going, you should have:

- Python 3.5 (I use [Anaconda](https://www.continuum.io/downloads))
- [Requests](http://docs.python-requests.org/en/master/) for downloading the files (comes with Anaconda)
- [lxml](http://lxml.de/lxmlhtml.html) for simple HTML parsing
- [The PDF Poppler library](https://poppler.freedesktop.org/) so that we can use __pdftotext__ to extract the raw text from each PDF.

To search by regular expression, you can obviously use Python's library. But I like doing things via the command-line if possible, and [__ag__ (the Silver Searcher)](https://github.com/ggreer/the_silver_searcher) is my favorite version of __grep-like__ tools.


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

I recommend using __grep__ from the command-line to swiftly look for patterns (though I prefer [__ag__, the silver searcher](https://github.com/ggreer/the_silver_searcher), for more regex power). _Then_, when you've gotten the lay of the data (including how messy the optical-character-recognition translation was), you can write Python code to do more specific things.


### Search for "benghazi", case-insensitive, across all emails

~~~sh
$ ag -i 'benghazi' data/docs/text
~~~

Sample result:

    data/docs/text/HRCEmail_SeptemberWeb/C05785381.txt
    24:BENGHAZI (AP) - At first, the responses to the questionnaire about the trauma of the war in Libya were
    49:   The women said they had been raped by Gadhafi's militias in numerous cities and towns: Benghazi, Tobruk,
    70:   Doctors at hospitals in Benghazi, the rebel bastion, said they had heard of women being raped but had not


### Ignore emails that include news articles

We want emails that mention "benghazi" because the sender/recipient is actually discussing it, not just because they're sending each other news clippings.

Here's how to get a list of such filenames

~~~sh
$ ag 'Associated Press|New York Times|Washington Post|Reuters|\( *AP *\)' \
      -L data/docs/text
~~~

~~~
data/docs/text/Clinton_Email_August_Release/C05765907.txt
data/docs/text/Clinton_Email_August_Release/C05765911.txt
data/docs/text/Clinton_Email_August_Release/C05765917.txt
data/docs/text/Clinton_Email_August_Release/C05765915.txt
data/docs/text/Clinton_Email_August_Release/C05765918.txt
data/docs/text/Clinton_Email_August_Release/C05765922.txt
data/docs/text/Clinton_Email_August_Release/C05765931.txt
data/docs/text/Clinton_Email_August_Release/C05765923.txt
data/docs/text/Clinton_Email_August_Release/C05765928.txt
data/docs/text/Clinton_Email_August_Release/C05765933.txt
~~~

Pipe those filenames back into `ag`:

~~~sh
$ ag 'Associated Press|New York Times|Washington Post|Reuters|\( *AP *\)' \
      -L data/docs/text  \
  | xargs ag -i 'benghazi'
~~~

Sample output:

~~~
data/docs/text/HRCEmail_SeptemberWeb/C05784017.txt
13:Subject:                            Fw: Benghazi Sitrep - August 14, 2011
14:Attachments:                        Benghazi Sitrep - August 14 2011.docx; Benghazi Sitrep - August 14 2011.docx
26:Subject: Fw: Benghazi Sitrep - August 14, 2011
40:(SBU) Jibril to Return to Benghazi to Discuss Forming a New Government: A senior foreign ministry official told us that
41:PM Mahmoud Jibril is planning to return to Benghazi on/about August 17 to resume discussions on reconstituting the
57:Subject: Benghazi Sitrep - August 14, 2011
70:Attached for your information is the latest Benghazi sitrep from the Office of the U.S. Envoy to the Libyan Transitional
~~~

#### Remove emails with forwarded-content

A little better, but there's still a bit too much noise that comes from __forwarded__ emails...some of these forwards will contain useful content, but let's see what we get when we cut them out:

~~~sh
$ ag 'Associated Press|New York Times|Washington Post|Reuters|\( *AP *\)' \
      -L data/docs/text  \
  |  xargs ag -iL 'fwd?:' \
  |  xargs ag -i 'benghazi'
~~~

Here's some sample output that I noticed immediately:

~~~

data/docs/text/HRCEmail_SeptemberWeb/C05779634.txt
19:For what it is worth. I know Self al-Islam — once flew w/ him on his jet from Benghazi to London. I have obviously been

data/docs/text/HRCEmail_SeptemberWeb/C05780083.txt
37:Benghazi to coordinate opposition military activities, made contact with the newly formed
38:National Libyan Council (NLC) stating that the Benghazi military council would join the NLC
122:• Benghazi, Opposition forces are currently in possession of 14 fighter aircraft at the
123:   Benghazi Airport, but they have no pilots or maintenance crews to support them.
~~~


Let's just use good ol __head__ to see what the tops of these emails are all about -- note that I pipe into __grep__ to remove all blank lines for easier reading:

~~~sh
$  head -n 20 data/docs/text/HRCEmail_SeptemberWeb/C05779634.txt \
      | grep -v '^$'
~~~

Output (junk characters removed):

~~~
        UNCLASSIFIED U.S. Department of State Case No. F-2014-20439 Doc No. C05779634 Date: 09/30/2015
From:                                                  Anne-Marie Slaughter
Sent:                                                  Sunday, April 3, 2011 11:31 AM
To:
Cc:                                                   Mills, Cheryl D; Abedin, Huma; Sullivan, Jacob J
Subject:                                              just a thought
For what it is worth. I know Self al-Islam — once flew w/ him on his jet from Benghazi to London. I have obviously been
very vocal in support of intervention and against Gaddafi himself, so have some credibility w/ both sides. lilt would be

~~~

Seems benign, but at least it's not just a news clipping.

### Dollar amounts

A more generally useful pattern is looking for the dollar sign, plus any number of digits that immediately follow:

~~~sh
ag '\$\d+' data/docs/text
~~~

~~~
data/docs/text/HRC_Email_296/C05739846.txt
43:             Department is asking permission from Congress to transfer $1.3 billion from funds that had been allocated for
44:             spending in Iraq. This includes $553 million for additional Marine security guards; $130 million for diplomatic
45:             security personnel; and $691 million for improving security at installations abroad.

data/docs/text/HRC_Email_296/C05739864.txt
107:                     families by providing payments of 2,000 Dinars (approximately $1,500) per month to
243:                      militiamen and their families by providing payments of 2,000 Dinars (approximately $1,500) per
~~~

This would obviously benefit from filtering the emails that include news clippings, but you get the idea.


# Extract the senders' email address and find top 10 senders

A common angle in searching an email corpus is to find most-common senders or recipients. We don't need any fancy scripting, just a recognition of what makes an email address an email address.

Here's a typical header:

~~~
From:                              Mills, Cheryl D <MillsCD@state.gov>
~~~

So basically, a line that begins with `From:`...has a bunch of white space, and has the email inside angle brackets: `<MillsCD@state.gov>`

Here's a quick tryout:

~~~sh
$ ag -o --noheading --nofilename '^From: {3,}.+' data/docs/text \
  | head -n 10
~~~

Output:

~~~
From:                             Sullivan, Jacob J <SullivanJJ@state.gov>

From:                              Mills, Cheryl D <MillsCD@state.gov>

From:                               Abedin, Huma <AbedinH@state.gov>

From:                           Abedin, Huma <AbedinH@state.gov>

From:                             sbwhoeop
~~~


Pretty good. But some emails have the address redacted, i.e. `sbwhoeop`. For now, let's just try to capture the actual email addresses:

~~~sh
$ ag -o --noheading --nofilename '^From: {3,}.+' data/docs/text \
     | ag -o '(?<=<).+?(?=>)' \
     | tr [:upper:] [:lower:]  \
     | tr -d ' ' \
     | LC_ALL=C sort \
     | LC_ALL=C uniq -c \
     | LC_ALL=C sort -rn \
     | head -n 10
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


Of course, it's not the most frequent senders that are the most interesting...but also, the ones who only show up a few times...


~~~sh
$ ag -o --noheading --nofilename '^From: {3,}.+' data/docs/text \
     | ag -o '(?<=<).+?(?=>)' \
     | tr [:upper:] [:lower:]  \
     | tr -d ' ' \
     | LC_ALL=C sort \
     | LC_ALL=C uniq -c \
     | LC_ALL=C sort -rn \
     | tail -n 20
~~~

As you can see, the OCR quality wasn't perfect...but there are ways -- with a little more regex skill -- that we can filter out the junk:

~~~
   1 burnswl@state.gov
   1 burnsw.1@state.goy
   1 brod17@clintonemail.com
   1 brimmere@state.gov
   1 automailer.-093@nyc.gov
   1 andrea.palm@hhs.gov
   1 aidedinh@state.gov
   1 agorcj@state.gov
   1 adlerce@state.goy
   1 abedivid@state.gov
   1 abedink@state.gov
   1 abedinh?state,gov
   1 abedinhostate.gov
   1 abedinhdstate.gov
   1 abedinh@state.qov
   1 abedinh@state.go.v
   1 abedinh@state,gov
   1 abeclinh@state.gov
   1 1i
   1 1
~~~
