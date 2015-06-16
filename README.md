PyDumpy
=======

This is a clone of version r16 at https://code.google.com/p/pydumpy/source/browse/trunk/src/pydumpy.py, authored by https://github.com/z1lv1n4s. 

PyDumpy is a simple tool written in Python that enables easy partial and sorted MySQL database dumping. PyDumpy is perfect when a quick production database snapshot is required with only partial data. Production databases may have hundreds of gigabytes of data which is not always easy or fast to dump and deploy on a development machine.

PyDumpy will dump the whole database by limiting all tables to a default value of 100 000 rows. It also provides a possibility to ask the user which tables to limit and how to sort them before dumping.

Dependencies
------------

PyDumpy relies on MySQL for Python package to connect to mysql and query the information schema.

Getting Started
---------------

PyDumpy should work with Python 2.6.4 and MySQL 5 versions and above. PyDumpy queries the information schema to find out the approximate count of rows available in the database tables and then uses mysqldump tool to dump each table separately. PyDumpy allows to pass external options to mysqldump by using the -e command line option.

Dependencies
------------

PyDumpy relies on MySQL for Python package to connect to mysql and query the information schema. To install the package using pip:

    $ pip install pymysql


Or on Debian or Ubuntu you might just use the package from the linux distribution:

    $ apt-get install python-mysqldb

If you are on a shared host and have not enough permissions see instructions below on how to create a local python virtualenv.

Installation
------------

PyDumpy does not require any installation since it's a simple script written in Python. You can make it executable by chmoding it:

    $ chmod +x pydumpy.py

Running on the Command Line

    $ pydumpy.py options
    -H or --hostname: MySQL database hostname. Required.
    -u or --username: MySQL database username. Required.
    -p or --password: MySQL database password. Required.
    -n or --database: MySQL database name. Required.
    -e or --options: Additional mysqldump options. Default empty.
    -f or --file: File to dump to.
    -r or --limit: Maximum number of rows per table. Default 100000.
    -l or --ask-to-limit: Ask to provide a row limit for each table.
    -s or --ask-to-sort: Ask to provide sorting keys for each table.

Usage Examples
--------------

To dump a database to a file:

    ./pydumpy -H localhost -u username -p password -n database --file=dump.sql

To dump a maximum of 50 000 rows from each database table to standard output:

    ./pydumpy -H localhost -u username -p password -n database -r 50000

To dump a maximum of 10 000 rows from each database table but allowing to override the setting for some tables:

    ./pydumpy -H localhost -u username -p password -n database -r 50000 --ask-to-limit --file=dump.sql

To dump with additional MySQL options for ex. removing comments:

    ./pydumpy -H localhost -u username -p password -n database -r 10000 -e "--skip-comments"

By default PyDumpy will output to standard output. It's possible to redirect all output using a standard pipe but then options like --ask-to-limit or --ask-to-sort won't work. Instead please use the --file option to specify the file to dump to.


How to install a local python virtualenv in a shared hosting with python 2.7 ?
------------------------------------------------------------------------------

In a shared hosting environment it can be otherwise impossible to install the required python packages.

1) Download the latest virtualenv tar.gz from https://pypi.python.org/pypi/virtualenv#downloads und untar it.

2) cd into the new virtualenv.xxx/

Create a new virtualenv by giving its target path as the last parameter:

3) python virtualenv.py ~/private/venv

To activate it:

    cd ~/private/venv
    . bin/activate

The venv will have its own pip and everything. Now install the necessary packages:

    pip install pymysql

Just copy pydumpy.py into the venv/ folder and run it from inside the virtual environment.

Contact
-------

Contact the original author (z1lv1n4s - https://github.com/z1lv1n4s) at https://code.google.com/p/pydumpy/

