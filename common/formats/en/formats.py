from __future__ import unicode_literals
"""
This file defines custom formats for 'en' language
Initially used to define spanish date formats
"""

DATE_FORMAT = 'j N Y'

DATE_INPUT_FORMATS = [
    '%d-%m-%Y', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%d%m%y', '%d%m%Y',                 # '25102006', '251006'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
]

SHORT_DATE_FORMAT = 'd-b-y'
