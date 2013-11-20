 # coding=UTF-8
import xmlrpclib, settings
import ezodf2

#Get params from settings.py
username = settings.username
pwd = settings.pwd
dbname = settings.dbname

global category_dict

category_dict = { }

priority_dict = { 'Mandatorio': 4,
                  'Prioritario': 3,
                  'Deseable': 2,
                  'No Necesario': 1,
}

# Get the uid
sock_common = xmlrpclib.ServerProxy ('http://'+settings.host+':8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
print uid 

#replace localhost with the address of the server
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')                                                                                   
print sock

file_path = settings.filepath
filename = settings.filename
start_row = 5
start_column = 1

global spreadsheet 
global sheets
global table
global rowcount
global current_cell

spreadsheet = ezodf2.opendoc(file_path + filename)

sheets = spreadsheet.sheets

table = sheets[0]

rowcount = table.nrows()

current_cell = table[start_row, start_column]

print table.name
print start_column, start_row

def search_category_on_oerp(category_i_need):
    category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'search', category_i_need)
    if category_id:
        return category_id
    else:
        return None
    

def get_categories_from_ods(start_row, rowcount):
    for i in xrange(start_row, rowcount, 1):
        current_category = table[i, start_column]
        if current_category.value and current_category not in category_dict:
            category_dict[current_category.value.encode('utf-8')] = 0


def create_categories_on_oerp():
    for key in category_dict.keys():

        if search_category_on_oerp(key):
            cat_name = key;
            cat_capitalized = key.capitalize()
            parent = None
            seq = 0
            
            new_category = { 
                'name': cat_name,
                'code': cat_capitalized[:7],
                #        'parent_id': parent,
                #        'sequence': seq
            }   
        
            category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'create', new_category)
            category_dict[key] = category_id
            print cat_name, category_id
#        print category_dict    

get_categories_from_ods(start_row, rowcount)
create_categories_on_oerp()

print len(category_dict)
#print category_dict
print "----------"


last_category = None
for i in xrange(start_row, rowcount, 1):
    category = table[i, start_column]
    if category.value:
#        print category.value
        cat_number = category_dict[category.value.encode('utf-8')]
        last_category = table[i, start_column]
    else:
#        print last_category.value
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

#    print function_name
#    print function_desc
    functionality = { 
        'category' : cat_number,
        'name': function_name,
        'description': function_desc,
        'is_tmpl': True,
    }   

#    partner_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'create', functionality)
