###
# Copyright 2012 doublerebel
# Licensed WTFPL
###

import socket
import urllib

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os

simplejson = None

try:
    simplejson = utils.python.universalImport('json')
except ImportError:
    pass

try:
    # The 3rd party simplejson module was included in Python 2.6 and renamed to
    # json.  Unfortunately, this conflicts with the 3rd party json module.
    # Luckily, the 3rd party json module has a different interface so we test
    # to make sure we aren't using it.
    if simplejson is None or hasattr(simplejson, 'read'):
        simplejson = utils.python.universalImport('simplejson',
                                                  'local.simplejson')
except ImportError:
    raise callbacks.Error, \
            'You need Python2.6 or the simplejson module installed to use ' \
            'this plugin.  Download the module at ' \
            '<http://undefined.org/python/#simplejson>.'


# This will be used to change the name of the class to the folder name
PluginName = os.path.dirname(__file__).split(os.sep)[-1]


class _Plugin(callbacks.Plugin):

    """Usage: @beatport <searchterms> genre: <genrename>"""
    threaded = True

    def beatport(self, irc, msg, args, things):
        """ <searchterms> [genre:<genrename>]
        
        Displays results from beatport.
        """
        opts = {}
        facets = []
        
        searchTerms = ' '.join(things)
        searchTerms = string.split(searchTerms, 'genre:')
        if searchTerms[1]:
            facets.append('genreName:' + string.capitalize(searchTerms[1].strip()))
        searchTerms = searchTerms[0].strip()
        
        searchurl = 'http://api.beatport.com/catalog/3/search'
        headers = utils.web.defaultHeaders

        # Construct a URL like:
        # http://api.beatport.com/catalog/3/search?query=anjunadeep&perPage=5&sortBy=releaseDate&facets[]=fieldType:track&genreName:Trance
        
        opts['query'] = searchTerms
        opts['perPage'] = botPort.numResults
        opts['sortBy'] = botPort.sortBy

        facets.append('fieldType:track')
        opts['facets'] = facets #'&'.join(facets)
        
        fd = utils.web.getUrlFd('%s?%s' % (searchurl,
                                           urllib.urlencode(opts)),
                                           headers)
        json = simplejson.load(fd)
        fd.close()

        if not json:
            irc.reply('Receiving JSON response from Beatport servers failed.')
            pass
        else:
            trackUrl = 'http://www.beatport.com/track/'
            for result in json.results:
                title = result['title'].encode('utf-8')
                url = trackUrl + result['slug'].encode('utf-8') + '/' + result['id'].encode('utf-8')
                out.append('%s %s' % (title, url))
        if out:
            irc.reply(' | '.join(out))
        else:
            irc.reply('No results for the Beatport search: ' + ' '.join(things))
    beatport = wrap(beatport, [many('anything')])


_Plugin.__name__ = PluginName
Class = _Plugin
