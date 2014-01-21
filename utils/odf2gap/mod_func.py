# *-* coding=utf-8 *-* 
import xmlrpclib, sys, settings, re, pprint

username = settings.username
pwd = settings.pwd
dbname1 = settings.dbname
dbname2 = "cantv.com.ve"

def connect(username, pwd, dbname):
    # Get the uid
    sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
    uid = sock_common.login(dbname2, username, pwd)

    #replace localhost with the address of the server
    sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
    return sock, uid

def mod_func(sock, uid, dbname, ids, values):
    account_id = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'write', ids, values)

def act_func(sock, sock2, uid, uid2, id_gap):
    functionalities = listar_gap_func(sock, uid, dbname1, id_gap)
    openerp_fcts = get_openerp_fct(sock, uid, dbname1, '')
    i = 0
    for functionality in functionalities:
        values = {}
        functionalities_another = listar_gap_func(sock2, uid2, dbname2, functionality['name'])
        if functionalities_another:
            for functionality_another in functionalities_another:
                if functionality_another['critical'] < functionality['critical']:
                    critical = functionality['critical']
                else:
                    critical = functionality_another['critical']

                for fct in openerp_fcts:
                    if re.match(functionality_another['openerp_fct'][1], fct["name"]):
                        id_effort = get_openerp_efforts(sock, uid, dbname1, functionality_another['effort'][1])
                        values = {
                            'critical': critical,
                            'duration_wk': functionality_another['duration_wk'],
                            'effort': id_effort[0],
                            'openerp_fct': fct["id"],
                            'testing': functionality_another['testing'],
                        }

                        mod_func(sock, uid, dbname1, functionality['id'], values)
                        i += 1
    print i

def extra(sock, uid, id_gap):
    functionalities = listar_gap_func(sock, uid, dbname1, id_gap)
    id_effort = get_openerp_efforts(sock, uid, dbname1, '0')
    i = 0
    for functionality in functionalities:
        values = {}
        if (functionality['openerp_fct']) and ((functionality['openerp_fct'][1] == 'No Contemplado en Arquitectura de Servicios Propuesta') or (functionality['openerp_fct'][1] == "No Contemplado en Contrato de Servicios")):
            values = {
                'effort': id_effort[0],
            }

            mod_func(sock, uid, dbname1, functionality['id'], values)
            i += 1
    print i

def buscar_gap_func(sock, uid, dbname, filt):
    if filt == "":
        filt = []
    cod = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'search', filt)
    return cod

def listar_gap_func(sock, uid, dbname, value):
    functionalities = []
    fields = []
    if value == "":
        filt = []
    else:
        filt = [('name','=', value)]
    cod = buscar_gap_func(sock, uid, dbname, filt)
    for i in cod:
        types = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'read', i, fields)
        functionalities.append(types)
    return functionalities

def get_openerp_fct(sock, uid, dbname, filt):
    openerp_fcts = []
    if filt == "":
        filt = []
    cod_openerp_fct = sock.execute(dbname1, uid, pwd, 'gap_analysis.openerp', 'search', filt)
    for cod in cod_openerp_fct:
        openerp_fct = sock.execute(dbname1, uid, pwd, 'gap_analysis.openerp', 'read', cod, [])
        openerp_fcts.append(openerp_fct)
    return openerp_fcts

def get_openerp_efforts(sock, uid, dbname, value):
    id_effort = sock.execute(dbname1, uid, pwd, 'gap_analysis.effort', 'search', [('name', '=', value)])
    return id_effort

def main():
    (sock, uid) = connect(username, pwd, dbname1)
    (sock2, uid2) = connect(username, pwd, dbname2)
    act_func(sock, sock2, uid, uid2, '')
    extra(sock, uid, '')

main()
