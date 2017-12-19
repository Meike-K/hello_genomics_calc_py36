#!/usr/bin/env python
# coding: utf-8
"""
 Hello Genomics sample calculation app for FASTGenomics
"""
import json
import pathlib
import random
import csv
import jinja2
import logging

from collections import defaultdict
from fastgenomics import io as fg_io
from . import logging_config

# initialize logging
logging_config.configure_logging(level=logging.INFO)
logger = logging.getLogger('hello_genomics_calc')

# set paths to jinja2-templates for summary.md etc.
TEMPLATE_PATH = pathlib.Path(__file__).parent.parent / 'templates'


def main():
    """
    main routine of hello genomics:

    minimal 'calculation app': reads the genes matrix, counts genes and writes a summary
    """
    # LOAD PARAMETERS
    #
    # Your parameters are located in /fastgenomics/config/parameters.json (not implemented yet!)
    # Our fastgenomics.io module loads these parameters or uses the pre-defined defaults
    # defined in your manifest.json of your application.
    #
    logger.info("Loading parameters")
    parameters = fg_io.get_parameters()

    # BEST PRACTICE:
    # Set or save random seed to achieve reproducibility
    #
    random.seed(4711)
    parameters['random_seed'] = 4711

    # GET GENES MATRIX FROM DATASET
    #
    # Data from the origin dataset is located in /fastgenomics/data/dataset
    # Data from other calculations is located in /fastgenomics/data/uuid_of_calculation/output
    # You can easily access data with our fastgenomics.io module as follows:
    #
    logger.info("Loading genes matrix")
    # HINT: the key 'genes_data_input' has to be defined in your manifest.json
    #       the actual path and filename will be provided by the FASTGenomics runtime and be available via
    #       /fastgenomics/config/input_file_mapping.json
    genes_path = fg_io.get_input_path('genes_data_input')

    with genes_path.open('r') as f_in:
        # LOAD GENES MATRIX:
        # The csv-reader-instance is an iterator for our input-file.
        # We save memory (in case of large input files) but iterating over rows instead of loading the content entirely.
        reader = csv.reader(f_in, delimiter=fg_io.get_parameter('delimiter'))

        # GET HEADER:
        # Get first row of the file, get rid of the '*type'-annotation, and transform column-names to lowercase
        header = [col.split('*')[0].lower() for col in next(reader)]

        # PERFORM SOME CALCULATION
        #
        # We here do some sample calculations and count genes and gene types
        #
        # 1. Create target dict with default entry int(0)
        gene_types = defaultdict(int)

        # 2. Get index of gene-type column
        gene_type_col = header.index("type")

        # 3. Count: Increase gene-type by one for each hit by iterating over the rows of our genes matrix
        num_genes = 0
        for row in reader:
            gene_types[row[gene_type_col]] += 1
            num_genes += 1

        logger.info(f"Found {num_genes} genes and {len(gene_types.keys())} gene types.")

    # WRITE OUTPUT
    #
    # You can write output files to /fastgenomics/output
    # Consider using the fastgenomics.io module to ensure correct paths and interfaces
    #
    logger.info("Storing results")
    # Hint: the key 'data_quality_output' has to be defined in your manifest.json
    output_path = fg_io.get_output_path('data_quality_output')
    results = {'num_genes': num_genes, 'gene_types': gene_types}

    with output_path.open('w') as f_out:
        json.dump(results, f_out)

    # WRITE SUMMARY
    #
    # Reproducibility is a core goal of FASTGenomics, but it is difficult to achieve this without your help.
    # Docker helps to freeze the exact code your app is using, but code without documentation is difficult to use,
    # so an app is expected to have a documentation and provide a summary of its results (as CommonMark).
    # You need to store it as /fastgenomics/summary/summary.md - otherwise it would be ignored.
    #
    # Please provide:
    # - an abstract about your application (without headings)
    # - results section (h3)
    # - methods section (h3)
    # - parameters section (h3): List of *all* parameters used.
    #                            DO NOT hard-code settings in your app but use parameters.
    #
    # In this example we use Jinja2 as template engine, use the template ./templates/summary.md.j2,
    # and pass over our results and parameters:
    #
    logger.debug("Loading Jinja2 summary template")
    with open(TEMPLATE_PATH / 'summary.md.j2') as temp:
        template_str = temp.read()

    logger.debug("Rendering template")
    template = jinja2.Template(template_str)
    summary = template.render(results=results, parameters=parameters, the_answer_to_everything=42)

    logger.info("Writing summary")
    summary_path = fg_io.get_summary_path()
    with summary_path.open('w') as f_sum:
        f_sum.write(summary)

    logger.info("Done.")
