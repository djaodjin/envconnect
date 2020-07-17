Envconnect webapp
=================

This Django project contains the web application for the enviro-connect project.

Prerequisites
-------------

    $ make require

Install
-------

    $ make install
    $ make initdb


Development setup: Step-by-step
-------------------------------

Install prerequisites and configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $ python -m venv envconnect
    $ source envconnect/bin/activate
    $ mkdir -p envconnect/reps
    $ cd envconnect/reps
    $ git clone https://github.com/djaodjin/envconnect.git
    $ cd envconnect

    $ ../../bin/pip install -r requirements.txt -r dev-requirements.txt
    $ make install
    $ make initdb
    $ make vendor-assets-prerequisites
    $ make build-assets
    $ diff -u ../../etc/envconnect/site.conf
    -DEBUG=False
    +DEBUG=True

Launching and debugging the full webserver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $ supervisord
    # browse http://localhost:8000/envconnect/


Running the new Vue client by itself
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

```
$ cd clients/web
$ yarn serve
# browse http://localhost:8080/envconnect/
```

Lints and fixes files
~~~~~~~~~~~~~~~~~~~~~

```
$ cd clients/web
$ yarn lint
```

Vue client Locales
~~~~~~~~~~~~~~~~~~

The app uses [vue-i18n](https://www.codeandweb.com/babeledit/tutorials/how-to-translate-your-vue-app-with-vue-i18n) to manage the translations of its content strings. Additionally, the UI framework (vuetify) has its own translations. This means that when changing locales for the app, remember to: 
- Add the locale file for the content in `src/locales`
- Update the locales list in `LocaleChanger.vue`
- Update the imports and the `lang.locales` option in `src/plugins/vuetify.js`

The app's default locale and fallback locale are set via the environment variables `VUE_APP_I18N_LOCALE` and `VUE_APP_I18N_FALLBACK_LOCALE` respectively.


Testing
-------

    supplier user account: steve, yoyo
    supplier manager user account: alice, yoyo
    website administrator: donny, yoyo
