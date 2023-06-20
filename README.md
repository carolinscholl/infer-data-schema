# infer-data-schema
Infer the json or csv schema from a given data file
<br/><br/>
## Description
Continuously checking data against a schema allows the detection of errors and schema updates. It is a minimal requirement
for data quality monitoring. However, the manual generation of a schema is time-consuming and requires in-depth 
knowledge of the syntax of the respective schema standard. Using this library, one can automatically generate a first
draft of a json or csv data schema. This should be reviewed and potentially be corrected by a data owner or expert. 

For json files, a schema draft according to the [JSON Schema](https://www.json.org/json-en.html) (Draft 6 and above) is automatically created using the [genson](https://github.com/wolverdude/GenSON) schema generator. 

For csv files, custom code is used to generate a schema draft according to [CSV Schema language 1.2](https://digital-preservation.github.io/csv-schema/csv-schema-1.2.html#dfn-permitemptydirective-0). 
A validator exists for this schema language and can be downloaded from [here](https://github.com/digital-preservation/csv-validator/releases). The validator expects a data file and the corresponding schema file. It validates if the data agrees with the schema. 
With this tool you can create a schema draft, which you can review and correct to eventually use it for validation.

Notes on csv-schema generation: 
Numeric data types are inferred by trying to parse the variables as a specific data type. Other data types such as dates are 
inferred by comparing the variable values against defined literals as regular expressions.
The automatic schema inference only infers data types. Limits are not set, with one exception for numeric variables: If
a column has more than 100 non-null entries and all of them are >=0, the variable is expected to be positive numeric (including zero).
A variable is considered to be categorical if it has less than 25 unique non-missing values and [this](https://jeffreymorgan.io/articles/identifying-categorical-data/) condition with an adaptively calculated threshold applies.

**Note: csv schema generation is not yet optimized and may crash for very large csv files.**
<br/><br/>
## Dependencies
- python ~= 3.8
- [pipx](https://pypa.github.io/pipx/) or [conda package manager](https://docs.conda.io/en/latest/)
- modules listed in environment.yml (see installation instructions below)
<br/><br/>

## Installation
1. Clone the repository.
2. Navigate to the local repository (`cd <path-to-local-repository>`) (on Windows, open Anaconda Prompt and execute `cd /d "<path-to-local-repository>"`)
<br/><br/>
### Option 1: Install and run with pipx
1. If you have pipx installed, execute `pipx install .` at the root of this repository. This will trigger the installation. 
2. Then you can run `run-schema-inference <data-file-path> <optional-schema-file-path>`
<br/><br/>
### Option 2: Install and run with conda
Both the bash and the shell script activate a conda environment and run the code within that.
1. Install the conda environment `conda env create -f environment.yml` (On Windows: Set CONDAPATH in run_inference.bat if it deviates from the one specified.)
2. Run the shell script or Batch file depending on your operating system:
   - On Linux (tested on Ubuntu 20.04.5 LTS): Execute `./run_inference.sh <data-file-path> <optional-schema-file-path>`
   - On Windows 10: Execute `./run_inference.bat <data-file-path> <optional-schema-file-path>` in Windows PowerShell or Anaconda Prompt.
<br/><br/>

After running the schema inference, a schema will be created and saved under the specified schema path (if provided).
If no schema path is provided, the generated schema will be saved in the same directory as the data file with the suffix "_schema-draft". The extensions ".json" and ".csvs" will be used for the schema files, respectively. 
Both absolute and relative paths are accepted. However, no spaces are allowed in the paths provided as parameters.
<br/><br/>
## Tests
Currently, only the csv schema generation is tested for a dummy csv file. The generated schema is compared against a saved ground-thruth file. 
The test can be run from the console on linux by executing `./run_test.sh`. Alternatively, run the tests manually in an IDE or from the console (activate infer-schema conda environment and run `python -m unittest discover test`).
<br/><br/>
## Contribution
Please do not hesitate to reach out, raise an issue or open a pull request.
