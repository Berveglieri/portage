# Copyright: 2005-2009 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id$

# all vars that are to wind up in portage_const must have their name listed in __all__

__all__ = ["EPREFIX", "SYSCONFDIR", "DATADIR", "PORTAGE_BASE",
		"portageuser", "portagegroup", "rootuser", "rootuid", "rootgid",
		"PORTAGE_BASH", "PORTAGE_MV"]

from os import path

EPREFIX      = @PORTAGE_EPREFIX@
SYSCONFDIR   = path.normpath("@sysconfdir@")
DATADIR      = path.normpath("@datadir@")
PORTAGE_BASE = path.normpath("@PORTAGE_BASE@")

portagegroup = "@portagegroup@"
portageuser  = "@portageuser@"
rootuser     = "@rootuser@"
rootuid      = @rootuid@
rootgid      = @rootgid@

PORTAGE_BASH = "@PORTAGE_BASH@"
PORTAGE_MV   = "@PORTAGE_MV@"
