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

from fastgenomics import io as fg_io

import logging
from hello_genomics import logging_config

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
    #       the actual filename will be provided by the FASTGenomics runtime and be available via
    #       /fastgenomics/config/input_file_mapping.json
    genes_file = fg_io.get_input_path('genes_data_input')

    with genes_file.open('r') as f_in:
        reader = csv.reader(f_in, delimiter=fg_io.get_parameter('delimiter'))
        # get matrix without the header
        genes_matrix = [row for row in reader][1:]

    # PERFORM SOME CALCULATION
    #
    # we here do some sample calculations and count genes
    num_genes = len(genes_matrix)
    logger.debug(f"found {num_genes} genes")

    # WRITE OUTPUT
    #
    # You can write output files to /fastgenomics/output
    # Consider using the fastgenomics.io module to ensure correct paths and interfaces
    #
    logger.info("Storing results")
    # Hint: the key 'data_quality_output' has to be defined in your manifest.json
    output_file = fg_io.get_output_path('data_quality_output')
    results = {'num_genes': num_genes, 'some_other_variable': "foo"}

    with output_file.open('w') as f_out:
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
    summary_file = fg_io.get_summary_path()
    with summary_file.open('w') as f_sum:
        f_sum.write(summary)

    logger.info("Done.")


if __name__ == '__main__':
    main()
