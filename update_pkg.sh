!#/bin/bash
pip3 uninstall pytoon
rm -rf dist/
python3 setup.py sdist bdist_wheel
twine upload dist/*