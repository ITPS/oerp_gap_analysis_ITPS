 # coding=UTF-8
import xmlrpclib, settings, re
import ezodf2

#Get params from settings.py
username = settings.username
pwd = settings.pwd
dbname = settings.dbname

global category_dict

category_dict = { }

# this is the priority dictionary
priority_dict = { 'Mandatorio': 4,
                  'Obligatorio': 4,
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

# open the ODS file
spreadsheet = ezodf2.opendoc(file_path + filename)

# assign the spreadsheet objects to a list
sheets = spreadsheet.sheets

# use the first spreadsheet
table = sheets[0]

# count the amounnt of rows
rowcount = table.nrows()

current_cell = table[start_row, start_column]

print table.name
print start_column, start_row

#this function creates parent categories when needed
def create_parents(category):
    category = re.sub(": ", ":", category)
    pieces = category.rsplit(":")
    for i in xrange(0, len(pieces) - 1,1):
        if not search_category_on_oerp(pieces[i]):
            create_category_on_oerp(pieces[i])

def set_category_parent(category):
    category = re.sub(": ", ":", category)
    pieces = category.rsplit(":")
    for i in xrange(0, len(pieces),1):
        if i != 0:
            child_category_id = search_category_on_oerp(pieces[i])
            parent_id = search_category_on_oerp(pieces[i-1])
            if parent_id:
                values = {'parent_id' : parent_id[0]}
                category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'write', child_category_id, values)

# this function searches for a category on an OpenERP model
def search_category_on_oerp(category_i_need):
    my_query  = [('name', '=', category_i_need),]
    category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'search', my_query)
    if category_id:
        return category_id
    else:
        return None
    
# this functions extracts a series of categories from a column in an ODS file
def get_categories_from_ods(start_row, rowcount):
    for i in xrange(start_row, rowcount, 1):
        current_category = table[i, start_column]
        if current_category.value and current_category not in category_dict:
            category_dict[current_category.value.encode('utf-8')] = 0

# this functions creates a category in a gap analysis deta model on OpenERP
def create_category_on_oerp(key):
    if not search_category_on_oerp(key):
        category = re.sub(": ", ":", key)
        category = category.rsplit(":")
        cat_name = category[len(category)-1]

        cat_capitalized = key.capitalize()
        seq = 0
        
        new_category = { 
            'name': cat_name,
            'code': cat_capitalized[:7],
            #        'sequence': seq
        }   
        
        category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'create', new_category)
        category_dict[key] = category_id
        print cat_name, category_id

        return category_id

# regular program flow

get_categories_from_ods(start_row, rowcount)
for key in category_dict.keys():
    if ":" in key:
        create_parents(key)
    child_category_id = create_category_on_oerp(key)
    set_category_parent(key)

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
            function_desc = function.value
            try:
                critical = priority_dict[table[i, 3].value]
            except KeyError:
                critical = priority_dict['No Necesario']

#    print function_name
#    print function_desc
    functionality = { 
        'category' : cat_number,
        'name': function_name,
        'description': function_desc,
        'is_tmpl': True,
        'critical': critical,
    }   

    partner_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'create', functionality)
