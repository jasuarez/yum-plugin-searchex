Description
===========

**Searchex** (_Search Extended_) is a _yum_ plugin heavily inspired by Debian's
_aptitude_ command that allows a flexible search of packages.


Usage
=====

```
yum searchex <pattern>+ <pattern>+ ...
```

Where each _pattern_ is a concatenation of one or more search expressions.

A _search expression_ is an expression used to search packages. It's format is
`~[+|-]<where><what>`.

_where_ is where to search the package. There are two kind of parameters: those
that require the _what_ parameter, and those that do not have such parameter.

The possible values for those that do not require a parameter are:

- _a_: get the available but not installed packages
- _i_: get the installed packages
- _o_: get the obsolete packages
- _r_: get the recent packages
- _u_: get the update packages

On the other hand, the possible values for those that require the _what_
parameter are:

- _d_: get the packages that contains _what_ in their description or summary
- _n_: get the packages that contain _what_ in their name
- _R_: get the packages belonging to _what_ repository
- _s_: get the packages that contains _what_ in their summary

The _where_ parameter can be omitted; in this case it is assumed that the _n_
parameter is used.

_+_ and _-_ options keeps or inverts the results of the search expression. A _+_
keeps the result, while a _-_ inverts it. If omitted, it is assumed _+_.


Examples
========

As there are parameters that are optional, usually there are several ways of
performing the same search. We will show several of them per each type of
search.

- Search all packages that are named _glib_:

```
yum searchex ~+nglib
yum searchex ~nglib
yum searchex glib
```

- Search all packages containing _KDE_ in their description:

```
yum searchex ~dKDE
```

- Search packages not installed that contain _gcc_ in their name:

```
yum searchex ~agcc
yum searchex ~a~ngcc
yum searchex ~-igcc
yum searchex ~-i~ngcc
```

- Search packages not installed that contain python in their name and PIP in the
  description:

```
yum searchex ~a~npython~dPIP
yum searchex ~apython~dPIP
yum searchex ~-ipython~dPIP
yum searchex python~a~dPIP
```

- Search all packages that matches any of the previous examples:

```
yum searchex glib ~dKDE ~agcc ~apython~dPIP
```


Installation
============

Copy `searchex.conf` into `/etc/yum/pluginconf.d`.

Copy `searchex.py` into `/usr/lib/yum-plugins`.

