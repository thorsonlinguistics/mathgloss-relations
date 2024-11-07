"""
Cleans the MathGloss CSV for processing.
"""

import csv
import os

from markdown import Markdown
from io import StringIO

base_path = os.path.dirname(os.path.abspath(__file__))
INFILE = os.path.join(base_path, "../MathGloss/database.csv")
OUTFILE = "database_clean.csv"

def main():

    md = Markdown(output_format="plain")
    md.stripTopLevelTags = False

    with open(INFILE, newline='') as infile:
        reader = csv.reader(infile)
        with open(OUTFILE, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            for row in reader:
                writer.writerow(map(lambda text: md.convert(text), row))

def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

# Patch markdown to extract plaintext
Markdown.output_formats["plain"] = unmark_element

if __name__ == "__main__":

    main()
