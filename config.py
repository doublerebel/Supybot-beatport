###
# Copyright 2012 doublerebel
# Licensed WTFPL
###

import supybot.conf as conf
import supybot.registry as registry
import os
#The plugin name will be based on the plugin's folder.
PluginName = os.path.dirname(__file__).split(os.sep)[-1]

def configure(advanced):
  # This will be called by supybot to configure this module.  advanced is
  # a bool that specifies whether the user identified himself as an advanced
  # user or not.  You should effect your configuration by manipulating the
  # registry as appropriate.
  from supybot.questions import expect, anything, something, yn
  botPort = conf.registerPlugin(PluginName, True)
  
  if yn("""The Beatport plugin rocks.  Would you like these commands to
           be enabled for everyone?""", default = False):
    botPort.userLevelRequires.setValue("")
  else:
    cap = something("""What capability would you like to require for
                       this command to be used?""", default = "Admin")
    botPort.userLevelRequires.setValue(cap)
  
  sortBy = expect("""In what order would you like results displayed?
                     See http://api.beatport.com/catalog-search.html for
                     options.""",
                  ["releaseDate", "publishDate", "releaseId", "trackName",
                   "trackId", "labelName", "genreName"],
                  default = "releaseDate")
  botPort.sortBy.setValue(sortBy)

  perPage = something("""How many results would you like returned per search?
                      """, default = 5)
  botPort.numResults.setValue(perPage)
  

P = conf.registerPlugin(PluginName)
P.__name__ = PluginName

# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(PluginName, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))


