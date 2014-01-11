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
start_row = 2
start_column = 1

global spreadsheet 
global sheets
global table
global rowcount
global current_cell
parent_id = 0

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
    global parent_id
    category_id = 0
    category = re.sub(": |- ", ":", category)
    pieces = category.rsplit(":")
    for i in xrange(0, len(pieces),1):
        parent_id = search_category_on_oerp(pieces[i-1])
        current_category = search_category_on_oerp(pieces[i])
        if not current_category:
            category_id = create_category_on_oerp(pieces[i])
            set_category_parent(category_id, parent_id)
        else:
            fields = ['parent_id']
            if current_category:
                category_on_oerp = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'read', current_category, fields)
                if (category_on_oerp[0]['parent_id']) and (parent_id != category_on_oerp[0]['parent_id'][0]):
                    category_name_match = re.match('.*'+pieces[i-1]+'.*', category_on_oerp[0]['parent_id'][1].encode('utf-8'))
                    if not category_name_match:
                        category_id = create_category_on_oerp(pieces[i])
                        set_category_parent(category_id, parent_id)
                    else:
                        category_id = current_category[-1]
                else:
                    category_id = current_category[-1]

    return category_id

def set_category_parent(category_id, parent_id):
    if parent_id:
        child_category_id = category_id

        values = {'parent_id' : parent_id[-1]}
        category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'write', child_category_id, values)

# this function searches for a category on an OpenERP model
def search_category_on_oerp(category_i_need):
    my_query  = [('name', '=', category_i_need),]
    category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'search', my_query)
    if category_id:
        return category_id
    else:
        return None
    
# this functions creates a category in a gap analysis deta model on OpenERP
def create_category_on_oerp(category):
    cat_name = category

    cat_capitalized = category.capitalize()
    seq = 0
    sub_str = 8

    for i in reversed(range(0,sub_str)):
        try:
            code = cat_capitalized[:sub_str-i].encode('latin-1')
        except UnicodeDecodeError:
            pass

    new_category = {
        'name': cat_name,
        'code': code,
    }

    category_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality.category', 'create', new_category)

    category_dict[cat_name] = category_id

    return category_id

def create_functionalities(category_id, functionality, critical):
    cat_number = category_id

    if functionality.value:
        function_lines = functionality.value.split('\n')
        first_line = None
        second_line = ''
        for line in function_lines:
#            if ":" or "-" in line:
#                line = re.sub(": |- ", ":", line)
#                function_name = line.split(':',1)
#            else:
#                function_name = line.split('\n')
#            for cell in function_name:
#                if not first_line:
#                    first_line = cell
#                else:
#                    second_line += "\n" + cell

            function_name = functionality.value
            function_desc = ""

    functionality_to_oerp = {
        'category' : cat_number,
        'name': function_name,
        'description': function_desc,
        'is_tmpl': True,
        'critical': critical,
    }

    partner_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'create', functionality_to_oerp)

# regular program flow

for i in xrange(start_row, rowcount, 1):
    if table[i, start_column].value:
        category = table[i, start_column].value.encode('utf-8')
        functionality = table[i, start_column + 1]

        try:
            critical = priority_dict[table[i, 3].value]
        except KeyError:
            critical = priority_dict['No Necesario']

        category = re.sub("\s *$", "", category)

        if re.match(".*-.*|.*:.*", category):
            child_category_id = create_parents(category)
        else:
            category_on_oerp = search_category_on_oerp(category)
            if not category_on_oerp:
                child_category_id = create_category_on_oerp(category)

        if functionality.value:
            create_functionalities(child_category_id, functionality, critical)

print len(category_dict)
print "----------"
