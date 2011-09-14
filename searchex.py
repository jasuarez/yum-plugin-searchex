# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#
# Copyright Igalia, S.L. 2011
#
# Author: Juan A. Suarez Romero <jasuarez@igalia.com>

from yum.plugins import TYPE_INTERACTIVE
import re

requires_api_version = '2.5'
plugin_type = (TYPE_INTERACTIVE,)

class SearchexCommand:
    def getNames(self):
        return ['searchex']

    def getUsage(self):
        return "[pattern...]"

    def getSummary(self):
        return "Search packages matching one of the patterns"

    def doCheck(self, base, basecmd, extcmds):
        pass

    def doCommand(self, base, basecmd, extcmds):
        return None, ""

def config_hook(conduit):
    '''
    Add the 'searchex' command.
    '''
    conduit.registerCommand(SearchexCommand())
