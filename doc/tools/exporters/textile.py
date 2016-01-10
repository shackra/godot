#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# textile.py: stuff for exporting to Textile
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
Module containing stuff for exporting the documentation from XML to Textile
markup
"""
import re
from . import common as mm

OPENPROJ_INH = "h4. Inherits: " + mm.C_LINK + "\n\n"


def _textformat(text):
    """ Convert text properties to Textile
    """
    # TODO: Make this capture content between [command] ... [/command]
    groups = re.finditer((r'\[html (?P<command>/?\w+/?)(\]| |=)?(\]| |=)?(?P<a'
                          r'rg>\w+)?(\]| |=)?(?P<value>"[^"]+")?/?\]'), text)
    alignstr = ""
    for group in groups:
        groupdict = group.groupdict()
        if groupdict["command"] == "br/":
            text = text.replace(group.group(0), "\n\n", 1)
        elif groupdict["command"] == "div":
            if groupdict["value"] == '"center"':
                alignstr = ("{display:block; margin-left:auto;"
                            " margin-right:auto;}")
            elif groupdict["value"] == '"left"':
                alignstr = "<"
            elif groupdict["value"] == '"right"':
                alignstr = ">"
            text = text.replace(group.group(0), "\n\n", 1)
        elif groupdict["command"] == "/div":
            alignstr = ""
            text = text.replace(group.group(0), "\n\n", 1)
        elif groupdict["command"] == "img":
            text = text.replace(group.group(0), "!{align}{src}!".format(
                align=alignstr, src=groupdict["value"].strip('"')), 1)
        elif groupdict["command"] == "b" or groupdict["command"] == "/b":
            text = text.replace(group.group(0), "*", 1)
        elif groupdict["command"] == "i" or groupdict["command"] == "/i":
            text = text.replace(group.group(0), "_", 1)
        elif groupdict["command"] == "u" or groupdict["command"] == "/u":
            text = text.replace(group.group(0), "+", 1)

    return text


def convertcommands(lang, text):
    """ Convert commands in text to Open Project commands
    """
    _ = lang
    text = _textformat(text)
    # Process other non-html commands
    groups = re.finditer((r'\[method ((?P<class>[aA0-zZ9_]+)(?:\.))'
                          r'?(?P<method>[aA0-zZ9_]+)\]'), text)
    for group in groups:
        gd = group.groupdict()
        if gd["class"]:
            replacewith = (_(mm.MC_LINK).format(gclass=gd["class"],
                                                method=gd["method"],
                                                lkclass=gd["class"].lower(),
                                                lkmethod=gd["method"].lower()))
        else:
            # The method is located in the same wiki page
            replacewith = (_(mm.TM_JUMP).format(method=gd["method"],
                                                lkmethod=gd["method"].lower()))

        text = text.replace(group.group(0), replacewith, 1)
    # Finally, [Classes] are around brackets, make them direct links
    groups = re.finditer(r'\[(?P<class>[az0-AZ0_]+)\]', text)
    for group in groups:
        gd = group.groupdict()
        replacewith = (_(mm.C_LINK).
                       format(gclass=gd["class"],
                              lkclass=gd["class"].lower()))
        text = text.replace(group.group(0), replacewith, 1)

    return text + "\n\n"


def mkfn(lang, node, is_signal=False):
    """ Return a string containing a unsorted item for a function
    """
    _ = lang
    finalstr = ""
    name = node.attrib["name"]
    rtype = node.find("return")
    if rtype:
        rtype = rtype.attrib["type"]
    else:
        rtype = "void"
    # write the return type and the function name first
    finalstr += "* "
    # return type
    if not is_signal:
        if rtype != "void":
            finalstr += _(mm.GTC_LINK).format(
                rtype=rtype,
                link=rtype.lower())
        else:
            finalstr += " void "

    # function name
    if not is_signal:
        finalstr += _(mm.DFN_JUMP).format(
            funcname=name,
            link=name.lower())
    else:
        # Signals have no description
        finalstr += "*{funcname}* <b>(</b>".format(funcname=name)
    # loop for the arguments of the function, if any
    args = []
    for arg in sorted(
            node.iter(tag="argument"),
            key=lambda a: int(a.attrib["index"])):

        ntype = arg.attrib["type"]
        nname = arg.attrib["name"]

        if "default" in arg.attrib:
            args.insert(-1, _(mm.M_ARG_DEFAULT).format(
                gclass=ntype,
                lkclass=ntype.lower(),
                name=nname,
                default=arg.attrib["default"]))
        else:
            # No default value present
            args.insert(-1, _(mm.M_ARG).format(gclass=ntype,
                                               lkclass=ntype.lower(), name=nname))
    # join the arguments together
    finalstr += ", ".join(args)
    # and, close the function with a )
    finalstr += " <b>)</b>"
    # write the qualifier, if any
    if "qualifiers" in node.attrib:
        qualifier = node.attrib["qualifiers"]
        finalstr += " " + qualifier

    finalstr += "\n"

    return finalstr
