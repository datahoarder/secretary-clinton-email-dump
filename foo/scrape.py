# https://github.com/wsjdata/clinton-email-cruncher/blob/master/generatePDFList.py
# https://github.com/wsjdata/clinton-email-cruncher/blob/master/downloadMetadata.py
import json
import re
import requests
from urllib.parse import urljoin

STATE_GOV_FOIA_QUERY_ENDPOINT = "https://foia.state.gov/searchapp/Search/SubmitSimpleQuery"
STATE_GOV_SEARCHAPP_ROOT = 'https://foia.state.gov/searchapp/'
COLLECTION_NAME = 'Clinton_Email'

def fetch_foia_records_data(start=0,limit=1000,page=1):
    """
    Fetch the data from state.gov's search app
    Returns a dictionary

    Most of this code comes from:
    https://github.com/wsjdata/clinton-email-cruncher/blob/master/downloadMetadata.py
    """

    params = {"searchText": "*",
    "beginDate": "false",
    "endDate": "false",
    "collectionMatch": "Clinton_Email",
    "postedBeginDate": "false",
    "postedEndDate": "false",
    "caseNumber": "false",
    "page": page,
    "start": start,
    "limit": limit}

    request = requests.get(STATE_GOV_FOIA_QUERY_ENDPOINT, params=params)

    respjson = request.text
    # via: https://github.com/wsjdata/clinton-email-cruncher/blob/master/downloadMetadata.py
    # date objects not valid json, extract timestamp
    respjson = re.sub(r'new Date\(([0-9]{1,})\)',r'\1',respjson)
    #negative dates are invalid, and can sometimes be shown as newDate()
    respjson = re.sub(r'new ?Date\((-[0-9]{1,})\)',r'null',respjson)

    return json.loads(respjson)


def fetch_pdf_url_data(*args):
    """
    Same as fetch_foia_records_data() but prepends the
      root path for the pdfLink
    """
    data = fetch_foia_records_data(*args)
    for r in data['Results']:
        r['pdfLink'] = urljoin(STATE_GOV_SEARCHAPP_ROOT, r['pdfLink'])
    return data


## TODO: Paginate through the data
