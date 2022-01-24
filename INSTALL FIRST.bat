@echo on
pip install pipenv

set PIPENV_VENV_IN_PROJECT=1
pipenv install

pip-compile --generate-hashes --no-index --output-file=requirements.txt requirements.in




pause ------===== Installed! You can now use the launchers!=====------
exit
