!#/bin/bash
rm -r pytoon.egg-info dist build
python3 setup.py sdist bdist_wheel
twine upload dist/*  