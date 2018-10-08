# Install

## Install Python and pip

* Python 3.5+
* pip 18.0+
* `pip install virtualenvwrapper`

## Setup Virtual Environment:

macOS and Linux, not sure about Windows:
```
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv -p /path/to/python3 studio-env
# Example: mkvirtualenv -p /usr/local/bin/python3 studio-env
```

## Install requirements into virtualenv


```
pip install -r requirements.txt
```

# Run

macOS and Linux, not sure about Windows:

```
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

workon studio-env

# not sure about the next line:
python manage.py runserver --noreload --insecure
```