PACKAGE=anno117_item_inspector
VENVNAME=tamm

##############################################################################
# do this while not in venv
venv:
	python -m venv .$(VENVNAME).venv

venv.clean:
	rd /s /q .$(VENVNAME).venv



##############################################################################
# do these while in venv
run: libs.quiet
	py $(PACKAGE).py


# libs make targets ###########################
libs: requirements.txt
	pip install -r requirements.txt

libs.quiet: requirements.txt
	pip install -q -r requirements.txt

libs.clean:
	pip uninstall -r requirements.txt


# game data (compact per-version packages, see BUILD.md) ###########################
data.build:
	py build_version_data.py --all

# exe make targets ###########################
exe: libs
	pyinstaller --onefile --windowed --add-data "data/ui;data/ui" --add-data "data/fonts;data/fonts" --add-data "data/versions;data/versions" --icon="app_icon.ico" --version-file="file_version_info.txt" --name "Anno 117 Item Inspector" $(PACKAGE).py

exe.clean:
	rd /s /q build
	del /q dist\$(PACKAGE).exe
	del /q $(PACKAGE).spec


# general make targets ###########################

all: libs exe

all.clean: libs.clean exe.clean

clean: all.clean