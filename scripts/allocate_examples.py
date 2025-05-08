'''
    Extend the working negative samples with more negative samples from the full TEI XML files
'''

import argparse
import copy
import csv
import math
import ntpath
import os
import regex as re
import xml
from collections import OrderedDict
from lxml import etree


def remove_namespace_prefix(element):
    """
    Recursively remove namespace prefixes from an element and its children.
    Returns a new element with the same structure but without namespace prefixes.
    """
    # Check if element is actually an Element object
    if not hasattr(element, 'tag') or not isinstance(element.tag, str):
        print(f"Warning: Skipping non-Element object of type {type(element)}")
        return None

    # Create new element with the same tag but without namespace prefix
    try:
        tag = etree.QName(element).localname
        new_element = etree.Element(tag)
    except (ValueError, TypeError) as e:
        print(f"Error processing element tag: {e}")
        print(f"Element type: {type(element)}, Element: {element}")
        return None

    # Copy attributes
    try:
        for key, value in element.attrib.items():
            # Remove namespace prefix from attribute names if present
            attr_name = etree.QName(key).localname
            new_element.set(attr_name, value)
    except (AttributeError, ValueError, TypeError) as e:
        print(f"Error processing element attributes: {e}")
        return new_element  # Return what we have so far

    # Copy text content
    if element.text:
        new_element.text = element.text

    # Process children recursively
    for child in element:
        # Skip non-element children
        if not hasattr(child, 'tag') or not isinstance(child.tag, str):
            print(f"Warning: Skipping non-Element child of type {type(child)}")
            continue

        try:
            new_child = remove_namespace_prefix(child)
            if new_child is not None:
                new_element.append(new_child)

                # Preserve tail text
                if child.tail:
                    new_child.tail = child.tail
        except Exception as e:
            print(f"Error processing child: {e}")
            print(f"Child type: {type(child)}, Child: {child}")
            continue

    return new_element


def create_resource_sets(tei_corpus_path, negative_examples_file_path, positive_examples_file_path):
    # Create teiCorpus root elements with proper namespace for both negative and positive examples
    # Using None as the key makes it the default namespace (no prefix)
    nsmap = {None: 'http://www.tei-c.org/ns/1.0'}
    negative_root = etree.Element("{http://www.tei-c.org/ns/1.0}teiCorpus", version="3.3.0", nsmap=nsmap)
    positive_root = etree.Element("{http://www.tei-c.org/ns/1.0}teiCorpus", version="3.3.0", nsmap=nsmap)

    for root, dirs, files in os.walk(tei_corpus_path):
        for file in files:
            if not file.endswith(".tei.xml"):
                continue

            # We parse the file and we get everything under <TEI>
            root_tei_file = etree.parse(os.path.join(root, file))
            document = root_tei_file.xpath('//tei:tei', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

            negative_copy = copy.deepcopy(document[0])
            positive_copy = copy.deepcopy(document[0])

            # Remove all <p> containing <rs> from the negative_copy
            for p in positive_copy.xpath('.//tei:p[not(.//tei:rs)]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
                p.getparent().remove(p)

            # Remove all <p> without any <rs> from the positive_copy
            for p in negative_copy.xpath('.//tei:p[.//tei:rs]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
                p.getparent().remove(p)

            # Add the copies to their respective teiCorpus roots, removing namespace prefixes
            if len(negative_copy.xpath('.//tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})) > 0:
                # Remove namespace prefixes before adding to the root
                clean_negative_copy = remove_namespace_prefix(negative_copy)
                negative_root.append(clean_negative_copy)

            if len(positive_copy.xpath('.//tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})) > 0:
                # Remove namespace prefixes before adding to the root
                clean_positive_copy = remove_namespace_prefix(positive_copy)
                positive_root.append(clean_positive_copy)

    # Write the complete teiCorpus documents to files
    negative_tree = etree.ElementTree(negative_root)
    negative_tree.write(negative_examples_file_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    positive_tree = etree.ElementTree(positive_root)
    positive_tree.write(positive_examples_file_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="General count information on the full TEI softcite corpus")
    parser.add_argument(
        "--tei-corpus",
        type=str,
        required=True,
        help="path to the directory of full text TEI XML files"
    )
    parser.add_argument(
        "--negative-examples-file",
        type=str,
        required=True,
        help="path to the output file containing the set of negative examples"
    )
    parser.add_argument(
        "--positive-examples-file",
        type=str,
        required=True,
        help="path to the output file containing the set of positive examples"
    )

    args = parser.parse_args()
    tei_corpus_path = args.tei_corpus
    positive_examples_file_path = args.positive_examples_file
    negative_examples_file_path = args.negative_examples_file

    # check path and call methods
    if tei_corpus_path is not None and not os.path.isdir(tei_corpus_path):
        print("The path to the directory of TEI files is not valid: ", tei_corpus_path)
        exit()

    create_resource_sets(tei_corpus_path, negative_examples_file_path, positive_examples_file_path)
