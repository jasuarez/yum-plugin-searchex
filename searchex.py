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
# Copyright Igalia, S.L. 2011-2014
#
# Author: Juan A. Suarez Romero <jasuarez@igalia.com>

from yum.plugins import TYPE_INTERACTIVE
import re

MATCH_ON_PACKAGE="~(?P<invert_p>[\+-]?)(?P<where_p>[dnRs])(?P<what_p>[^~]*)"
MATCH_ON_PACKAGE_NAME="(?P<what_n>[^~]+)"
MATCH_ON_LIST="~(?P<invert_l>[\+-]?)(?P<where_l>[aioru])"
MATCH_UNKNOWN="(?P<what_u>~[\+-]?.)"

MATCH_ALL=MATCH_ON_PACKAGE + "|" + MATCH_ON_LIST + "|" \
    + MATCH_ON_PACKAGE_NAME + "|" + MATCH_UNKNOWN

requires_api_version = '2.5'
plugin_type = (TYPE_INTERACTIVE,)

def _match_pkg_field(package, field, text, invert):
    m = re.search(text, field, re.IGNORECASE)
    if invert:
        return m == None
    else:
        return m != None

def _match_pkg_name(package, name, invert=False):
    return _match_pkg_field(package, package.name, name, invert)

def _match_pkg_desc(package, desc, invert=False):
    return _match_pkg_field(package, package.description, desc, invert)

def _match_pkg_summary(package, summary, invert=False):
    return _match_pkg_field(package, package.summary, summary, invert)

def _match_pkg_repo(package, repository, invert=False):
    return _match_pkg_field(package, package.ui_from_repo, repository, invert)

def _match_pkg_desc_or_summary(package, text, invert=False):
    if invert:
        return _match_pkg_summary(package, text, invert) and \
            _match_pkg_desc(package, text, invert)
    else:
        return _match_pkg_summary(package, text, invert) or \
            _match_pkg_desc(package, text, invert)

def _filter_list_installed(pkglist, invert=False):
    if invert:
        pkglist.installed = []
    else:
        pkglist.available = []
        pkglist.extras = []
        pkglist.updates = []
        pkglist.obsoletes = []
        pkglist.recent = []
    return pkglist

def _filter_list_available(pkglist, invert=False):
    if invert:
        pkglist.available = []
    else:
        pkglist.installed = []
        pkglist.extras = []
        pkglist.updates = []
        pkglist.obsoletes = []
        pkglist.recent = []
    return pkglist

def _filter_list_obsoletes(pkglist, invert=False):
    if invert:
        pkglist.obsoletes = []
    else:
        pkglist.available = []
        pkglist.installed = []
        pkglist.extras = []
        pkglist.updates = []
        pkglist.recent = []
    return pkglist

def _filter_list_updates(pkglist, invert=False):
    if invert:
        pkglist.updates = []
    else:
        pkglist.available = []
        pkglist.installed = []
        pkglist.extras = []
        pkglist.obsoletes = []
        pkglist.recent = []
    return pkglist

def _build_pkg_filter(where, what, invert=False):
    if where == 'd':
        return [(_match_pkg_desc_or_summary, what, invert)]
    elif where == 'n':
        return [(_match_pkg_name, what, invert)]
    elif where == 'R':
        return [(_match_pkg_repo, what, invert)]
    elif where == 's':
        return [(_match_pkg_summary, what, invert)]
    else:
        return []

def _build_list_filter(where, invert=False):
    if where == 'a':
        return [(_filter_list_available, invert)]
    elif where == 'i':
        return [(_filter_list_installed, invert)]
    elif where == 'o':
        return [(_filter_list_obsoletes, invert)]
    elif where == 'u':
        return [(_filter_list_updates, invert)]
    else:
        return []

def _filter_package(package, filter):
    for f in filter:
        if not f[0](package, f[1], f[2]):
            return None
    return package

def _filter_list(pkglist, filter):
    for f in filter:
        pkglist=f[0](pkglist, f[1])
    return pkglist

        
class SearchexCommand:
    def runFilter(self, pkglist, type_list):
        for pkg in pkglist:
            if _filter_package(pkg, self._match_on_pkg) and \
                    (type_list, pkg.name, pkg.summary) not in self._result:
                self._result.append ((type_list, pkg.name + "." + pkg.arch, pkg.summary))
        
    def getNames(self):
        return ['searchex']

    def getUsage(self):
        return "[pattern...]"

    def getSummary(self):
        return "Search packages matching one of the patterns"

    def doCheck(self, base, basecmd, extcmds):
        pass

    def doCommand(self, base, basecmd, extcmds):
        self._result = []

        for extcmd in extcmds:
            self._match_on_list = []
            self._match_on_pkg = []
            for pattern in re.finditer(MATCH_ALL, extcmd):
                if pattern.group('what_u'):
                    return 1, ['Unknown pattern "%s"' % pattern.group('what_u')]
                if pattern.group('what_n'):
                    f=_build_pkg_filter('n', pattern.group('what_n'))
                    self._match_on_pkg.extend(f)
                    continue
                f=_build_list_filter(pattern.group('where_l'), \
                                         pattern.group('invert_l') == '-') or []
                self._match_on_list.extend(f)
                f=_build_pkg_filter(pattern.group('where_p'), \
                                        pattern.group('what_p'), \
                                        pattern.group('invert_p') == '-') or []
                self._match_on_pkg.extend(f)

            ypl=_filter_list(base.returnPkgLists(""), self._match_on_list)
            self.runFilter(ypl.installed, "i")
            self.runFilter(ypl.available, "a")
            self.runFilter(ypl.extras, "e")
            self.runFilter(ypl.updates, "u")
            self.runFilter(ypl.obsoletes, "o")
            self.runFilter(ypl.recent, "r")
            self._result.sort()

        for r in self._result:
            print unicode("(%s) %-30s: %s" % r, errors='replace')

        return 0, ['%d packages matched' % len(self._result)]

def config_hook(conduit):
    '''
    Add the 'searchex' command.
    '''
    conduit.registerCommand(SearchexCommand())
