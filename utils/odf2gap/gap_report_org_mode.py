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

effort_dict = { '0' : 'Funcionalidad no contemplada',
        '1' : 'Funcionalidad existente en Plone',
        '2' : 'Funcionalidad existente en Plone, pero requiere configuración ya parametrización',
        '3' : 'Funcionalidad no existente en Plone, requiere desarrollo menor a 4 horas',
        '4' : 'Funcionalidad no existente en Plone, requiere desarrollo menor a 8 horas',
        '5' : 'Funcionalidad no existente en Plone, se necesitan mas detalles o requiere de un fuerte desarrollo mayor a 32 horas'
}

efforts_acum = {'0' : 0,
        '1' : 0,
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
    org_header = """#+TITLE:     Análisis de brecha Portal cantv.com.ve
#+AUTHOR:    Carlos Paredes
#+EMAIL:     cparedes@covete.com.ve
#+DATE:      2014-1-16
#+DESCRIPTION: Análisis de brecha Portal cantv.com.ve
#+KEYWORDS:
#+LANGUAGE:  es
#+OPTIONS:   H:3 num:t toc:t:nil @:t ::t |:t ^:t -:t f:t *:t <:t
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

    versiones = """\n* Versiones del Documento
#+BEGIN_DITAA images/versiones_brecha_cantv_com_ve.png -r -S
/-------------------------------------------------+-----------\\
| cBLU                  Autor                     |  Versión  |
+-------------------------------------------------+-----------+
|                 Carlos Paredes                  |     1     |
+-------------------------------------------------+-----------+
|                 Carlos Paredes                  |     2     |
+-------------------------------------------------+-----------+
|                                                 |           |
\-------------------------------------------------+-----------/
#+END_DITAA"""
    print versiones

    gap_info = "\n* "+gap['name']+"\n\n** Funcionalidades:"
    print gap_info.encode('utf-8')

    for f in gap['gap_lines']:
        line = listar_gap_lines(sock, uid, f)
        func = listar_gap_func(sock, uid, line['functionality'][0])

        efforts_acum[line['effort'][1]] += 1

        if (func['description'] != '') and func['description']:
            func_info = "\n*** "+line['category'][1].encode('utf-8')+"\n+ Nombre: "+line['functionality'][1].encode('utf-8')+"\n+ Descripción: "+func['description'].encode('utf-8')+"\n+ Prioridad: "+priority_dict[line['critical']]+"\n+ Esfuerzo: "+effort_dict[line['effort'][1]]+"\n+ Aplicación que cubrirá la funcionalidad: "+line['openerp_fct'][1].encode('utf-8')
        else:
            func_info = "\n*** "+line['category'][1].encode('utf-8')+"\n+ Nombre: "+line['functionality'][1].encode('utf-8')+"\n+ Prioridad: "+priority_dict[line['critical']]+"\n+ Esfuerzo: "+effort_dict[line['effort'][1]]+"\n+ Aplicación que cubrirá la funcionalidad: "+line['openerp_fct'][1].encode('utf-8')

        print func_info

    print "\n* Resultado de Análisis:\n** Funcionalidades:"

    print """\n#+BEGIN_DITAA images/brecha_cantv_com_ve.png -r -S
+-----------------------------------------------+-----------+
|cBLU              Característica               | Cantidad  |"""

    separator = "+-----------------------------------------------+-----------+"
 
    print separator
    print "| Requieren conf y/o parametrización < 1 hora | "+str(efforts_acum['1'])+" |"
    print separator
    print "| Requieren conf y/o parametrización < 2 horas | "+str(efforts_acum['2'])+" |"
    print separator
    print "| Requieren desarrollo < 4 horas | "+str(efforts_acum['3'])+" |"
    print separator
    print "| Requieren desarrollo < 8 horas | "+str(efforts_acum['4'])+" |"
    print separator
    print "| Requieren desarrollo > 32 horas | "+str(efforts_acum['5'])+" |"
    print separator
    print  "| No contempladas | "+str(efforts_acum['0'])+" |"
    print separator
    print "#+END_DITAA"

    print "\n\n#+CAPTION: Análisis de brecha portal cantv.com.ve\n#+NAME: Funcionalidades\n    [[./images/graph_brecha_cantv_com_ve.png]]"
    print "\clearpage"

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

    print """#+BEGIN_DITAA images/gap_plone_features_cantv_com_ve.png -r -S
+-----------------------------------------------+-----------+
|cBLU              Característica               | Cantidad  |"""
    
    separator = "+-----------------------------------------------+-----------+"

    for key in dict_openrp_func.keys():
        print separator
        print "| Plone "+key+" | "+str(dict_openrp_func[key])+" |"

    print separator
    print "#+END_DITAA"

def main():
    (sock, uid) = connect()

    make_report(sock, uid, 'autogestión Requerimientos Funcionales')
    gap_openrp_features(sock, uid, 'autogestión Requerimientos Funcionales')

main()
