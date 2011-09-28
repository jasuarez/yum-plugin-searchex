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

MATCH_ON_PACKAGE="~(?P<where_p>[dns])(?P<what_p>[^~]*)"
MATCH_ON_LIST="~(?P<where_l>[i])"

MATCH_ALL=MATCH_ON_PACKAGE + "|" + MATCH_ON_LIST

requires_api_version = '2.5'
plugin_type = (TYPE_INTERACTIVE,)

def _match_pkg_field(package, field, text):
    m = re.search(text, field)
    return m != None

def _match_pkg_name(package, name):
    return _match_pkg_field(package, package.name, name)

def _match_pkg_desc(package, desc):
    return _match_pkg_field(package, package.description, desc)

def _match_pkg_summary(package, summary):
    return _match_pkg_field(package, package.summary, summary)

def _filter_list_installed(pkglist):
    pkglist.available = []
    return pkglist

def _build_pkg_filter(where, what):
    if where == 'd':
        return [(_match_pkg_desc, what)]
    elif where == 'n':
        return [(_match_pkg_name, what)]
    elif where == 's':
        return [(_match_pkg_summary, what)]
    else:
        return []

def _build_list_filter(where):
    if where == 'i':
        return [_filter_list_installed]
    else:
        return []

def _filter_package(package, filter):
    for f in filter:
        if not f[0](package, f[1]):
            return None
    return package

def _filter_list(pkglist, filter):
    for f in filter:
        pkglist=f(pkglist)
    return pkglist

        
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
        match_on_list = []
        match_on_pkg = []
        result = []

        for pattern in re.finditer(MATCH_ALL, extcmds[0]):
            f=_build_list_filter(pattern.group('where_l')) or []
            match_on_list.extend(f)
            f=_build_pkg_filter(pattern.group('where_p'), pattern.group('what_p')) or []
            match_on_pkg.extend(f)

        pkglist=_filter_list(base.returnPkgLists(""), match_on_list)
        #import pdb;pdb.set_trace()
        for pkg in pkglist.installed:
            if _filter_package(pkg, match_on_pkg) and ("i", pkg.name, pkg.summary) not in result:
                result.append (("i", pkg.name, pkg.summary))
        for pkg in pkglist.available:
            if _filter_package(pkg, match_on_pkg) and ("a", pkg.name, pkg.summary) not in result:
                result.append(("a", pkg.name, pkg.summary))
        result.sort()
        for r in result:
            print "(%s) %-25s: %s" % r
        return None, ""

def config_hook(conduit):
    '''
    Add the 'searchex' command.
    '''
    conduit.registerCommand(SearchexCommand())
