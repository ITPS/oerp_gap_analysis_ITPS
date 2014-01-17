# *-* coding=utf-8 *-* 
import xmlrpclib, sys, settings, re, pprint

username = settings.username
pwd = settings.pwd
dbname = settings.dbname

priority_dict = { 4 : 'Mandatorio',
        3 : 'Prioritario',
        2 : 'Deseable',
        1 : 'No Necesario',
}

effort_dict = { '1' : 'Funcionalidad existente en Plone',
        '2' : 'Funcionalidad existente en Plone, pero requiere configuración ya parametrización',
        '3' : 'Funcionalidad no existente en Plone, requiere desarrollo menor a 4 horas',
        '4' : 'Funcionalidad no existente en Plone, requiere desarrollo mayor a 10 horas',
        '5' : 'Funcionalidad no existente en Plone, se necesitan mas detalles o requiere de un fuerte desarrollo mayor a 32 horas'
}

efforts_acum = {'1' : 0,
        '2' : 0,
        '3' : 0,
        '4' : 0,
        '5' : 0,
}

def connect():
    # Get the uid
    sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
    uid = sock_common.login(dbname, username, pwd)

    #replace localhost with the address of the server
    sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
    return sock, uid

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
    return gap

def listar_gap_func(sock, uid, value):
    fields = ['description']
    func = sock.execute(dbname, uid, pwd, 'gap_analysis.functionality', 'read', value, fields)
    return func

def listar_gap_lines(sock, uid, value):
    fields = ['category', 'critical', 'effort', 'functionality', 'openerp_fct']
    line = sock.execute(dbname, uid, pwd, 'gap_analysis.line', 'read', value, fields)
    return line

def make_report(sock, uid, gap_name):
    gap = listar(sock, uid, gap_name)
    org_header = """
#+TITLE:     Análisis de brecha Portal cantv.com.ve
#+AUTHOR:    Carlos Paredes
#+EMAIL:     cparedes@covete.com.ve
#+DATE:      2014-1-16
#+DESCRIPTION: Análisis de brecha Portal cantv.com.ve
#+KEYWORDS:
#+LANGUAGE:  es
#+OPTIONS:   H:3 num:t toc:t \n:nil @:t ::t |:t ^:t -:t f:t *:t <:t
#+OPTIONS:   TeX:t LaTeX:t skip:nil d:nil todo:t pri:nil tags:not-in-toc
#+INFOJS_OPT: view:nil toc:nil ltoc:t mouse:underline buttons:0 path:http://orgmode.org/org-info.js
#+EXPORT_SELECT_TAGS: export
#+EXPORT_EXCLUDE_TAGS: noexport
#+LINK_UP:
#+LINK_HOME:
#+XSLT:
#+LATEX_CLASS: cantv
#+LATEX_CLASS_OPTIONS: [11pt, letterpaper, oneside, spanish]
#+LATEX_HEADER: \usepackage{array}
#+LATEX_HEADER: \input{titulo-brecha-cantv-com-ve}"""
    print org_header

    gap_info = "\n* "+gap['name']+"\n\n** Funcionalidades:"
    print gap_info

    for f in gap['gap_lines']:
        line = listar_gap_lines(sock, uid, f)
        func = listar_gap_func(sock, uid, line['functionality'][0])

        efforts_acum[line['effort'][1]] += 1

        if (func['description'] != '') and func['description']:
            func_info = "\n*** "+line['category'][1].encode('utf-8')+"\n+ Nombre: "+line['functionality'][1].encode('utf-8')+"\n+ Descripción:"+func['description'].encode('utf-8')+"\n+ Prioridad: "+priority_dict[line['critical']]+"\n+ Esfuerzo: "+effort_dict[line['effort'][1]]+"\nAplicación que cubrirá la funcionalidad: "+line['openerp_fct'][1].encode('utf-8')
        else:
            func_info = "\n*** "+line['category'][1].encode('utf-8')+"\n+ Nombre: "+line['functionality'][1].encode('utf-8')+"\n+ Prioridad: "+priority_dict[line['critical']]+"\n+ Esfuerzo: "+effort_dict[line['effort'][1]]+"\nAplicación que cubrirá la funcionalidad: "+line['openerp_fct'][1].encode('utf-8')

        print func_info
    
    effort_info = "\n\n* Resultado de Análisis:\n** Funcionalidades:\n + Funcionalidades disponibles en Plone: "+str(efforts_acum['1'])+"\n + Funcionalidades disponibles en Ploe que requieren configuración y parametrización: "+str(efforts_acum['2'])+"\n + Funcionalidades no disponibles en Plone que requieren desarrollo: "+str(efforts_acum['3']+efforts_acum['4']+efforts_acum['5'])

    effort_info = effort_info + "\n#+CAPTION: Análisis de brecha portal cantv.com.ve\n#+NAME: Funcionalidades\n    [[./images/brecha/graph_brecha_cantv_net.png]]"

    print effort_info

def gap_openrp_features(sock, uid, gap_name):
    gap = listar(sock, uid, gap_name)

    dict_openrp_func = {}
    print "\n** Cantidad de funcionalidades cubiertas por características de Plone\n"

    for f in gap['gap_lines']:
        line = listar_gap_lines(sock, uid, f)

        if line['openerp_fct']:
            try:
                dict_openrp_func[line['openerp_fct'][1].encode('utf-8')] += 1
            except KeyError:
                dict_openrp_func[line['openerp_fct'][1].encode('utf-8')] = 1

    for key in dict_openrp_func.keys():
        print "Plone "+key+" = "+str(dict_openrp_func[key])

def main():
    (sock, uid) = connect()

    make_report(sock, uid, 'Portal cantv.com.ve')
    gap_openrp_features(sock, uid, 'Portal cantv.com.ve')

main()
