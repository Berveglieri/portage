# Copyright 2012-2013 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

from __future__ import unicode_literals

from portage.dep import Atom, paren_enclose, use_reduce
from portage.eapi import _get_eapi_attrs
from portage.exception import InvalidData
from _emerge.Package import Package

def find_built_slot_operator_atoms(pkg):
	atoms = {}
	for k in Package._dep_keys:
		atom_list = list(_find_built_slot_operator(use_reduce(pkg._metadata[k],
			uselist=pkg.use.enabled, eapi=pkg.eapi,
			token_class=Atom)))
		if atom_list:
			atoms[k] = atom_list
	return atoms

def _find_built_slot_operator(dep_struct):
	for x in dep_struct:
		if isinstance(x, list):
			for atom in _find_built_slot_operator(x):
				yield atom
		elif isinstance(x, Atom) and x.slot_operator_built:
			yield x

def ignore_built_slot_operator_deps(dep_struct):
	for i, x in enumerate(dep_struct):
		if isinstance(x, list):
			ignore_built_slot_operator_deps(x)
		elif isinstance(x, Atom) and x.slot_operator_built:
			# There's no way of knowing here whether the SLOT
			# part of the slot/sub-slot pair should be kept, so we
			# ignore both parts.
			dep_struct[i] = x.without_slot

def evaluate_slot_operator_equal_deps(settings, use, trees):

	metadata = settings.configdict['pkg']
	eapi = metadata['EAPI']
	eapi_attrs = _get_eapi_attrs(eapi)
	running_vardb = trees[trees._running_eroot]["vartree"].dbapi
	target_vardb = trees[trees._target_eroot]["vartree"].dbapi
	vardbs = [target_vardb]
	deps = {}
	for k in Package._dep_keys:
		deps[k] = use_reduce(metadata[k],
			uselist=use, eapi=eapi, token_class=Atom)

	for k in Package._runtime_keys:
		_eval_deps(deps[k], vardbs)

	if eapi_attrs.hdepend:
		_eval_deps(deps["HDEPEND"], [running_vardb])
		_eval_deps(deps["DEPEND"], [target_vardb])
	else:
		if running_vardb is not target_vardb:
			vardbs.append(running_vardb)
		_eval_deps(deps["DEPEND"], vardbs)

	result = {}
	for k, v in deps.items():
		result[k] = paren_enclose(v)

	return result

def _eval_deps(dep_struct, vardbs):
	for i, x in enumerate(dep_struct):
		if isinstance(x, list):
			_eval_deps(x, vardbs)
		elif isinstance(x, Atom) and x.slot_operator == "=":
			for vardb in vardbs:
				best_version = vardb.match(x)
				if best_version:
					best_version = best_version[-1]
					try:
						best_version = \
							vardb._pkg_str(best_version, None)
					except (KeyError, InvalidData):
						pass
					else:
						slot_part = "%s/%s=" % \
							(best_version.slot, best_version.sub_slot)
						x = x.with_slot(slot_part)
						dep_struct[i] = x
						break
			else:
				# this dep could not be resolved, so remove the operator
				# (user may be using package.provided and managing rebuilds
				# manually)
				if x.slot:
					x = x.with_slot(x.slot)
				else:
					x = x.without_slot
				dep_struct[i] = x
