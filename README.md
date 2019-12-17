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

## Encrypt settings


macOS:
```
brew install git-crypt
git-crypt unlock secret
```

## Setup database


macOS:
```
brew install postgresql
brew services start postgresql
 
psql postgres

# username, password, DB name should be the same as specified in the local settings
CREATE ROLE user WITH LOGIN PASSWORD 'password';
CREATE DATABASE databasename;

python manage.py migrate
```

## Setup FFMPEG

```
FFMPEG settings are hardware specific.
Check STEPIC_STUDIO/settings/base.py for details.
```

## Run

macOS and Linux, not sure about Windows:

```
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

workon studio-env

# not sure about the next line:
python manage.py runserver --noreload --insecure
```
