 # coding=UTF-8
import xmlrpclib
import ezodf2


username = 'admin' #the user
pwd = '123321...'      #the password of the user
dbname = 'gap-analysis-eng'    #the database

category_dict = { 'General': 2,
                  'Home page': 3,
                  'Pie de página global': 4,
                  'Misceláneos Home': 5,
                  'Elementos obligatorios': 6,
                  'Estructura base Cantv.net': 7,
                  'Estructura base Cantv.net: Canales': 8,
                  'Estructura base Cantv.net: Servicios': 9,
                  'Estructura de Menús': 10,
                  'Home Page Invitado': 11,
                  'Aplicaciones para el portal de cara al usuario': 12,
                  'Aplicaciones para gestión de contenidos de Cantv.net': 13,
                  'Contenidos': 14,
                  'Búsqueda': 15,
                  'Publicaciones recientes': 16,
                  'Móvil': 17,
}

# Get the uid
sock_common = xmlrpclib.ServerProxy ('http://192.168.213.161:8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
print uid 

#replace localhost with the address of the server
sock = xmlrpclib.ServerProxy('http://192.168.213.161:8069/xmlrpc/object')                                                                                   
print sock



file_path = "/home/cmaldonado/Downloads/"
filename = "RequerimientosFuncionales_cantv.net.ods"
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
