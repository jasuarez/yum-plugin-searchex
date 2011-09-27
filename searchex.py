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

MATCH_ON_PACKAGE="~(?P<where_p>[nd])(?P<what_p>[^~]*)"
MATCH_ON_LIST="~(?P<where_l>[i])"

MATCH_ALL=MATCH_ON_PACKAGE + "|" + MATCH_ON_LIST

requires_api_version = '2.5'
plugin_type = (TYPE_INTERACTIVE,)

def _match_pkg_name(package, name):
    m = re.search(name, package.name)
    return (m != None)

def _match_pkg_desc(package, desc):
    m = re.search(desc, package.description)
    return (m != None)

def _filter_list_installed(pkglist):
    pkglist.available = []
    return pkglist

def _build_pkg_filter(where, what):
    if where == 'n':
        return (_match_pkg_name, what)
    elif where == 'd':
        return (_match_pkg_desc, what)
    else:
        return None

def _build_list_filter(where):
    if where == 'i':
        return _filter_list_installed
    else:
        return None

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
        #import pdb;pdb.set_trace()
        match_on_list = []
        match_on_pkg = []

        for pattern in re.finditer(MATCH_ALL, extcmds[0]):
            f=_build_list_filter(pattern.group('where_l'))
            if f:
                match_on_list.append(f)
            f=_build_pkg_filter(pattern.group('where_p'), pattern.group('what_p'))
            if f:
                match_on_pkg.append(f)

        pkglist=_filter_list(base.returnPkgLists(""), match_on_list)
        for pkg in pkglist.installed:
            if _filter_package(pkg, match_on_pkg) != None:
                print "(i) %s:  %s" % (pkg.name, pkg.summary)
        for pkg in pkglist.available:
            if _filter_package(pkg, match_on_pkg) != None:
                print "(a) %s:  %s" % (pkg.name, pkg.summary)

        # pkglist=base.returnPkgLists("")
        # for pkg in pkglist.available:
        #     for pattern in re.finditer(MATCH_ALL, extcmds[0]):
        #         if _match_name(pkg, pattern.group('what_p')):
        #             print "%s:  %s" % (pkg.name, pkg.summary)
        return None, ""

def config_hook(conduit):
    '''
    Add the 'searchex' command.
    '''
    conduit.registerCommand(SearchexCommand())
