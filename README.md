

# qzard

qzard is a Crowd Sourced app for Quiz Questions. It is built with [Python][0] using the [Django Web Framework][1].

This project has the following basic apps:

* Accounts (App for user acconts)
* Profiles (App for user profiles)
* Quizes (App for organizing quiz events)
* Quizpool (App for creating quiz questions)

## Installation

### Quick start

To set up a development environment quickly, first install Python 2.7/ Python 3. It
comes with virtualenv built-in. So create a virtual env by:

    1. `$ python3 -m venv qzard`
    2. `$ . qzard/bin/activate`

Install all dependencies:

    pip install -r requirements.txt

Run migrations:

    python manage.py migrate

### Detailed instructions

Take a look at the docs for more information.

[0]: https://www.python.org/
[1]: https://www.djangoproject.com/
