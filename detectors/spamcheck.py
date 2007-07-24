"""
spamcheck.py - Auditor that consults a SpamBayes server and scores all form
submissions.  Submissions which are deemed to be spam are rejected.  For the
time being only reject submissions which are assumed to be spam (score >=
SPAM_CUTOFF).  Once a reasonable body of ham and spam submissions have been
built up you can consider whether to also reject unsure submissions (score >
HAM_CUTOFF).  The current settings make it less likely that you'll reject
valid submissions at the expense of manual checks to correct spammy items
which snuck by the screen.
"""

import xmlrpclib
import socket

from roundup.exceptions import Reject

def check_spam(_db, _klass, _nodeid, newvalues):
    """Auditor to score a website submission."""

    spambayes_uri = _db.config.detectors['SPAMBAYES_URI']
    spam_cutoff = float(_db.config.detectors['SPAMBAYES_SPAM_CUTOFF'])


    server = xmlrpclib.ServerProxy(spambayes_uri, verbose=False)
    try:
        prob = server.score(newvalues, [], {})
    except (socket.error, xmlrpclib.Error), e:
        pass
    else:
        if prob >= spam_cutoff:
            raise Reject("Looks like spam to me - prob=%.3f" % prob)

def init(database):
    """Initialize auditor."""
    database.issue.audit('create', check_spam)
    database.issue.audit('set', check_spam)
    database.file.audit('create', check_spam)
    database.file.audit('set', check_spam)
