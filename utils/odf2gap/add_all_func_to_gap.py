# *-* coding=utf-8 *-* 
import xmlrpclib, sys, settings, re, pprint

username = settings.username
pwd = settings.pwd
dbname = settings.dbname

def connect():
    # Get the uid
    sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
    uid = sock_common.login(dbname, username, pwd)

    #replace localhost with the address of the server
    sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
    return sock, uid

def borrar(sock, uid):
    buscar = []
    cod = sock.execute(dbname, uid, pwd, 'gap_analysis', 'search', buscar)
    for i in cod:
        sock.execute(dbname, uid, pwd, 'gap_analysis', 'unlink', cod)

def actualizar(sock, uid):
    cod = buscar(sock, uid, "all")
    fields = ['name', 'code', 'type', 'user_type']
    for i in cod:
        func = sock.execute(dbname, uid, pwd, 'gap_analysis', 'read', i, fields)

        values = {'filt': 'value', 'filt' : 'value'}
        
        modificar(sock, uid, i, values)

def modificar(sock, uid, ids, values):
    account_id = sock.execute(dbname, uid, pwd, 'gap_analysis', 'write', ids, values)

def buscar(sock, uid, filt):
    if filt == "":
        filt = []
    cod = sock.execute(dbname, uid, pwd, 'gap_analysis', 'search', filt)
    return cod

def listar(sock, uid, value):
    gaps = []
    fields = []
    if value == "":
        filt = []
    else:
        filt = [('name','=', value)]
    cod = buscar(sock, uid, filt)
    for i in cod:
        gap = sock.execute(dbname, uid, pwd, 'gap_analysis', 'read', i, fields)
        gaps.append(gap)
    return gaps

def crear_gap_lines(sock, uid, gap_name):
    line_id = 0
    functionalities = listar_gap_func(sock, uid, '')
    gap = listar(sock, uid, gap_name)

    for f in functionalities:
        line = {
            'category': f['category'][0],
            'code': False,
            'contributors': False,
            'critical': 4,
            'duration_wk': 0.0,
            'effort': f['effort'][0],
            'functionality': f['id'],
            'gap_id': gap[0]['id'],
            'id': line_id,
            'keep': True,
            'openerp_fct': f['openerp_fct'][0],
            'phase': '1',
            'seq': False,
            'testing': f['testing'],
            'to_project': True,
            'total_cost': 0.0,
            'total_time': 0.0,
            'unknown_wk': False,
            'workloads': []
        }

        id_gap_line = sock.execute(dbname, uid, pwd, 'gap_analysis.line', 'create', line)
        line_id += 1

def buscar_gap_lines(sock, uid, filt):
    if filt == "":
        filt = []
    cod = sock.execute(dbname, uid, pwd, 'gap_analysis.line', 'search', filt)
    return cod

def listar_gap_lines(sock, uid, value):
    lines = []
    fields = []
    if value == "":
        filt = []
    else:
        filt = [('gap_id','=', value)]
    cod = buscar_gap_lines(sock, uid, filt)
    for i in cod:
        line = sock.execute(dbname, uid, pwd, 'gap_analysis.line', 'read', i, fields)
        lines.append(line)
    return lines

def mod_gap_lines(sock, uid, ids, values):
    account_id = sock.execute(dbname, uid, pwd, 'gap_analysis.line', 'write', ids, values)

def act_gap_lines(sock, uid, id_gap):
    lines = listar_gap_lines(sock, uid, id_gap)
    for l in lines:
        values = {}
        if re.match('Minisitio.*', l['category'][1]):
            values = {'effort' : 2, 'openerp_fct' : 8, 'testing': 2.0}
            mod_gap_lines(sock, uid, l['id'], values)

def buscar_gap_func(sock, uid, filt):
    if filt == "":
        filt = []
    cod = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'search', filt)
    return cod

def listar_gap_func(sock, uid, value):
    functionalities = []
    fields = []
    if value == "":
        filt = []
    else:
        filt = [('gap_id','=', value)]
    cod = buscar_gap_func(sock, uid, filt)
    for i in cod:
        types = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'read', i, fields)
        functionalities.append(types)
    return functionalities

def main():
    (sock, uid) = connect()

    #listar(sock, uid, 'cantv.com.ve')
    #pprint.pprint(listar_gap_lines(sock, uid, ''), indent=4)
    #listar_gap_func(sock, uid, '')
    crear_gap_lines(sock, uid, "cantv.com.ve")#Inserta todas las funcionalidades al GAP con nombre cantv.com.ve
    #act_gap_lines(sock, uid, '')

main()
