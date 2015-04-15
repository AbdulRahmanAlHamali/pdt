WHEEL_DIR=$(HOME)/.pip/wheels
DOWNLOAD_CACHE_DIR=$(HOME)/.pip/downloads
SHELL := /bin/bash -x
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
DEPENDENCIES := $(shell grep -h -v "\#" DEPENDENCIES)
BUILD_DEPENDENCIES := $(shell grep -h -v "\#" DEPENDENCIES*)
DEB_LICENCE := MIT
DEB_VENDOR := Paylogic
DEB_CATEGORY := deployment
DEB_MAINTAINER := Paylogic developers <develpoers@paylogic.eu>
DEB_DESCRIPTION := Paylogic deployment tool
DEB_URI := https://github.com/paylogic/pdt
DEB_USER := pdt
DEB_GROUP := pdt
DEB_DIST := $(shell lsb_release -cs)

env:
ifndef local_env
	PATH=/usr/local/bin/:/usr/bin:$(GLOBAL_PATH) virtualenv $(ENV) --no-site-packages -p python$(python_version)
	easy_install -U --index-url=$(index_url) pip wheel
	pip install -U --index-url=$(index_url) --extra-index-url=$(extra_index_url) setuptools
	pip install -U --index-url=$(index_url) --extra-index-url=$(extra_index_url) devpi-client==2.0.3
endif

config:
	test -a config.yaml || cp config{_example,}.yaml

develop: env config
	pip install -r requirements-dev.txt $(pip_args)
ifndef skip_syncdb
	python manage.py syncdb
endif
	python manage.py collectstatic --noinput

test: env config
	pip install tox
	tox --recreate -vv

coverage: develop
	py.test --cov=paylogic --cov=codereview --cov-report=$(cov_report) tests

coveralls:
	pip install python-coveralls
	make coverage cov_report=term-missing skip_syncdb=1
	coveralls

clean:
	git clean -f -d
	-rm -rf ./$(ENV) ./build /tmp/pip_build_root

build: env
	rm -rf ./build
	mkdir -p ./build$(BUILD_PREFIX)
	cp VERSION ./build/
	pip install -r requirements-build.txt --target=./build$(BUILD_PREFIX) \
		--install-option="--install-scripts=$(PWD)/build$(BUILD_PREFIX)/bin" $(pip_args)
	cp -R pdt ./build$(BUILD_PREFIX)
	cp config_build.yaml build$(BUILD_PREFIX)/config.yaml
	cd build$(BUILD_PREFIX); PYTHONPATH=. django/bin/django-admin.py collectstatic --noinput \
		--settings=pdt.settings_build
	rm build$(BUILD_PREFIX)/config.yaml
	cp -R deployment/* build/

deb: build
	cp -R deployment/* build/
	cd build;\
		fpm \
		--name pdt \
		-s dir \
		-t deb \
		-f \
		--version="`cat VERSION`" \
		--config-files=etc/pdt \
		--config-files=etc/init \
		--license='$(DEB_LICENCE)' \
		--vendor='$(DEB_VENDOR)' \
		--category='$(DEB_CATEGORY)' \
		--maintainer='$(DEB_MAINTAINER)' \
		--description='$(DEB_DESCRIPTION)' \
		--url='$(DEB_URI)' \
		--deb-user=$(DEB_USER) \
		--deb-group=$(DEB_GROUP) \
		--deb-changelog=../CHANGES.rst \
		--directories=var/lib/pdt \
		--directories=usr/lib/pdt \
		--directories=etc/pdt \
		--directories=var/log/pdt \
		--before-install=../deployment/usr/lib/pdt/bin/before-install \
		--after-install=../deployment/usr/lib/pdt/bin/after-install \
		--before-remove=../deployment/usr/lib/pdt/bin/before-remove \
		`grep -v "\#" ../DEPENDENCIES | xargs -I {} echo "--depends="{}` .

upload-deb: deb
	$(foreach file, $(wildcard build/*.deb), \
		$(shell \
			scp $(file) reprepro@apt.deployment.paylogic.eu:/data/debian/incoming/ && \
			ssh reprepro@apt.deployment.paylogic.eu 'reprepro -b /data/debian includedeb $(DEB_DIST) /data/debian/incoming/$$(basename "$(file)"); \
			rm -rf /data/debian/incoming/pdt_*' \
	))

dependencies:
	sudo apt-get install $(BUILD_DEPENDENCIES) -y
	sudo gem2.0 install --no-ri --no-rdoc fpm

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

.PHONY: test build clean wheel upload-wheel deb coveralls coverage develop
