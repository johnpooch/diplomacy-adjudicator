# Diplomacy Adjudicator

## Getting Started

Clone the repo and create a `virtualenv` called `env`. Activate the `virtualenv`
and install dev requirements.

```shell
virtualenv env
env/bin/pip install -r requirements.txt
source env/bin/activate
pip install -r dev_requirements.txt
```


## Running the tests

Make sure you are inside your virtual environment and have installed dev requirements.
From the project root run `nosetests` to run all of the tests.

To run specific test files, add the path to the tests:
```shell script
nosetests adjudicator/tests/datc/test_a.py
```
