from setuptools import find_packages, setup


setup(
    name="django-report-builder",
    version="6.6.0",
    author="David Burke",
    author_email="david@burkesoftware.com",
    maintainer="Mustafa Ülker",
    maintainer_email="mustafaulker.cs@gmail.com",
    description="Query and Report builder for Django ORM",
    license="BSD",
    keywords="django report",
    url="https://github.com/mustafaulker/django-report-builder",
    packages=find_packages(exclude=["report_builder_demo", "report_builder_demo.*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.4',
    install_requires=[
        'openpyxl>=3.1.0',
        'python-dateutil',
        'djangorestframework>=3.8.0',
    ],
)
