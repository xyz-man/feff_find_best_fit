![Linux](https://img.shields.io/badge/-Linux-grey?logo=linux)
![Usage](https://img.shields.io/badge/Usage-FEFF9%20find%20best%20fit-red)
![Python](https://img.shields.io/badge/Python-v3.6%5E-orange?logo=python)

## Index

* [Description](#description)
* [Features](#features)
* [Installation](#installation)

## Description

**[FEFF9](http://feff.phys.washington.edu/feffproject-feff.html) find best fit** this is a cli app for compare theoretical and experimental spectra and find the best fit for 
their linear combinations.


## Features

* Automatic compare spectra.
* Separate configuration file

## Installation

### 1. Create Virtual Python Environment and Install Python3 interpreter
Additional information on https://www.python.org/downloads/
and 
[Creation of virtual environments](https://docs.python.org/3/library/venv.html)

or simple way to create subfolder venv (with python packages) inside the current directory:

    $ python -m venv venv

### 2. Clone this repository into your directory

    $ mkdir feff_find_best_fit && cd feff_find_best_fit
    
    
    $ git clone https://github.com/xyz-man/feff_find_best_fit.git
        or
    $ git clone -b develop https://github.com/xyz-man/feff_find_best_fit.git

### 3. Install requirements


    $ pip install -r requirements.txt
    
### 4. Configuration

Edit the `settings.py` file and change needed values. 
      
### 5. Run

Inside the root project directory (`.feff_find_best_fit/`) activate local virtual environments:

    $ source venv/bin/activate
    
and run `main.py` file:

    $ python main.py
    


### 6. License

**FEFF9 find best fit** has been created under the **GNU GPLv3 license**