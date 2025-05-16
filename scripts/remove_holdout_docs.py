#!/usr/bin/env python3
"""
Script to remove TEI documents from an XML file based on IDs from a CSV file.

Usage:
    python remove_holdout_docs.py <ids_csv_file> <input_xml_file> <output_xml_file>

Example:
    python remove_holdout_docs.py ids.holdout.csv all_clean_post_processed-full.tei.xml all_clean_post_processed-filtered.tei.xml
"""

import csv
import sys
from lxml import etree

def read_ids_from_csv(csv_file):
    """Read IDs from the first column of a CSV file."""
    ids = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Skip header row
        next(reader)
        for row in reader:
            if row:  # Check if row is not empty
                ids.add(row[0])  # Add the ID from the first column
    return ids

def remove_tei_elements(xml_file, output_file, ids_to_remove):
    """Remove TEI elements with fileDesc xml:id in the given set of IDs."""
    # Parse the XML file
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_file, parser)
    root = tree.getroot()
    
    # Define namespace
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Find all TEI elements
    tei_elements = root.findall('.//tei:TEI', namespaces=ns)
    
    # Count for reporting
    total_tei = len(tei_elements)
    removed_tei = 0
    
    # Iterate through TEI elements and remove those with matching IDs
    for tei in tei_elements:
        # Find the fileDesc element
        file_desc = tei.find('.//tei:fileDesc', namespaces=ns)
        if file_desc is not None:
            # Get the xml:id attribute
            xml_id = file_desc.get('{http://www.w3.org/XML/1998/namespace}id')
            if xml_id in ids_to_remove:
                # Remove this TEI element
                tei.getparent().remove(tei)
                removed_tei += 1
    
    # Write the modified XML to the output file
    tree.write(output_file, pretty_print=True, encoding='utf-8', xml_declaration=True)
    
    print(f"Processed {total_tei} TEI elements")
    print(f"Removed {removed_tei} TEI elements with matching IDs")
    print(f"Remaining: {total_tei - removed_tei} TEI elements")

def main():
    if len(sys.argv) != 4:
        print("Usage: python remove_holdout_docs.py <ids_csv_file> <input_xml_file> <output_xml_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    xml_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print(f"Reading IDs from {csv_file}...")
    ids_to_remove = read_ids_from_csv(csv_file)
    print(f"Found {len(ids_to_remove)} IDs to remove")
    
    print(f"Processing XML file {xml_file}...")
    remove_tei_elements(xml_file, output_file, ids_to_remove)
    
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()