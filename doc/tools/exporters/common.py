#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# common.py: common stuff shared between exporters
# Copyright (c) 2007-2016 Juan Linietsky, Ariel Manzur.
# Contributor: Jorge Araya Navarro <elcorreo@deshackra.com>
#

# IMPORTANT NOTICE:
# If you are going to modify anything from this file, please be sure to follow
# the Style Guide for Python Code or often called "PEP8". To do this
# automagically just install autopep8:
#
#     $ sudo pip3 install autopep8
#
# and run:
#
#     $ autopep8 makedocs.py
#
# Before committing your changes. Also be sure to delete any trailing
# whitespace you may left.

"""
Module containing common stuff shared among exporters
"""

# Strings
C_LINK = ("\"<code>{gclass}</code>(Go to page of class"
          " {gclass})\":/class_{lkclass}")
MC_LINK = ("\"<code>{gclass}.{method}</code>(Go "
           "to page {gclass}, section {method})\""
           ":/class_{lkclass}#{lkmethod}")
TM_JUMP = ("\"<code>{method}</code>(Jump to method"
           " {method})\":#{lkmethod}")
GTC_LINK = " \"{rtype}(Go to page of class {rtype})\":/class_{link} "
DFN_JUMP = ("\"*{funcname}*(Jump to description for"
            " node {funcname})\":#{link} <b>(</b> ")
M_ARG_DEFAULT = C_LINK + " {name}={default}"
M_ARG = C_LINK + " {name}"


def tb(string):
    """ Return a byte representation of a string
    """
    return bytes(string, "UTF-8")


def sortkey(keys):
    """ Symbols are first, letters second
    """
    if "_" == keys.attrib["name"][0]:
        return "A"
    else:
        return keys.attrib["name"]
