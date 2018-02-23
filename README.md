```
    o      O        o  o              .oOOOo.
    O      o       O  O              .O     o                              o
    o      O       o  o              o
    OoOooOOo       O  O              O
    o      O .oOo. o  o  .oOo.       O   .oOOo .oOo. 'OoOo. .oOo. `oOOoOO. O  .oOo  .oOo
    O      o OooO' O  O  O   o       o.      O OooO'  o   O O   o  O  o  o o  O     `Ooo.
    o      o O     o  o  o   O        O.    oO O      O   o o   O  o  O  O O  o         O
    o      O `OoO' Oo Oo `OoO'         `OooO'  `OoO'  o   O `OoO'  O  o  o o' `OoO' `OoO'
```
---

# How to write a FASTGenomics App

Writing an app is fairly easy - there are some conventions you need to know, but otherwise you are free to use any
language, tools and methods you want. This document explains the basic structure using the example of our python app
"Hello Genomics" and outlines core concepts.

## Core concepts

There are two flavors of apps in FASTGenomics: Calculations and Visualizations.
"Calculations" perform data-intensive tasks, for example clustering whereas "visualizations" display the aforementioned
results. A visualization might take a clustering result and display a diagram for the user.
To join the FASTGenomics community you have to tie up your app as an docker-image with some fixed structure to ensure
compatibility and reproducibility.

In the following section we'll give you a recipe-like tutorial, how to build your own app given a running python source
code and some sample date.
If you want to understand, why things are the way they are, have a closer look [here](#deep-dive-into-fastgenomics).

## How To (Cookbook-Style)
0. Write your application using any programming language and provide sample data.

1. Structure your application locally as follows:
  ```
working_directory/
    ├── docker-compose.yml (used for testing the app)
    ├── Dockerfile (blueprint of your app)
    ├── manifest.json (mandatory, see below)
    ├── LICENSE (mandatory)
    ├── README.md (mandatory)
    ├── requirements.txt (best practise)
    ├── sample_data (mandatory)
    │   ├── config
    │   │   ├── parameters.json (optional for testing usage of parameters)
    │   │   └── input_file_mapping.json (mandatory for I/O)
    │   ├── data (mandatory for testing)
    │   │   ├── some_file.csv
    │   │   └── ...
    │   ├── output
    │   └── summary
    ├── src (mandatory: source code of your app)
    │   ├── my_python_module 
    │   │   ├── __init__.py
    │   │   ├── __main__.py
    │   │   └── ...
    │   └── templates (optional static files)
    │       └── summary.md.j2
    └── test (best practise)
  ```
  This structure helps to create docker images and test things on ease.  
  
  **Tip:** This sample app has already the structure required - just clone it and get started.  
  **Hint:** In the following we assume that you cloned the "hello_genomics_calc" app and just modify files.
  
2. Edit the `manifest.json`:
  - Define each parameter / constant you want to use in your application
  - Define each input and output of your application  
    **Attention:** each file you want to read or write has to be defined here!  
    Input is defined in therms of a key/value pair: The key is a string, under which you expect to get a file from other
    applications. The actual path and filename will be determined during execution by the FASTGenomics runtime and
    provided within the `input_file_mapping.json` (not the one you're providing).
    With the definition of output in the manifest.json, you make promises for other apps, which files you'll write:
    Provide a key and the filename of the files you will write during execution.
    
3. Edit the `input_file_mapping.json` and define key/value pairs for each input file requested by your app and provide
   the *relative* path of each file to the sample_data/data directory.  
   Example: ``{"some_input": "some_file.csv"}``
   
4. Rewrite your source code regarding I/O and usage of parameters by either making use of our [fastgenomics-py] module
   or by reading the `manifest.json` together with the `config/parameters.json` and `config/input_file_mapping.json`.
   Default values are defined in the `manifest.json`; If you want to re-configure things for special cases, every
   non-default parameter will be defined in the `parameters.json`. If you want to do it on your own see details
   [here](#deep-dive-into-fastgenomics). 
   
   Assuming, that you make use of our [fastgenomics-py] module, you can easily access files and parameters by
   ```python
   import fastgenomics.io as fg_io
   ...
   my_input = fg_io.get_input_path('some_input').open('r').read()
   ...
   fg_io.get_output_path('some_output').open('w').write('some content')
   ... 
   param = fg_io.get_parameter('some_parameter')
   ```
   
5. If you're writing a calculation you have to write a `summary.md` and report on results of the calculations.
   A summary is a [Markdown]-file, that consists of an abstract, describing your calculation, a results-part, as well
   as a list of every parameter used. Using [fastgenomics-py], you can write a summary by:
   ```python
   fg_io.get_summary_path().open('w')
   ```
   
6. Now it's time for a first test of your rewrite: Run your app locally and set paths for testing:
   ```python
   import this
   ...
   import fastgenomics.io as fg_io

   # set paths for local testing (remove before creating docker image!)
   fg_io.set_paths(app_dir='./src', data_root='./sample_data')
   ```
   If everything works like a charm, you can tie up the source-code along with libraries into a docker image, described
   in the following.
   
7. Edit the `Dockerfile`:
   The Dockerfile is some kind of blueprint, how to tie up your application together with requirements into an image.
   Basically you perform install and copy operations and define some default action on starting the container.
   
8. Edit the `docker-compose.yml` in order to mount your local files for testing (the sample_data directory) into your
   application. Later, the FASTGenomics runtime will use your calculation by providing files via mount, and start it.
   Imagine the mount-points, defined in the `docker-compose.yml`, as some file-based gateway, through which you can
   exchange files with other applications.
            
9. Build and run your application with `docker-compose build` and `docker-compose up`. To stop an infinite running app
   run `docker-compose down` or hit Ctrl + C or kill it with `docker kill <id of the container>`which you can lookup by
   `docker ps -a`.
   To inspect your environment use `docker inspect <container>` or get the output by `docker logs <container>`. 


## Deep Dive into FASTGenomics
### Docker

Every application runs in the FASTGenomics runtime in the form of an own docker container (which you can imagine as
self-sustaining, portable workplaces). Using docker containers helps us to eliminate the "works on my machine" problems
and afford full reproducibility and transparency. Moreover using docker containers allows you to use any programming
language and framework you prefer while keeping things as simple as possible for us to integrate your app into an
analysis. You like Python? So do we. You are an Haskel or Julia expert? Just use it! Do you have some special
configuration, which is extremely complicated or annoying to install? Just do it once and your app will work everywhere.

You never heard of Docker before? Read the article [Docker Overview].

These are the very small number of things you really need to know:

- `Dockerfile`: This is the construction plan of your application: Here you decide what to `COPY` into, `RUN` and
  execute (`CMD`) within your container.
- `docker-compose.yml` file: This file describes, how to build and start your container and providing input/output
  directories (volumes) for your container.  Have a closer look at our example in order to test your application in a
FASTGenomics-runtime-like environment.

In order to build and test your container proceed as follows:

0. Install docker on your developer machine [Install Docker]
1. Write the Dockerfile and docker-compose.yml
2. Build your container with `docker-compose -f <docker-compose.filename.yml> build`
3. Provide sample input data (have a closer look at our example) and check paths in the `docker-compose.yml`.  We
recommend relative paths.
4. Start the app via `docker-compose -f <docker-compose.filename.yml> up`

You already have a working python-script? Just clone hello-genomics and interchange the main.py, rename the directory,
and modify the paths in the Dockerfile.

One more thing: Once you started your application (container) you can list all current instances via `docker ps -a`.  To
inspect the output of an application just type `docker logs <container-id>`.

### App structure and manifest.json

Your local application should be structured as follows:

```
.
├── docker-compose.yml (best practise)
├── Dockerfile (mandatory)
├── manifest.json (mandatory)
├── LICENSE (mandatory)
├── README.md (mandatory)
├── requirements.txt (best practise)
├── sample_data (mandatory)
│   ├── config
│   │   └── input_file_mapping.json (if you read files: mandatory)
│   ├── data (contains sample input for your app)
│   │   ├── considered_genes.csv
│   │   ├── ...
│   │   └── some_file.csv
│   ├── output
│   └── summary
├── src (mandatory: source code)
│   ├── hello_genomics 
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── ...
│   │   └── main.py
│   └── templates (optional)
│       └── summary.md.j2
└── test (best practise)
```

FASTGenomics assumes that:

- `manifest.json` is present in the root directory
- `LICENSE` text is present in the root directory
- `Dockerfile` is present in the root directory and defines a default command via `CMD` or `entry_point`
- `sample_data` is present and available for testing (together with a `docker-compose.yml`)

Each app has to provide a `manifest.json` file with the following metadata-entries:

- Name (of the application)
- Type (calculation or visualization)
- class (superior class of application)
- Author information (name, email, organization)
- Description (general description of the app, this can be [Markdown])
- License (name of the license)
- Parameters
- Demands (A list of requirements your app might have. Currently, only GPU is supported and indicates that your app
  needs a GPU to do computations)
- Input (List of files along with a key, under which files can be loaded)
- Output (List of files along with a key, under which files can be stored)

See attached manifest.json for more information.  To validate your directory structure and manifest.json just use
`check_my_app`in the [fastgenomics-py] package.

### Being part of a workflow

```
    ┌────────────┐        ┌────────────┐        ┌────────────┐
    │            │        │            │        │            │
    │  app  N-1  │ ─────> │  your app  │ ─────> │  app  N+1  │
    │  (APPID1)  │ a.txt  │  (APPID2)  │ b.txt  │  (APPID3)  │
    │            │        │            │        │            │
    └────────────┘        └────────────┘        └────────────┘
```

Your app is part of something bigger and a piece of the puzzle: One of our goals is to enable you to create a powerful
analyses composed of small interchangeable applications like yours. To reach the goal, every app should be as universal
as possible. Every app has to declare its in- and outputs so that we know which apps can be combined to a "workflow".

**Example:** If you write a classification app, we would like to know the `Type` and intent (`Usage`-field in the
`manifest.json`) of your input and output. As a consequence, we can avoid feeding your output into another app, which
uses unclustered data as input. In future releases we would like to unify these types and intents and allow for an easy 
to use "Lego"-like interface for your app.

Let's assume your application gets the ID `APPID2` in the FASTGenomics runtime and runs after APPID1 and before APPID3.
Hence you can have access to every output of APPID1 but not APPID3 because it needs your output to run. In the following
section we describe how to access output-data from other applications or have access to the dataset.

The best method to test, if your application can be part of a workflow is by running it with sample data with the
input/output of the following section.

### File input / output

We use files to talk to your app. If you write a calculation app, we expect your output as files, too. Every app can
expect to find these folders:

| Folder  | Purpose  | Mode  |
|---|---|---|
| /fastgenomics/config/   | Here you can find your parameters and configurations     | Read-only  |
| /fastgenomics/data/     | All input files will be located here                     | Read-only  |
| /fastgenomics/output/   | Output directory for your result-files                   | Read/Write |
| /fastgenomics/summary/  | Store your summary here                                  | Read/Write |

To get access to data one could just simply load the data from `/fastgenomics/data/path/to/data.txt` and start your 
calculation but that's not how FASTGenomics works: As your application (ID `APPID2`) is part of a larger workflow, whose 
applications are interchangeable, you can neither know the exact filename nor the APPID from the previous application.
To address this problem, we introduced a file mapping mechanism, in which you define unique keys under which you would 
like to get the actual path of the input-file/output-file.

Lets start with an example: Assume you expect a normalized matrix (access-key `normalized_expression_input`) of the
expression matrix as input (which is produced by app APPID1, a.txt) and you promise to write some data quality related
file "data_quality.json" (access-key `data_quality_output`).

First you have to define your input/output-interface in the `manifest.json` as follows:

*manifest.json:*

```json
"Input": {
        "normalized_expression_input": {
            "Type": "NormalizedExpressionMatrix",
            "Usage": "Genes Matrix with entrez IDs"
        },
        "other_input": {}
},
"Output": {
        "data_quality_output": {
            "Type": "DataQuality",
            "Usage": "Lists the number of genes for data quality overview.",
            "FileName": "data_quality.json"
        },
        "other_output": {}
}
```

Then you can access the files in your python code via:

*your_code.py:*

```python
from fastgenomics import io as fg_io

normalized_input_matrix = fg_io.get_input_path('normalized_expression_input')
with normalized_input_matrix.open() as f:
    # do something like f.read()
    pass
```

Analogous to the input-file-mapping you can write output-files:

*your_code.py:*

```python
from fastgenomics import io as fg_io

my_output_file = fg_io.get_input_path('data_quality_output')
with my_output_file.open('w') as f:
    # do something like f.write('foo')
    pass
```

Using the example of the aforementioned workflow, a typical directory tree, your app `APPID2` would see during runtime,
looks like in the following:

```
/fastgenomics
    ├── config
    │   ├── input_file_mapping.json
    │   └── parameters.json (optional, might not exist)
    ├── data
    │   ├── APPID1
    │   │   └── a.txt
    │   └── some_path_to_dataset
    │       ├── cells.tsv
    │       ├── data_quality.json
    │       ├── expressions_entrez.tsv
    │       ├── genes_considered_all.tsv
    │       ├── genes_considered_expressed.tsv
    │       ├── genes_considered_unexpressed.tsv
    │       ├── genes_entrez.tsv
    │       ├── genes_nonentrez.tsv
    │       ├── genes.tsv
    │       ├── genes_unconsidered_all.tsv
    │       ├── genes_unconsidered_expressed.tsv
    │       ├── genes_unconsidered_unexpressed.tsv
    │       ├── manifest.json
    │       └── unconsidered_genes.tsv
    ├── output
    │   └── b.txt
    └── summary
        └── summary.md
```

```json

"Input": {
        "normalized_expression_input": {
            "Type": "NormalizedExpressionMatrix",
            "Usage": "Genes Matrix with entrez IDs"
        },
        "other_input": {}
},
"Output": {
        "data_quality_output": {
            "Type": "DataQuality",
            "Usage": "Lists the number of genes for data quality overview.",
            "FileName": "data_quality.json"
        },
        "other_output": {}
}
```

The directory `/fastgenomics/data/APPID3` is missing, because of the order of applications:  
your application has to run before APPID3, hence it isn't visible yet.

The actual filename can be looked up in `/fastgenomics/config/input_file_mapping.json`, which looks like the following
example:

```json
{
    "normalized_expression": "APPID1/a.txt"
}
```
This file will be created by the FASTGenomics runtime.

**Hint:**

If you would like to test your application in a FASTGenomics runtime-like environment, you have to provide these
directories and the input_file_mapping.json on your own. As mechanisms could change we highly recommend the usage of
our [fastgenomics-py] python module as described above.

**Warnings:**

- Please do not write any files not defined in the manifest.json!
- Do not expect internet access and even if you'd have some don't use it as reproducibility is not guaranteed.
- Your will not run as root, so don't try to write to protected locations

### Parameters

Your app needs to work with a variety of datasets and workflows, so baking parameters into to app is a bad idea.
Furthermore, such included parameters are not visible to anyone. So please use configuration options, which are more
configurable and can be included in the summary automatically. Please use them!   
You can set parameters and their default values in your `manifest.json`:

*manifest.json:*

```json
"Parameters": {
        "drop_unknown": {
            "Type": "bool",
            "Description": "Drop genes with unknown gene type",
            "Default": false
        },
        "other_parameter": {}
},
```

Type can be one of "Integer", "String", "Bool", "Float", etc. (see [fastgenomics-py] for details).  

If you want to read parameters, we recommend using [fastgenomics-py] as follows:

*your_code.py:*

```python
from fastgenomics import io as fg_io
...
parameters = fg_io.get_parameters()
...
drop_unknown = fg_io.get_parameter('drop_unknown')
...
```

If you want / need to read the parameters without [fastgenomics-py], the process looks like this:

1. Read the "Parameters" section of manifest.json - this contains the parameters and default values as described above.
2. Look at /fastgenomics/config/parameters.json, if this file does not exist you can use default values.
3. If the file does exist - read it and overwrite values from the manifest with the values from this file.
   The file is a json-file containing a dictionary.

**parameters.json Details** 
Each key in the json object corresponds to the name you have defined in your application's manifest.json, e.g. 
`drop_unknown`. In contrast to the `manifest.json` describing the app, the `parameters.json` defines
the parameter values that are used in the current execution of the app. For different datasets and workflows these
values could be changed by the users later. Initially, the values should be set to the default as described in
manifest.json.

**Hints:**

- If you use a random seed (e.g. in the k-means algorithm) fix the seed and add the seed to the parameters, otherwise
  your results will not be reproducible.
- Denote default values of parameters in your `manifest.json` - not in your source code!

### Summary

Reproducibility is a core goal of FASTGenomics, but it is difficult to achieve this without your help.
Docker helps to freeze the exact code and dependencies, your app is using, but code without documentation is difficult
to understand and use. Therefore, apps are expected to have a documentation and provide a so called "summary" of its
results (as [Markdown]). You need to store it as `/fastgenomics/summary/summary.md` - otherwise it would be ignored.

While a generic documentation of your application is specified in the `manifest.json`, we encourage you to describe the
methods and scientific meaning of the results within the summary. This summary should describe the
results, achieved by your application, in terms of an "abstract, a methods and a results"-section of a hypothetically
publication. If necessary provide results of your analysis within the summary:  

For example: "... and identified 14 clusters ..."

*your_code.py:*

```python
from fastgenomics import io as fg_io
...
summary_str = f"... and identified {len(clusters)} clusters ..."

summary_file = fg_io.get_summary_path()
with summary_file.open('w') as f_sum:
    f_sum.write(summary_str)
```

A summary is a [Markdown] file, your app has to write every time it runs.
The file should follow these rules:

- Only use headings h3-h5 (###, ####, #####)
- Sections:
  - Abstract (without heading, just the first lines in the document)
  - Results (h3 heading, upper case, optional for visualizations)
  - Details (h3 heading, upper case, optional for visualizations)
  - Parameters (h3 heading, upper case, contains a list of the parameters)
- Do not provide information like author and lists of input/output files
  These information are filled in automatically.
- Only use parameters, as denoted in your `manifest.json`; don't use constants besides parameters
- Report on all parameters/settings (even default settings)
- Report or fix random seed
- Report on own offline databases (source, date)
- Describe every step of your calculation in the 'Details'-section
- Only write files as denoted in your `manifest.json`

### Miscellaneous

#### Logging

You might wonder how your app can output progress- debug information etc. There is an easy solution for this: simply
write output the stdout /stderr. For example print("hello world"), the user of your app can then see this output.

For enhanced debugging and logging we recommend logging-modules like the python `logging` module (see hello genomics).

To gain access to the output of your running/terminated application type: `docker ps -a` to list all (`-a`) running and
terminated apps and identify the container-id of your application. Then type `docker logs <container-id>` to access
logs.

#### Versions

Most of the time, you want to use version numbers to differentiate versions of your application. This version number is
not included in your manifest.json, since we use a Docker feature: tags. Every Docker image has a tag, which can be
used as the version number.  You can see this with many images, where the part after ":" is the tag.  
E.g.: `python:3.6.1` denotes that we use the python image, with Python version 3.6.1.

You can use any tag except `:latest`, but we recommend an incrementing integer or a Major.Minor.Patch scheme. Please
make sure that each push to our registry uses a new tag, do not attempt to overwrite older versions!

**We highly encourage you to pin all of your dependencies/requirements to ensure reproducibility.**

See also [Publishing](##Publishing) for more details.

#### Exit-Code

Please make sure that your app terminates either with Exit code 0 (success) or a nonzero Exit code, if you encountered
an error during execution. Ensure nonzero exit-code if you encounter any error!

#### User

You app will be executed by a non-root user. So do not try to use a specific user in your app.
Best practice: Develop you app with a non-root user, e.g. the guest account. See the docker [docker-user] instruction.

## Publishing

Checklist:

1. Write your code, respect the file locations as specified in this readme.
2. Write a Dockerfile for your App.
3. Write a manifest.json, which defines the interfaces of your app and provides some additional information.
   Use english for every description!
4. Write a docker-compose.yml and provide sample_date
5. Ship and respect licences
6. Provide a input_file_mapping.json for testing
7. Build and test your application by
   `docker-compose -f <your_compose_file> build`
    and `docker-compose -f <your_compose_file> up`
8. Check your image size: `docker images` gives you an overview.
   Please go easy with image sizes as starting procedure and memory is limited.
   Think twice before submitting images larger than 1GB.
9. Contact us: <contact@fastgenomics.org> in order to integrate your application into FASTGenomics. 
10. Smile: You did it! You just wrote and published your first FASTGenomics application!


[Markdown]: https://github.github.com/gfm/ "GitHub Flavored Markdown"
[fastgenomics-py]: http://www.github.com/fastgenomics/fastgenomics-py
[Docker Overview]: https://docs.docker.com/engine/docker-overview/
[Install Docker]: https://docs.docker.com/engine/installation/ "Install Docker (CE)"
[docker-user]: https://docs.docker.com/engine/reference/builder/#user
[docker tag]: https://docs.docker.com/engine/reference/commandline/tag/#examples
