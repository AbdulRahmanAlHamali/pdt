WHEEL_DIR=$(HOME)/.pip/wheels
DOWNLOAD_CACHE_DIR=$(HOME)/.pip/downloads
SHELL := /bin/bash
ENV := .env
GLOBAL_PATH := $(PATH)
PATH := $(PWD)/$(ENV)/bin:$(PATH)
BUILD_PREFIX := /usr/lib/pdt
python_version := 3
cov_report := html
index_url := https://pypi.python.org/simple/
extra_index_url := $(index_url)
wheel_args := --use-wheel
pip_args := $(wheel_args) --index-url=$(index_url) --extra-index-url=$(extra_index_url) --allow-all-external
DEPENDENCIES := $(shell grep -v "\#" DEPENDENCIES)

env:
ifndef local_env
	PATH=/usr/bin/:/usr/local/bin virtualenv $(ENV) --no-site-packages -p python$(python_version)
	pip install -U pip wheel --index-url=$(index_url) --extra-index-url=$(extra_index_url)
	pip install -U setuptools --index-url=$(index_url) --extra-index-url=$(extra_index_url)
	pip install -U devpi-client==2.0.3 --index-url=$(index_url) --extra-index-url=$(extra_index_url)
endif

develop: env
	test -a config.yml || cp config{_example,}.yaml
	pip install -r requirements-testing.txt $(pip_args)
	pip install -r requirements.txt $(pip_args)
ifndef skip_syncdb
	python manage.py syncdb
	python manage.py collectstatic --noinput
endif

test: env
	pip install tox
	tox --recreate -vv

coverage: develop
	py.test --cov=paylogic --cov=codereview --cov-report=$(cov_report) tests

coveralls:
	pip install python-coveralls
	make coverage cov_report=term-missing skip_syncdb=1
	coveralls

clean:
	-rm -rf ./$(ENV) ./build /tmp/pip_build_root

build: clean env
	mkdir -p ./build$(BUILD_PREFIX)
	cp VERSION ./build/
	pip install -r requirements-build.txt --target=./build$(BUILD_PREFIX) --install-option="--install-scripts=$(PWD)/build$(BUILD_PREFIX)/bin" $(pip_args)
	cp -R pdt ./build$(BUILD_PREFIX)
	cp config_build.yaml build$(BUILD_PREFIX)/config.yaml
	cd build$(BUILD_PREFIX); PYTHONPATH=. django/bin/django-admin.py collectstatic --noinput --settings=pdt.settings_build
	rm build$(BUILD_PREFIX)/config.yaml
	mkdir -p build/etc/pdt
	cp config_example.yaml build/etc/pdt/config.yaml
	cp -R deployment/* build/
	cp -R manage.py build/$(BUILD_PREFIX)/bin/

deb: build
	cd build;\
		fpm --name pdt -s dir -t deb -v "`cat VERSION`" --config-files=etc/pdt/config.yaml \
		--config-files=etc/pdt/circus.ini -f \
		`grep -v "\#" ../DEPENDENCIES | xargs -I {} echo "--depends="{}` .

dependencies:
	sudo apt-get install $(DEPENDENCIES) -y
	sudo gem install fpm

wheel: clean env
	$(eval pip_args := --index-url=$(index_url) --extra-index-url=$(extra_index_url) --allow-all-external)
	rm -rf $(DOWNLOAD_CACHE_DIR)
	rm -rf $(WHEEL_DIR)
	mkdir -p $(DOWNLOAD_CACHE_DIR)
	pip wheel -w "$(WHEEL_DIR)" -r requirements-testing.txt $(pip_args)
	for x in `ls "$(DOWNLOAD_CACHE_DIR)/"| grep \.whl` ; do \
		-mv "$$x" "$(WHEEL_DIR)/$${x$(pound)$(pound)*%2F}"; done

upload-wheel: wheel
	devpi use $(devpi_url)
	devpi use $(devpi_path)
	devpi login $(devpi_login) --password=$(devpi_password)
	devpi upload --no-vcs --formats=bdist_wheel $(WHEEL_DIR)/*

.PHONY: test clean wheel upload-wheel deb coveralls coverage develop
