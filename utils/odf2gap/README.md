This script is written to help people who need to convert spreadsheets
from OpenOffice into Gap Analysis information

It currently supports using two columns: Funcionality category and
Funcionality name. At the moment, if the functionality anem is longer than a
line or has a colon (:) it sends the rest of the text to the description
field.

Requirements:
xmlrpclib, ezodf2 both installable through easy_install

TODO:

- Configuration file
- Ability to configure columns to match fields on OpenERP
- Ablity to read more values like effort, mandatoriness and estimated time

suggestions are welcome cmaldonado@covetel.com.ve
