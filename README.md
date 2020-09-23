OSTI API Python Module
======================

Purpose
-------
To facilitate posting data set metadata to OSTI ELINK API to obtain DOIs, via python language interface.

The OSTI data set API is designed for use by US Department of Energy funding recipient researchers and laboratories to obtain DOIs [Digital Object Identifiers](https://doi.org/ "DOI.org home page") for data sets.  Documentation is available for the API at [OSTI's ELINK web site](https://www.osti.gov/elink/241-6api.jsp "241.6 API documentation").

Requirements
------------
The ostiapi.py library module requires publicly available support modules dicttoxml and the requests module.  To install these locally, use your system's pip (or pip3) python installer function.

    # install python libraries required to use this module
    $ pip3 install dicttoxml

    $ pip3 install requests

    # download this ostiapi.py module from github (here)

Usage
-----
There are three main functions in the ostiapi library for use by clients with existing ELINK user accounts.  Please contact OSTI to obtain credentials if you do not already have them.  OSTI staff can work with you to access the test and production environments as needed.

Accessible functions:
* *reserve(data, username, password)*
  Send minimal metadata in order to reserve a DOI value for upcoming data sets pre-publication.
* *post(data, username, password)*
  Send required metadata to OSTI in order to obtain a live published DOI for completed data sets, or update URL or other metadata information.
  An OSTI ID value or accession number (unique identifier provided by the client) is required in order to update existing records, and will be
  generated upon successful post or reserve call.
* *get(parameters, username, password)*
  Obtain metadata from OSTI for existing data sets.  If parameters (dict) is empty, all records
  will be returned.  Supported parameter key values below, which may be combined
  as desired. Note the returned object should contain elements '**@start**', '**@rows**', and '**@numfound**' indicating starting row index, number of rows
  in request set, and total number found respectively.

  | key | description |
  | -- | -- |
  | start | starting row index, from 0 (defaults to 0) |
  | rows | number of desired rows per request (defaults to 25) |
  | osti_id | query a single record by its OSTI ID |
  | status | One of "complete", "saved", or "pending"; by OSTI record status |
  | title | search text of titles |
  | author | search authors of records |
  | publication_date_from | find records published on or after indicated date (MM/DD/YYYY) |
  | publication_date_to | find records published on or before indicated date (MM/DD/YYYY) |
  | submit_date_from | find records submitted on or after indicated date (MM/DD/YYYY) |
  | submit_date_to | find records submitted on or before indicated date (MM/DD/YYYY) |
  | accession_num | find records by unique site-specific ID value |
  | status | find records by status: one of 'complete', 'saved', or 'pending' |
  | doi | find records by DOI value |
  | site_input_code | restrict records to a particular ELINK site code value |

Examples below are from the python3 interpreter, and have been tested on version 3.6.8 python.

    $ python3

``` python
    >>> import ostiapi
    """
    library defaults to production access, use testmode() to set to OSTI test servers
    """
    >>> ostiapi.testmode()
    """
    reserve a DOI for unpublished or in-process data set prior to publication if desired
    """
    >>> data=ostiapi.reserve({'title':'My upcoming dataset', 'accession_num':'sample-ds-0001'}, 'my-osti-account', 'my-osti-password')
    >>> data
    {'record':{'osti_id':'1509999', 'accession_num':'sample-ds-0001', 'product_nos':None, 'contract_nos':None, 'title':'My upcoming dataset', 'doi':'10.5072/1509999','doi_status':'RESERVED', 'status':'SUCCESS', 'status_message':None, '@status':'NEW'}}

    """
    Note the data['record']['osti_id'] value for later update of the data set
    if accession_num is provided, it may be used in place of osti_id
    Ensure the value of data['record']['status'] is 'SUCCESS' to indicate the record was accepted and stored properly;
    if not, the data['record']['status_message'] value should detail any errors or metadata validation issues.
    """

    """
    Retrieve first set of all records from OSTI.
    """
    >>> ostiapi.get({}, 'my-osti-account', 'my-osti-password')
    {'record':[{'osti_id':'11509999', ... }], '@start':0, '@rows':1, '@numfound':1}
```

Reserved DOI values are not minted with DataCite, but intended as placeholders until such time as the data set is ready for publication.  Once this is the case, you may update the existing DOI reservation record by "osti_id" or "accession_num" value via the ostiapi.post() method, providing additional required metadata fields in order to complete the submission.  Upon receiving a SUCCESS on the post() operation, the DOI should be minted an live with DataCite within 24 to 48 hours.

Required and optional metadata fields are detailed below, and should be passed as the data dictionary argument of the ostiapi.post() function in order to mint a data set DOI with OSTI.

Required Metadata Fields
------------------------
The ostiapi.post(data, username, password) function requires at least the following keys be present in the "data" dictionary argument.

| key name | description |
| -- | -- |
| title | A title for the data set |
| dataset_type | A content type designating the primary type of data in the data set (see below) |
| creators OR authors | Either "creators" value, consisting of a string of author "last, first" values semi-colon delimited, OR "authors" with more complete details (see below) |
| publication_date | The data set publication date, in MM/DD/YYYY format |
| site_url | URL linking to data set landing page content for DOI destination |
| contract_nos | DOE contract numbers for funding identification from OSTI |
| sponsor_org | The sponsoring organization name |

Additional metadata details are encouraged to aid in data set discoverability with various search services.  The recognized fields are shown below.

| key name | description |
| -- | -- |
| keywords | Semi-colon delimited set of key words or phrases for the data set |
| description | An abstract or description of the data set |
| accession_num | A site-specified unique identifier to optionally identify the record |
| research_org | The name of the researching organization |
| doi_infix | Optionally specify an intermediate string for DOI construction.  Will be inserted between prefix and suffix of the generated DOI. |
| product_nos | Product or report numbers assigned to this data set |
| other_identifying_numbers | Any other non-report or contract numbers as applicable, semi-colon delimited list |

Data set content type values
----------------------------
Codes describing the primary make up of the data set.

| code | description |
| -- | -- |
| AS | Animations/Simulations |
| GD | Genome/Genetic Data (such as gene sequences) |
| IM | Interactive data maps, such as GIS data and/or shape files |
| ND | Numeric Data |
| IP | Still images or photos |
| FP | Figures/Plots, charts and diagrams |
| SM | Specialized Mix of differing data types |
| MM | Multimedia, such as videos of experiments |
| I	| Instrument |

Author Details
--------------
Additional information about creators or authors may be provided via an array of "authors" details specified as indicated below.  This includes email contact addresses, and ORCID values if applicable.

Example:
``` python
    >>> data['authors']=[{'first_name':'Neal', 'last_name':'Ensor', 'affiliation_name':'DOE OSTI', 'private_email':'ensorn@osti.gov', 'orcid_id':'0000-0001-5166-5705'}]
```

| key name | description |
| -- | -- |
| first_name | Given or first name of author |
| last_name | Family or last name of author |
| affiliation_name | Facility or lab affiliation of author |
| private_email | Contact email for this author |
| orcid_id | ORCID assigned to this author |
