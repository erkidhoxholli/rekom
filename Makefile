ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYGETTEXT_FILE:=$(shell locate pygettext.py | head -n 1)

generate_translations:
	echo ">>>>>> Generating translations"
	cd $(ROOT_DIR)

	$(PYGETTEXT_FILE) -d base -o translations/base.pot main.py

	cp translations/base.pot translations/en/LC_MESSAGES/base.po
	mv translations/base.pot translations/pl/LC_MESSAGES/base.po

	echo "** Po files generated successfully under /translations directory"
	echo "** Please use PoEdit to open po files and generate mo files that will be used for translations"

run:
	echo ">>>>>>>> Running the project"
	uvicorn main:app --reload