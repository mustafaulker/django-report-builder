# django-report-builder

A GUI for Django ORM. Build custom queries and display results.
Targets sys admins and capable end users who might not be able to program or gain direct interactive shell access.

## Works as expected on Django 5 also.

# News

## 6.6.0
- Split files and zip them when the row count exceeds one million.

## 6.5.7
- Remove mis-import

## 6.5.6
- Fix dynamically static-file path generating
- Remove redundant code

## 6.5.5

- Remove six dependency
- Replace deprecated openpyxl save_virtual_workbook func. (Cherry-picked from @tmszi's fork)

## 6.5

- Make compatible for Django >4. Project's GitLab Repo merged into this fork and Django 4 compatibility changes were made.

View more on the [CHANGELOG](CHANGELOG).

# What is Django Report Builder?

![](docs/screenshots/reportbuilderscreen.jpg)

## Features

* Add filters
* Add display fields
* Preview and create xlsx reports
* Uses Django permissions models - Staff users must have "change" or "view" permission to view
  reports. Unprivileged users can still build reports and see database schema.
    * Report builder is intended for generally trusted staff users and requires is_staff to be set.
* Export to Report global admin action
* Scheduled reports can generate and send to users on cron like schedule
* Optional asynchronous report generation

# Documentation

http://django-report-builder.readthedocs.org/

[Google group](https://groups.google.com/forum/#!forum/django-report-builder/).

[Contributing](http://django-report-builder.readthedocs.org/en/latest/contributors/)

## Development quick start

This package uses Django in Docker and Angular CLI for development purposes.

1. Start docker `docker-compose up`
2. Migrate and create an admin user `docker-compose run --rm web ./manage.py migrate`
3. Start the Angular CLI server. Ensure Node is installed. `cd js`, `yarn`, `yarn start`
4. Django runs on port 8000 by default. Go to localhost:8000/admin and log in.
5. Angular runs on port 4200. Now that you are logged in, go to localhost:4200

More detailed instructions are at [here](https://django-report-builder.readthedocs.io/en/latest/contributors/)
