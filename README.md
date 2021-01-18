# ![](https://raw.githubusercontent.com/yudai/gotty/master/resources/favicon.png) Gather DNS Information Script
## What do we have here?

This repo contains a simple script that will connect to Dynect / AWS Route 53 according to an input.yml file.

Basically, the following files will be present:

| File Name        | Usage                                                         |
| ---------------- |:-------------------------------------------------------------:|
| main.py          | Python script, usage will be explained below.                 |
| requirements.txt | Requirements file to get the modules needed.                  |
| input_example.yml| YML file that will trigger the gathering among DNS Providers  |

## Usage
1. Clone the Repository
2. Create a [Virtual Environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
3. Run `pip install -r requirements.txt` inside your Virtual Environment
4. Create an `input.yml` file from `input_example.yml`. You can either a single DNS provider or both.  
5. You can run `python main.py -h` to get the list of parameters or `python main.py` to run it with the default parameters.
   1. By default, the path that will be looked for the Input is `./input.yml`. As well, it will provide the output as YYYYMMDDHHMM_dns_report.csv
   2. You can provide the input parameter by running `python main.py -i <path_to_your_yml>`
   3. You can specify the output file name by issuing `python main.py -o <new_filename>`
7. Enjoy

