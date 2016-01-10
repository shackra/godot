#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# makedocs.py: Generate documentation for Open Project Wiki
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
#
# TODO:
#  * Refactor code.
#  * Adapt this script for generating content in other markup formats like
#    reStructuredText, Markdown, DokuWiki, etc.
#
# Also check other TODO entries in this script for more information on what is
# left to do.
import argparse
import gettext
import logging
import re
from itertools import zip_longest
from os import path, listdir
from xml.etree import ElementTree

from exporters import common as mm, textile as texl


# add an option to change the verbosity
logging.basicConfig(level=logging.INFO)


def getxmlfloc():
    """ Returns the supposed location of the XML file
    """
    filepath = path.dirname(path.abspath(__file__))
    return path.join(filepath, "class_list.xml")


def langavailable():
    """ Return a list of languages available for translation
    """
    filepath = path.join(
        path.dirname(path.abspath(__file__)), "locales")
    files = listdir(filepath)
    choices = [x for x in files]
    choices.insert(0, "none")
    return choices


desc = "Generates documentation from a XML file to different markup languages"

parser = argparse.ArgumentParser(description=desc)
parser.add_argument("--input", dest="xmlfp", default=getxmlfloc(),
                    help="Input XML file, default: {}".format(getxmlfloc()))
parser.add_argument("--output-dir", dest="outputdir", required=True,
                    help="Output directory for generated files")
parser.add_argument("--language", choices=langavailable(), default="none",
                    help=("Choose the language of translation"
                          " for the output files. Default is English (none). "
                          "Note: This is NOT for the documentation itself!"))
# TODO: add an option for outputting different markup formats

args = parser.parse_args()
# Let's check if the file and output directory exists
if not path.isfile(args.xmlfp):
    logging.critical("File not found: {}".format(args.xmlfp))
    exit(1)
elif not path.isdir(args.outputdir):
    logging.critical("Path does not exist: {}".format(args.outputdir))
    exit(1)

_ = gettext.gettext
if args.language != "none":
    lang = gettext.translation(domain="makedocs",
                               localedir="locales",
                               languages=[args.language])
    lang.install()

    _ = lang.gettext


# Let's begin
tree = ElementTree.parse(args.xmlfp)
root = tree.getroot()

# Check version attribute exists in <doc>
if "version" not in root.attrib:
    logging.critical(_("<doc>'s version attribute missing"))
    exit(1)

version = root.attrib["version"]
classes = sorted(root, key=mm.sortkey)
# first column is always longer, second column of classes should be shorter
zclasses = zip_longest(classes[:int(len(classes) / 2 + 1)],
                       classes[int(len(classes) / 2 + 1):],
                       fillvalue="")

# We write the class_list file and also each class file at once
# TODO: move Textile stuff to its module
with open(path.join(args.outputdir, "class_list.txt"), "wb") as fcl:
    # Write header of table
    fcl.write(mm.tb("|^.\n"))
    fcl.write(mm.tb(_("|_. Index symbol |_. Class name "
                      "|_. Index symbol |_. Class name |\n")))
    fcl.write(mm.tb("|-.\n"))

    indexletterl = ""
    indexletterr = ""
    for gdclassl, gdclassr in zclasses:
        # write a row #
        # write the index symbol column, left
        if indexletterl != gdclassl.attrib["name"][0]:
            indexletterl = gdclassl.attrib["name"][0]
            fcl.write(mm.tb("| *{}* |".format(indexletterl.upper())))
        else:
            # empty cell
            fcl.write(mm.tb("| |"))
        # write the class name column, left
        fcl.write(mm.tb(_(mm.C_LINK).format(
            gclass=gdclassl.attrib["name"],
            lkclass=gdclassl.attrib["name"].lower())))

        # write the index symbol column, right
        if isinstance(gdclassr, ElementTree.Element):
            if indexletterr != gdclassr.attrib["name"][0]:
                indexletterr = gdclassr.attrib["name"][0]
                fcl.write(mm.tb("| *{}* |".format(indexletterr.upper())))
            else:
                # empty cell
                fcl.write(mm.tb("| |"))
        # We are dealing with an empty string
        else:
            # two empty cell
            fcl.write(mm.tb("| | |\n"))
            # We won't get the name of the class since there is no ElementTree
            # object for the right side of the tuple, so we iterate the next
            # tuple instead
            continue

        # write the class name column (if any), right
        fcl.write(mm.tb(_(mm.C_LINK).format(
            gclass=gdclassl.attrib["name"],
            lkclass=gdclassl.attrib["name"].lower()) + "|\n"))

        # row written #
        # now, let's write each class page for each class
        for gdclass in [gdclassl, gdclassr]:
            if not isinstance(gdclass, ElementTree.Element):
                continue

            classname = gdclass.attrib["name"]
            with open(path.join(args.outputdir, "{}.txt".format(
                    classname.lower())), "wb") as clsf:
                # First level header with the name of the class
                clsf.write(mm.tb("h1. {}\n\n".format(classname)))
                # lay the attributes
                if "inherits" in gdclass.attrib:
                    inh = gdclass.attrib["inherits"].strip()
                    clsf.write(mm.tb(texl.OPENPROJ_INH.format(
                        gclass=inh, lkclass=inh.lower())))
                if "category" in gdclass.attrib:
                    clsf.write(mm.tb(_("h4. Category: {}\n\n").
                                     format(gdclass.attrib["category"].strip())))
                # lay child nodes
                briefd = gdclass.find("brief_description")
                if briefd.text.strip():
                    clsf.write(mm.tb(_("h2. Brief Description\n\n")))
                    clsf.write(mm.tb(texl.convertcommands(_, briefd.text.strip()) +
                                     _("\"read more\":#more\n\n")))

                # Write the list of member functions of this class
                methods = gdclass.find("methods")
                if methods and len(methods) > 0:
                    clsf.write(mm.tb(_("\nh3. Member Functions\n\n")))
                    for method in methods.iter(tag='method'):
                        clsf.write(mm.tb(texl.mkfn(_, method)))

                signals = gdclass.find("signals")
                if signals and len(signals) > 0:
                    clsf.write(mm.tb(_("\nh3. Signals\n\n")))
                    for signal in signals.iter(tag='signal'):
                        clsf.write(mm.tb(texl.mkfn(_, signal, True)))
                # TODO: <members> tag is necessary to process? it does not
                # exists in class_list.xml file.

                consts = gdclass.find("constants")
                if consts and len(consts) > 0:
                    clsf.write(mm.tb(_("\nh3. Numeric Constants\n\n")))
                    for const in sorted(consts, key=lambda k:
                                        k.attrib["name"]):
                        if const.text.strip():
                            clsf.write(mm.tb("* *{name}* = *{value}* - {desc}\n".
                                             format(
                                                 name=const.attrib["name"],
                                                 value=const.attrib["value"],
                                                 desc=const.text.strip())))
                        else:
                            # Constant have no description
                            clsf.write(mm.tb("* *{name}* = *{value}*\n".
                                             format(
                                                 name=const.attrib["name"],
                                                 value=const.attrib["value"])))
                descrip = gdclass.find("description")
                clsf.write(mm.tb(_("\nh3(#more). Description\n\n")))
                if descrip.text:
                    clsf.write(mm.tb(descrip.text.strip() + "\n"))
                else:
                    clsf.write(mm.tb(_("_Nothing here, yet..._\n")))

                # and finally, the description for each method
                if methods and len(methods) > 0:
                    clsf.write(
                        mm.tb(_("\nh3. Member Function Description\n\n")))
                    for method in methods.iter(tag='method'):
                        clsf.write(mm.tb("h4(#{n}). {name}\n\n".format(
                            n=method.attrib["name"].lower(),
                            name=method.attrib["name"])))
                        clsf.write(mm.tb(texl.mkfn(_, method) + "\n"))
                        clsf.write(mm.tb(texl.convertcommands(_, method.find(
                            "description").text.strip())))
