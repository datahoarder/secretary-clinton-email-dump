from os.path import join, basename, splitext, exists
from os import makedirs
from lxml import html
from urllib.parse import urljoin
from shutil import unpack_archive
from glob import glob
import requests
import subprocess

LANDING_PAGE_URL = 'http://graphics.wsj.com/hillary-clinton-email-documents/'
DATA_DIR = join(".", "data")
DOCS_DIR = join(DATA_DIR, "docs")
PDF_DIR = join(DOCS_DIR, 'pdf')
TEXT_DIR = join(DOCS_DIR, 'text')


def bx(txt):
    """
    returns a string highlighted for output
    """
    return '\033[1m' + txt + '\033[0m'

def bootstrap():
    """
    Make some directories
    """
    makedirs(DOCS_DIR, exist_ok=True)
    makedirs(TEXT_DIR, exist_ok=True)

def fetch(overwrite=False):
    """
    Fetch the zip files from WSJ
    """

    # Download the page
    resp = requests.get(LANDING_PAGE_URL)
    footnote_links = html.fromstring(resp.text).cssselect('.footnote a')
    for link in footnote_links:
        href = urljoin(LANDING_PAGE_URL, link.attrib['href'])
        if 'zips/' in href:
            zname = join(DOCS_DIR, basename(href))
            if not overwrite and exists(zname):
                print(bx("\tSkipping"), href)
                print(bx("\tAlready downloaded to:"), zname)
            else:
                print("Downloading", href)
                zipresp = requests.get(href)
                with open(zname, "wb") as zf:
                    zf.write(zipresp.content)
                    print(bx("\tSaved"), zname, "to disk...")


# Unzip the zips
def unpack():
    for zname in glob(join(DOCS_DIR, '*.zip')):
        print(bx("Unzipping"), zname)
        zdir = join(DOCS_DIR, 'pdfs', splitext(basename(zname))[0])
        unpack_archive(zname, extract_dir=zdir)

def pdftotext_is_installed():
    """
    Checks for existence of `pdftotext` on system
    Returns output of `pdftotext -v` if it does exist
    else, returns False
    """
    try:
        _ox = subprocess.run(["pdftotext", "-v"], stderr=subprocess.PIPE)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
        else:
            raise
    else:
        return _ox.stderr.decode('utf-8')


def extract_texts():
    """
    Runs pdftotext some-file.pdf -layout -
     on each PDF in PDF_DIR/
    """
    for pdfname in glob(join(PDF_DIR, '**', '*.pdf')):
        psubdir, pname = pdfname.split('/')[-2:]
        tsubdir = join(TEXT_DIR, psubdir)
        makedirs(tsubdir, exist_ok=True)
        xp = subprocess.run(['pdftotext',  pdfname, '-layout', '-'],
                             stdout=subprocess.PIPE)
        txt = xp.stdout.decode('utf-8')
        txtname = join(tsubdir, splitext(pname)[0]) + '.txt'
        if not exists(txtname):
            with open(txtname, 'w') as tf:
                tf.write(txt)
                print(bx("Extracted"), len(txt), "chars to:", txtname)
        else:
            print(bx("Skipping pdftotext:"), txtname)


if __name__ == "__main__":
    print(bx("Bootstrapping up the workspace..."))
    bootstrap()

    print(bx("Fetching files from source..."))
    fetch()

    print(bx("Unpacking the zip files..."))
    unpack()

    if not pdftotext_is_installed():
        print(bx("""
            You need to have pdftotext installed
            https://poppler.freedesktop.org/

            On OSX, you can install it with Homebrew:

            $ brew install pdftotext
            """))
    else:
        print(bx("Converting pdfs to texts..."))
        extract_texts()


