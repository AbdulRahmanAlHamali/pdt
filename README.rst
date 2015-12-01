Paylogic Deployment Tool
========================

`Paylogic Deployment Tool` manages paylogic migrations, deployments and releases.

If you want to use it, please read the documentation below.

.. image:: http://img.shields.io/coveralls/paylogic/pdt/master.svg
   :target: https://coveralls.io/r/paylogic/pdt
.. image:: https://travis-ci.org/paylogic/pdt.svg?branch=master
    :target: https://travis-ci.org/paylogic/pdt
.. image:: https://readthedocs.org/projects/pdt/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/pdt/

.. contents::


REST API client
---------------

There is a command line REST API client implemented as a separate project, see `pdt-client <https://github.com/paylogic/pdt-client>`_


Development Environment
-----------------------

To set up the development environment, run:

::

    # install system dependencies, requires sudo access!
    make dependencies

    # install python dependencies, initialize configs
    make develop


Then, to run the django development server:

::

    .env/bin/python manage.py runserver

Open a browser, go to http://127.0.0.1:8000/ and you can use the `PDT`.


Production Deployment
---------------------

Automatic way - debian package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    make deb [index_url=<local pypi index>]

This command will create debian package (located in ``./build/pdt_<version from ./VERSION>.deb``)
with the application. Important file locations:

``/etc/pdt/config.yaml``
    Default configuration which you need to adjust

``/etc/pdt/circus.ini``
    PDT circus supervisor configuration (you shouldn't need to change this)

``/etc/init/pdt.conf``
    Upstart configuration for PDT circus supervisor (you shouldn't need to change this)

``/var/lib/pdt/db.sqlite3``
    Default PDT sqlite3 database location (this is only the case if the database backend is sqlite3)

``/usr/lib/pdt``
    PDT code location


Manual way - build folder
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    make build [index_url=<local pypi index>]

This command will make ./build folder containing all needed to run the application.

The preferred method to deploy Django applications is to use WSGI supporting
web server. Use ``build/wsgi.py`` file as WSGI script.

There is one important thing to remember. Django serves media (static) files
only in development mode. For running PDT in a production environment,
you need to setup your web-server to serve the /static/ alias directly from the ``./build/static`` folder.

Here is the tutorial for deployment with `uwsgi <https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/uwsgi/>`_

Make sure that production server has system packages mentioned in `<DEPENDENCIES>`_ file are installed (ubuntu 14.04).

After the deployment of the build folder to the production server:

::

    cd <build folder>
    # apply database migrations
    PYTHONPATH=. django/bin/django-admin.py syncdb


Using wheels
------------

To speedup the build process, 2 make targets are implemented:

`make wheel`
    Build `wheels <https://pypi.python.org/pypi/wheel>`_ for all python dependencies, storing them in the
    cache directory

`make upload-wheel` (depends on `make wheel`)
    Upload previously generated wheels to given private `devpi server <https://pypi.python.org/pypi/devpi-server>`_.

    Parameters:

* `devpi_url` - devpi server URL to use
* `devpi_path` - index path to upload to
* `devpi_login` - login to use for devpi authorization
* `devpi_password` - password to use for devpi authorization

After you'll upload wheels, `make build` and `make develop` time will be dramatically reduced, if you will
pass `index_url` parameter pointing to the same devpi server index you used for `make upload-wheel`, for example:

::

    make build index_url=https://my.pypi.com/index/trusty/+simple/

Be aware that binary wheels can only be used on exactly same architecture and environment as they were built.


Configuration
-------------

For secret configuration, the nice `YamJam <http://yamjam.readthedocs.org/en/latest/index.html>`_ is used.

Secret settings are loaded from 2 places:

/etc/pdt/config.yaml
    place the production secrets there
<pdt root>/config.yaml
    place the local development secrets there

Example of the configuration

.. code-block:: yaml

    pdt:
        django_secret_key: my-secret-key-value
        database:
            engine: django.db.backends.sqlite3
            name: db.sqlite3
            user:
            password:
            host:
            port:
        raven:
            dsn: # http://some-raven-dsn
        api:
            token: some-api-token
        fogbugz:
            token: some-fogbugz-token
            url: http://fogbugz.example.com
            ci_project_field_id: cixproject
            migration_url_field_id: dbxmigration
            revision_field_id: revision
        hostname: localhost
        debug: true
        celery:
            broker_url: redis://localhost:6379/0
            result_backend: redis://localhost:6379/0
            scheduler_url: redis://localhost:6379/1
        cache:
            redis:
                host: localhost
                port: 6379
                db: 3


License
-------

This software is licensed under the `MIT license <http://opensource.org/licenses/MIT>`_


© 2015 Paylogic International.
