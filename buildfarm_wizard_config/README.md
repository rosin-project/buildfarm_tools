# Buildfarm wizard

![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable](https://www.repostatus.org/badges/latest/wip.svg "Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release")

## Setup

In order to setup the buildfarm wizard, make sure you have the following packages installed: `python3`, `python3-venv` (install with `apt-get`).

And then run the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

To start the application, run the following command:

```bash
FLASK_APP=flaskr flask run
```

To start in Debug mode:

```bash
FLASK_APP=flaskr TESTING=1 flask run
```

## tools

To launch `ipython` on the virtual environment:

```bash
source venv/bin/activate
pip install ipython
python -m IPython
```
