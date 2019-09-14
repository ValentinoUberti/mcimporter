# -*- coding: utf-8 -*-
import json
from fasi_per_articolo import FASI_PER_ARTICOLO
def lista_articoli():
    
    links = [lambda row: A(XML('Visualizza lavorazioni'),_class='button btn btn-default',_onclick=XML("lista_lavorazioni('"+row.codice_articolo+"')"))]
    fields = [db.anagrafica_articoli.codice_articolo]
    articoli_form = SQLFORM.grid(db.anagrafica_articoli,formname='articoli1',maxtextlength=100,create=True,        deletable=True,searchable=True,sortable=True,paginate=10, formstyle = 'table3cols',csv=False,user_signature=True,links=links,fields=fields)
    #articoli_form.element('.web2py_counter', replace=None)
    
    """        
    if articoli_form.process().accepted:
        redirect(URL('anagrafica_articoli_2',args=articoli_form.vars.id))
    
    art_form = SQLFORM.grid(db.articoli,formname='articoli',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True)
    
    """
    return locals()
    return dict(articoli_form = articoli_form)


def lista_lavorazioni_per_articolo():
    codice_articolo = request.vars['codice_articolo']
   
    try:
        lavorazioni = db(db.lista_lavorazioni_per_articolo.codice_articolo==codice_articolo).select().first().json_dettaglio
    except:
        lavorazioni=[]
        
    #lavorazioni = json.dumps(lavorazioni)
    print "lavorazioni ",lavorazioni
    return locals()


def lista_lavorazioni_possibili():
    links = [lambda row: A(XML('Inserisci'),_class='button btn btn-default',_onclick=XML("inserisci_lavorazione('"+str(row.id)+"')"))]
    fields = [db.lavorazioni.nome]
    form = SQLFORM.grid(db.lavorazioni,create=True, deletable=True,searchable=True,sortable=True,paginate=10, formstyle = 'table3cols',csv=False,fields=fields,links=links)
    return locals()
    
    
@service.jsonrpc
@service.jsonrpc2    
def return_lavorazione_name_from_id(args):
    id_lavorazione=args
    print id_lavorazione
    try:
        nome_lavorazione=db(db.lavorazioni.id==id_lavorazione).select().first().nome
    except:
        nome_lavorazione="Error"
    
    return nome_lavorazione
  
@service.jsonrpc
@service.jsonrpc2    
def stampa_lavorazioni_per_ordine_e_articolo(id_ordine,codice_articolo,riga):
    
   
    row_dettaglio_ordine=db(db.ordine_cliente.id==id_ordine).select().first()
    row_lavorazioni = db(db.lista_lavorazioni_per_articolo.codice_articolo==codice_articolo).select().first()
    row_articolo = db(db.anagrafica_articoli.codice_articolo==codice_articolo).select().first()
    row_dettaglio_righe_in_ordine=db((db.righe_in_ordine_cliente.id_ordine_cliente == id_ordine) & (db.righe_in_ordine_cliente.n_riga == riga) & (db.righe_in_ordine_cliente.codice_articolo == codice_articolo)).select().first()
    
    
    #print row_articolo,row_dettaglio_righe_in_ordine
    #print row_dettaglio_ordine
    #print row_lavorazioni
    descrizione_articolo=row_articolo.descrizione
    revisione=row_articolo.revisione
    
    quantita=row_dettaglio_righe_in_ordine.quantita
    evasione=row_dettaglio_righe_in_ordine.evasione.strftime("%d/%m/%Y")
    
    nome_cliente=row_dettaglio_ordine.nome_cliente
    codice_ordine_interno=row_dettaglio_ordine.ultimo_codice_ordine
    riferimento_ordine=row_dettaglio_ordine.riferimento_ordine_cliente
    
    
    print "ID RIGA : ",row_dettaglio_righe_in_ordine.id
    
    
    p = FASI_PER_ARTICOLO(nome_cliente,codice_ordine_interno,riferimento_ordine,evasione,codice_articolo,descrizione_articolo,revisione,quantita)
    p.footer(str(row_dettaglio_righe_in_ordine.id))
    
    json_lavorazioni=row_lavorazioni.json_dettaglio
    j = json.loads(json_lavorazioni)
    
    
    
    
    #for x in range(9):
    #    p.add_row("AAAAAA"+str(x),"BBBBBB"+str(x),"HHHH"+str(x),"CCCC"+str(x),"DD"+str(x),"EE"+str(x),"FF56"+str(x),"GG"+str(x))
    
    
    
    for data_json in j:
        try:
            tempoattrezzagio = data_json['tempoattrezzagio']
            descrizione_lavorazione = data_json['descrizione_lavorazione']
            tempolavorazionesenzaattrezzaggio = data_json['tempolavorazionesenzaattrezzaggio']
            commento = data_json['commento']
            posizione = data_json['posizione']
            id_lavorazione = data_json['id_lavorazione']
            
            nome_operazione="op"
            pezzi_prodotti=""
            barcode=str(id_ordine)+"-"+str(riga)+"-"+str(posizione)
            try:
                controlli=db(db.lavorazioni.id==id_lavorazione).select().first().controllo
            except :
                controlli=""
            
            print controlli
            
            p.add_row(descrizione_lavorazione,nome_operazione,controlli,tempoattrezzagio,tempolavorazionesenzaattrezzaggio,pezzi_prodotti,commento,barcode)
            
            print data_json
        except Exception,e:
            print e
            
    """
    add_row(self,nome_macchina,nome_operazione,controlli,tempo_attrezzaggio,tempo_produzione,pezzi_prodotti,note,barcode):
    """
    nomefile=id_ordine+"-"+codice_articolo.replace("/","")+"-"+riga+".pdf"
    p.insert_rows()
    p.add_columns()
    p.create_pdf(nomefile)
    
    
    return nomefile
@service.jsonrpc
@service.jsonrpc2    
def save_lavorazioni_per_articolo(codice_articolo,json_lavorazioni): 
    
    print json_lavorazioni
    db(db.lista_lavorazioni_per_articolo.codice_articolo==codice_articolo).delete()
    db.lista_lavorazioni_per_articolo.insert(codice_articolo=codice_articolo,json_dettaglio=json_lavorazioni)
    
    
    
    response.flash="ok"
    #return response
 
def controlla_esistenza_fase_da_codice_articolo(id_ordine,codice_articolo,n_riga):
    
    #id_ordine=db(db.righe_in_ordine_cliente.id==id_riga_ordine).select().first().id_ordine_cliente
    
    id_ordine=id_ordine.strip()
    row = db(db.lista_lavorazioni_per_articolo.codice_articolo==codice_articolo).select()
    if len(row)>0:
        return A(XML('Stampa fasi'),_class='button btn btn-success',_onclick=XML('stampa_fasi_da_articolo(\''+id_ordine+'\',\''+codice_articolo+'\',\''+n_riga+'\')'))
    
    
    return A(XML('Crea fasi'),_class='button btn btn-danger',_onclick=XML('crea_fasi_per_articolo(\''+codice_articolo+'\')'))
    
def lista_articoli_da_codice_ordine():
    id_ordine_cliente = request.vars['id_ordine_cliente']
    
    row=db(db.ordine_cliente.id==id_ordine_cliente).select().first()
    print row
    
    db.righe_in_ordine_cliente.fase_esistente=Field.Virtual("Fasi esistenti",lambda row: controlla_esistenza_fase_da_codice_articolo(row.righe_in_ordine_cliente.id_ordine_cliente,row.righe_in_ordine_cliente.codice_articolo,row.righe_in_ordine_cliente.n_riga))
    
    db.righe_in_ordine_cliente.id_ordine_cliente.writable=False
    db.righe_in_ordine_cliente.id_ordine_cliente.readble=False
    
    fields=[db.righe_in_ordine_cliente.id_ordine_cliente,db.righe_in_ordine_cliente.n_riga,db.righe_in_ordine_cliente.codice_articolo,db.righe_in_ordine_cliente.quantita,db.righe_in_ordine_cliente.evasione,db.righe_in_ordine_cliente.fase_esistente]
    
    
    righe_in_ordine_cliente_form = SQLFORM.grid((db.righe_in_ordine_cliente.id_ordine_cliente == id_ordine_cliente) & (db.righe_in_ordine_cliente.codice_articolo !="commento"),formname='aggiungi_righe_a_ordini_clienti',maxtextlength=100,create=False,     deletable=False,searchable=True,sortable=True,paginate=8, formstyle = 'table3cols',csv=False,fields=fields)
    
    
    return locals()
   
def stampa_fasi_articoli_da_ordine():
    db.ordine_cliente.ultimo_codice_ordine.writable=False
    
    
    
    fields=[db.ordine_cliente.ultimo_codice_ordine,db.ordine_cliente.nome_cliente,db.ordine_cliente.data_inserimento,db.ordine_cliente.riferimento_ordine_cliente]
    #fields=['ultimo_codice_ordine','nome_cliente','data_inserimento','listino','riferimento_ordine_cliente','data_ordine_cliente','magazzino_interno','pagamento']
    links = [lambda row: A(XML('Articoli'),_class='button btn btn-default',_onclick=XML("lista_articoli_da_codice_ordine('"+str(row.id)+"')"))]
    ordini_clienti_form = SQLFORM.grid(db.ordine_cliente.ddt_completato==False,formname='ordini_clienti',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=10, formstyle = 'table3cols',csv=False,fields=fields,links=links)
     
    return locals()

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()