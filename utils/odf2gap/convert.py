 # coding=UTF-8
import xmlrpclib, settings
import ezodf2

#Get params from settings.py
username = settings.username
pwd = settings.pwd
dbname = settings.dbname

category_dict = { 'Category 1': 2,
                  'Category 2': 3,
                  'Category 3': 4,
                  'Category 4': 5,
}

# Get the uid
sock_common = xmlrpclib.ServerProxy ('http://'+settings.host+':8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
print uid 

#replace localhost with the address of the server
sock = xmlrpclib.ServerProxy('http://192.168.213.161:8069/xmlrpc/object')                                                                                   
print sock

file_path = settings.filepath
filename = settings.filename
start_row = 7
start_column = 1

spreadsheet = ezodf2.opendoc(file_path + filename)

sheets = spreadsheet.sheets

table = sheets[0]

rowcount = table.nrows()

current_cell = table[start_row, start_column]
print table.name
print start_column, start_row


last_category = None
for i in xrange(start_row, rowcount, 1):
    category = table[i, start_column]
    if category.value:
        print category.value
        cat_number = category_dict[category.value.encode('utf-8')]
        last_category = table[i, start_column]
    else:
        print last_category.value
        cat_number = category_dict[last_category.value.encode('utf-8')]
    function = table[i, start_column + 1]
    if function.value:
        function_lines = function.value.split('\n')
        first_line = None
        second_line = ''
        for line in function_lines:
            if ":" in line:
                function_name = line.split(':',1)
            else:
                function_name = line.split('\n')
            for cell in function_name:
                if not first_line:
                    first_line = cell
                else:
                    second_line += "\n" + cell

            function_name = first_line
            function_desc = second_line

    print function_name
    print function_desc
    functionality = { 
        'category' : cat_number,
        'name': function_name,
        'description': function_desc,
        'is_tmpl': True,
    }   

    partner_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'create', functionality)
