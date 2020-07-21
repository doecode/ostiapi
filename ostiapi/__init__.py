import requests
import xml.etree.ElementTree as ET
import dicttoxml
from collections import defaultdict
import sys


# basic configuration; modify for other posting environments
this = sys.modules[__name__]
# default value is for production API endpoint
this.url = 'https://www.osti.gov/elink/'


# call this function for posting to OSTI API testing URL
def testmode():
    this.url = 'https://www.osti.gov/elinktest/'


# Define some helpfully-named Exceptions for API issues
class APIException(IOError):
    """ Error or Exception handling a particular request. """

    def __init__(self, *args):
        super(IOError, self).__init__(*args)


class NotFoundException(APIException):
    """ Record not on file. """


class ForbiddenException(APIException):
    """ Access was forbidden. """


class ServerException(APIException):
    """ Unknown internal server error. """


class UnauthorizedException(APIException):
    """ Unauthorized access attempted. """



def record_to_xml(name):
    """ Utility function to translate object names to XML tags. """
    if name == 'authors':
        return 'author'
    elif name == 'related_identifiers':
        return 'detail'
    elif name == 'records':
        return 'record'
    else:
        return name


def datatoxml(data):
    """
    Translate data dictionary to ELINK XML request.

    :param data: the data dictionary to transform
    :return: an OSTI-formatted XML API request
    """
    return dicttoxml.dicttoxml(data,
                               custom_root='records',
                               attr_type=False,
                               item_func=record_to_xml)


def reserve(data, username=None, password=None):
    """
    Special post to reserve a dataset DOI.

    If title is not provided, a placeholder will be used; it is 
    encouraged that more metadata should be provided if possible.

    Returns dictionary containing "osti_id" and "doi" values that should
    be retained.  In order to activate a reserved DOI, the "osti_id" and
    additional required metadata should be sent through the post() method.

    Return example:
    {"record":{"osti_id":9999, "doi":"10.5072/9999", "doi_status":"PENDING"}}

    """
    if ('title' not in data):
        data['title'] = "Placeholder Dataset Title"
    
    data['set_reserved'] = "true"

    return post(data, username, password)


def post(data, username=None, password=None):
    """
    Post python data dictionary to ELINK API.

    Required key names (fields):
    title
    publication_date
    contract_nos
    creators (or authors array of author objects)
    site_url
    dataset_type

    optional:
    site_input_code (required if user has multiple-site access)
    keywords
    description
    related_identifiers (array of identifier objects)
    doi_infix
    accession_num (unique identifier from client site)
    sponsor_org
    research_org

    It is important to note one should check the returned dict for the key value 'status'
    to ensure this is 'SUCCESS'.  If not, the error message information should be obtained
    from the 'status_message' key on the returned result.

    :param data: a list of data dictionary records to post
    :param username: the ELINK user name
    :param password: the ELINK account password
    :return: a dictionary containing the ELINK response if successful
    :raises: ForbiddenException if account is invalid, ServerException if there is a general service error,
    UnauthorizedException if no user account information is supplied
    """

    # ELINK POST expects an array of records
    records = []
    records.append(data)

    # post XML to ELINK API
    elink = requests.post(this.url + '2416api',
                          data=datatoxml(records),
                          auth=(username, password))

    # Check ELINK response code for more information
    # 200 = request OK, check XML status for more information
    # 401 = no authentication context found (UNAUTHENTICATED)
    # 403 = user account login error (FORBIDDEN)
    # 500 = ELINK service error (INTERNAL_SERVER_ERROR)
    #
    if elink.status_code == 200:
        return etree_to_dict(ET.fromstring(elink.content))['records']
    elif elink.status_code == 401:
        raise UnauthorizedException('No user account information supplied.')
    elif elink.status_code == 403:
        raise ForbiddenException('User account failed login or authentication.')
    else:
        raise ServerException('ELINK service is not available or unknown connection error.')


def etree_to_dict(t):
    """
    Simple function to translate an XML expression into a dict.

    :param t: the XML etree object
    :return: a dict containing the XML information
    """
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        # treat DOI attributes differently for readability
        if ("doi"==t.tag):
            for k,v in t.attrib.items():
                d["doi_"+k] = v
        else:
            d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag] = text
        else:
            d[t.tag] = text
    return d


def get(id, username=None, password=None):
    """
    Acquire a single OSTI record as a python dict.

    :param id: the OSTI ID to look for
    :param username: the ELINK account user name
    :param password: the ELINK account password
    :return: a dict containing the record metadata if found
    """
    elink = requests.get(this.url + '2416api?osti_id=' + str(id),
                         auth=(username, password))

    if elink.status_code == 200:
        xml = ET.fromstring(elink.content)

        return etree_to_dict(xml)['records']
    elif elink.status_code == 403:
        raise ForbiddenException('User does not have access to this record.')
    elif elink.status_code == 404:
        raise NotFoundException('Record is not on file.')
    else:
        raise ServerException('Unknown HTTP status code: ' + str(elink.status_code))
