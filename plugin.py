###
# Copyright 2012 doublerebel
# Licensed WTFPL
###

import os
import re
import urllib

import supybot.utils as utils
from supybot.commands import *
import supybot.callbacks as callbacks

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

    """Usage: @beatport [preview] <searchterms> [genre:<genrename>,
    artist:<artistname>, track:<trackname>, otherfacet:<value>]"""
    threaded = True

    def queryBeatport(self, irc, msg, args, things):
        opts = {}
        facets = []
        
        searchTerms = ' '.join(things).lower()
        reKeywords = '^([\s\-+_a-zA-Z0-9&]+)'
        reFacets = '((?:genre|artist|track):\s?[\-+_a-zA-Z0-9&]+)'
        
        for match in re.findall(reFacets, searchTerms):
            match = match.split(':')
            facet = match[0]
            # API accepts '+' for space character and expects each word of a facet to be capitalized
            value = '+'.join([word.capitalize() for word in match[1].strip().split('+')])
            if facet == 'genre':
                if value == 'Drum&bass' or value == 'Drum-and-bass' or value == 'D&b' or value == 'Dnb':
                    facets.append('genreId:1') # workaround for broken Drum & Bass API call
                else:
                    facets.append('genreName:' + value)
            elif facet == 'artist':
                facets.append('artistName:' + value)
            elif facet == 'track':
                facets.append('trackName:' + value)
            else:
                facets.append(facet + ':' + value)

        searchPattern = reKeywords
        if len(facets):
            searchPattern += reFacets
        match = re.search(searchPattern, searchTerms)
        if match:
            opts['query'] = match.group(1).strip()

        searchurl = 'http://api.beatport.com/catalog/3/search'
        headers = utils.web.defaultHeaders

        # Construct a URL like:
        # http://api.beatport.com/catalog/3/search?query=anjunadeep&perPage=5&sortBy=releaseDate&facets[]=fieldType:track&facets[]=genreName:Trance
        
        opts['perPage'] = self.registryValue('numResults')
        opts['sortBy'] = self.registryValue('sortBy')

        facets.append('fieldType:track')
        params = urllib.urlencode(opts) + '&facets[]=' + '&facets[]='.join(facets)
        
        print '%s?%s' % (searchurl, params)

        fd = utils.web.getUrlFd('%s?%s' % (searchurl,
                                           params),
                                           headers)
        json = simplejson.load(fd)
        fd.close()

        return json

    def beatport(self, irc, msg, args, things):
        """ [preview] <searchterms> [genre:<genrename>, artist:<artistname>,
        track:<trackname>, otherfacet:<value>]
        
        Displays results from beatport.

        '+' may be used as a space character in keywords and artist and genre names.
        For more specifying facets, see documentation at:
        http://api.beatport.com
        """
        preview = things[0] == 'preview' and things.pop(0)
        json = self.queryBeatport(irc, msg, args, things)

        if not json:
            irc.reply('Receiving JSON response from Beatport servers failed.')
            pass
        else:
            trackUrl = 'http://www.beatport.com/track/'
            out = []
            for result in json['results']:
                if 'title' in result:
                    artists = []
                    for artist in result['artists']:
                        if artist['type'] == 'artist':
                            artists.append(artist['name'])
                    artists = ', '.join(artists)
                    title = result['title'].encode('utf-8')
                    if preview:
                        url = result['sampleUrl'].encode('utf-8')
                    else:
                        url = trackUrl + result['slug'].encode('utf-8') + '/' + str(result['id']).encode('utf-8')
                    out.append('%s - %s %s' % (artists, title, url))
        if out:
            irc.reply(' | '.join(out))
        else:
            irc.reply('No results for the Beatport search: ' + ' '.join(things))
    beatport = wrap(beatport, [many('anything')])


_Plugin.__name__ = PluginName
Class = _Plugin
