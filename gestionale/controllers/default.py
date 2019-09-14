# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from __future__ import division
import json
import csv

import datetime
from calendar import monthrange
import gluon
from datetime import timedelta
import wrapper
import subprocess
import os

import socket
import sys

from imports.writeToXlsx import WriteToXlsx
from imports.yamlImporter import YamlImporter
from imports.attendanceImporter import AttendanceImporter
import calendar
import locale
from datetime import datetime
from calendar import monthrange


def ore_dipendenti():
    return locals()


def upload_csv():

    def fixHours(h):

       decimal=h % 1
       number=int(h)
       print("Decimal = ",number,decimal)
       if decimal >= 0.41 and decimal <0.88:
           decimal=0.50
           number=float(number) + decimal
       elif decimal > 0.88:
           decimal=0.00
           number=float(number+1)
       else:
         number=float(number)

       #if number==decimal==0:
       #    number=0

       return number

    def fixHoursAndRest(h):
    
       decimal=h % 1
       number=8 - int(h)
       print("Decimal = ",number,decimal)
       if decimal >= 0.41 and decimal <0.88:
           decimal=0.50
           number=float(number) + decimal
       elif decimal > 0.88:
           decimal=0.00
           number=float(number+1)
       else:
         number=float(number)

       #if number==decimal==0:
       #    number=0

       return number

    def fixHoursAndRestFriday(h):
        
       decimal=h % 1
       number=int(h) -7
       print("Decimal Friday  = ",number,decimal)
       if decimal >= 0.41 and decimal <0.88:
           decimal=0.50
           number=float(number) + decimal
       elif decimal > 0.88:
           decimal=0.00
           number=float(number+1)
       else:
         number=float(number)

       #if number==decimal==0:
       #    number=0

       return number

    all=[]
    # Save the uploaded file
    xlsx=request.vars['csvfile[]'].value
    outFileName=filepath = os.path.join(request.folder, 'uploads', "hours_uploaded.xlsx")
    outFile=open(outFileName,"w")
    outFile.write(xlsx)
    outFile.close()

    pamaster_path=os.path.join(request.folder, 'static/timbratore', "pamaster.xlsm")
    workers_path=os.path.join(request.folder, 'static/timbratore', "workers.yaml")

    
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8') # Italian on windows
    yamlData = YamlImporter(workers_path)
    data = yamlData.importYaml()

    attendance=AttendanceImporter(outFileName)
    attendance.loadData()
    #attendance.orderData()

    

    monthNumber=attendance.finalOrderedActions.days[32]
    monthName=calendar.month_name[monthNumber].title()
    year=datetime.now().year
    downloadFileName="timbrature-"+monthName+"-"+str(year)+".xlsx"
    saved_path=os.path.join(request.folder, 'static/timbratore', downloadFileName)

    XLSM = WriteToXlsx(pamaster_path, saved_path)
    rowsMonth=[1,38,75,112,149]
    for i in rowsMonth:
        XLSM.write(i,45,monthName)

    #Fix day name
    for row in data:
        startingRow=int(row.startingRow) -2
        num_days = monthrange(year, monthNumber)[1]
        for day in range(1,num_days+1):
              currentDate=datetime.strptime("{0}/{1}/{2}".format(day,monthNumber,year),"%d/%m/%Y")
              dayName=currentDate.strftime("%A")[:3]
             
              XLSM.write(int(startingRow),(day*2)-1+4,dayName.upper())
            

    for day in attendance.finalOrderedActions.days:
        if day < 32:
          for worker in attendance.finalOrderedActions.days[day]:
              hours=attendance.finalOrderedActions.days[day][worker]
              print("Day {}, Worker {}, Hour {}".format(day,worker,hours))
              startingRow=yamlData.returnStartingRow(worker)
              currentDate=datetime.strptime("{0}/{1}/{2}".format(day,monthNumber,year),"%d/%m/%Y")
              dayOfTheWeek=currentDate.weekday()
              
              if dayOfTheWeek ==4: #Friday
                  if hours > 6.9:
                      XLSM.write(int(startingRow),(day*2)-1+5,7)
                      
                      XLSM.write(int(startingRow)+1,(day*2)-1+5,fixHoursAndRestFriday(hours))
                      XLSM.write(int(startingRow)+1,(day*2)-2+5,"S1")
                      XLSM.write(int(startingRow)+2,(day*2)-1+5,1)
                      XLSM.write(int(startingRow)+2,(day*2)-2+5,"ROL")
                  else:
                      if hours>0:
                         XLSM.write(int(startingRow),(day*2)-1+5,fixHours(hours))
                         XLSM.write(int(startingRow)+2,(day*2)-1+5,fixHoursAndRest(hours)-1)
                         XLSM.write(int(startingRow)+2,(day*2)-2+5,"ROL")

              else:
                  if hours > 7.9:
                    
                     XLSM.write(int(startingRow),(day*2)-1+5,8)
                     if fixHours(hours) - 8 >0:
                         XLSM.write(int(startingRow)+1,(day*2)-2+5,"S1")
                         XLSM.write(int(startingRow)+1,(day*2)-1+5,fixHours(hours) -8 )

                  else:
                      if hours>0:
                         XLSM.write(int(startingRow),(day*2)-1+5,fixHours(hours))

                     


    XLSM.save()

    all.append(URL('static/timbratore',downloadFileName))

    return response.json(all)



  



@service.jsonrpc
@service.jsonrpc2
def stampa_rcp(args):
    
    id_riga_in_produzione=args['0']
    row = db(db.articoli_in_produzione.id == id_riga_in_produzione).select().first()
    
    scadenza=datetime.datetime.strptime(str(row.data_consegna),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
    cliente=row.cliente
    riferimento_ordine=row.riferimento_ordine
    codice_ordine=row.codice_ordine
    codice_articolo=row.codice_articolo
    descrizione=row.descrizione
    saldo=row.qta_saldo
    id_riga=row.id_riga
    
    dettaglio_ordine = db(db.ordine_cliente.ultimo_codice_ordine==codice_ordine).select().first()
    
    # print dettaglio_ordine
    try:
        ente=dettaglio_ordine.ente
        if ente is None:
            ente="Nessuno"
    except:
        ente="Nessuno"

    # print "Ente : ",ente
    try:
        revisione = str(db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().revisione)
        # print "revisione = "+ revisione
    except Exception,e:
    	# print e.message
        pass
    
    
    dettagli=db(db.anagrafica_articoli.codice_articolo==codice_articolo).select().first()
    giacenza=dettagli.giacenza
    ubicazione=dettagli.ubicazione
    cartella=dettagli.cartella_disegno
    peso=dettagli.peso
    if peso is None:
        peso=""

    p = CONTROLLO_PRODUZIONE("Microcarp S.r.l.","Registro dei Controlli in Produzione")
    p.intestazione(cliente,riferimento_ordine, codice_articolo,scadenza,revisione, saldo,giacenza,ubicazione,cartella,peso)
       
    p.footer(str(id_riga),ente)
   
   
    lavorazioni=db(db.lavorazioni).select()
    
    for lavorazione in lavorazioni:
       
        p.add_row(lavorazione.nome,lavorazione.controllo)
    
    p.insert_rows()
    p.create_pdf()
    

@service.jsonrpc
@service.jsonrpc2
def crea_fattura(args):
    
    
    id_cliente=args['0']
    # print "ID CLIENTE : ",id_cliente
    
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    
    """
    Dati cliente
    """
    
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    iban_cliente = dati_cliente.codice_iban
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    
    scritta_esenzione_cliente = dati_cliente.descrizione_esenzione_iva
    annotazioni=dati_cliente.annotazioni
    


    
    
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    for r in ddts_id:
        data_scelta = r.data_emissione
        
    m = datetime.datetime.strptime(data_scelta,"%d/%m/%Y").date()
    # print "MESE : "+str(m.month)
    
    day_start,day_end = monthrange(m.year, m.month)
    d = str(day_end)+"/"+str(m.month)+"/"+str(m.year)
    
    start_date = datetime.datetime.strptime(d,"%d/%m/%Y")
    
    
    fattura = FATTURA("FATTURA DIFFERITA",start_date.strftime("%d/%m/%Y"),numero_fattura_da_salvare)
    fattura.intestazione(nome_cliente,citta_cliente,indirizzo_cliente,cap_cliente,provincia_cliente,nazione_cliente,cf_cliente,pi_cliente)
    
    
    try:
        fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),"PAGAMENTO","SCADENZA")
    
    except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica"
                  return locals()
    
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []
    
    scritta_esenzione = False
    
    for ddt_id in ddts_id:
        
        
        lista_ddt.append(ddt_id.ddt_id)
        
        riferimento_ddt = "Rif. DDT : " + ddt_id.numero_ddt + " del " + ddt_id.data_emissione
        fattura.add_row("",riferimento_ddt,"","","","","","","")
        
        rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt_id.ddt_id).select()
        # print "DDT ID : ",ddt_id.ddt_id
        
        for row in rows:
            """
            <Row {'n_riga': '3', 'prezzo': '8.9919', 'saved_ddt_id': '21', 'quantita': '11', 'evasione': datetime.datetime(2017, 1, 31, 8, 56), 'id': 10L, 'codice_articolo': '892069925', 'codice_iva': 'Iva 22%', 'descrizione': 'FLANGIA', 'sconti': None, 'u_m': 'Nr', 'user_id': '1', 'codice_ordine': '1/17', 'id_ordine': '26', 'riferimento_ordine': 'fdsfsdf'}>

            """
            
            """
            La riga del ddt contiene i dati relativi all'ordine (id_ordine)
            siccome il pagamento può essere modificato bisogna risalire all'ordine
            poi al tipo di pagamento, poi ai giorni e calcolare la data
            """
            if not "commento" in row.codice_articolo:
                id_ordine = row.id_ordine
                try:
                      try:
                          pagamento = db(db.ordine_cliente.id == id_ordine).select().first()["pagamento"]
                          # print "pagamento = ",pagamento
                      except:
                          pagamento = None
                          
                      if pagamento is None:
                            pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                       
                      if "F.M." in pagamento:
                          fine_mese = True
                      else:
                          fine_mese = False
                          
                       
                      
                        
                      
                      
                      if not fine_mese:
                           try:
                              giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                          
                              if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                                	   	
                              scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                              scadenza_salvata = scadenza
                              scadenza = scadenza.strftime("%d/%m/%Y")
                           except:
                               response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                               return locals()
                      else:
                          
                           if ("M.S." or "ms") in pagamento:
                               
                               giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                               giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                               
                               if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                               
                               scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                               day_start,day_end = monthrange(scadenza.year, scadenza.month)
                               scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                               scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                               scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                               scadenza = scadenza.strftime("%d/%m/%Y") 
                               
                           else:
                               # Fine mese senza M.S.               
                               giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                               if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                               scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                               day_start,day_end = monthrange(scadenza.year, scadenza.month)
                               scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           
                          
                          
                           pass
                      
                      
                      fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(iban_cliente),pagamento,str(scadenza))
                except Exception,e:
                      # print e
                      response.flash="Controllare il tipo di pagamento in anagrafica"
                      return locals()
                
                # print "Aggiunta rig"
                sconti = row.sconti
                if row.sconti is None:
                    
                    sconti=""
                    
                try:
                    if row.prezzo == "0":
                        row.prezzo = ""
                    f = float(row.prezzo)
                    # print "SONO QUI : PREZZO = ".format(f)
                except:
                    msg = "Prezzo non presente " + riferimento_ddt + " Cod.Art : " + row.codice_articolo
                    response.flash=msg
                    return locals()
                try:
                	f=float(row.quantita)
                except:
                	msg = "Quantità non valida Cod.Art : " + row.codice_articolo + " Qta : " +row.qta
                	response.flash=msg
                	return locals()
                	pass
                
                importo = saved_importo = float(row.quantita) * float(row.prezzo)
                importo = Money(str(importo),"EUR")
                importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                prezzo = str(row.prezzo).replace(".",",")
                
                codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                
                # print "VALLLLE " + row.codice_iva
                
                descrizione_codice_iva = db(db.righe_in_ordine_cliente.id == row.id_riga_ordine, db.righe_in_ordine_cliente.n_riga==row.n_riga).select().first()["codice_iva"]
                codice_iva=db(db.anagrafica_codici_iva.descrizione_codice_iva == descrizione_codice_iva).select().first()["codice_iva"]
                
                
                row.codice_iva=codice_iva
                
                
                if "Esenzione" in descrizione_codice_iva:
                    scritta_esenzione = True
                
                percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == descrizione_codice_iva).select().first()["percentuale_iva"]
                
                importo_totale +=saved_importo
                imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                
                if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = saved_importo
                else:
                    lista_codici_iva[codice_iva] += saved_importo
            
            
            else:
            	"""
            	Passo il commento ma resetto tutti i campi
            	"""
            	row.riferimento_ordine=""
            	row.u_m=""
            	row.quantita=""
            	prezzo=""
            	sconti=""
            	importo=""
            	codice_iva=""
            	row.codice_articolo=""
            	# row.descrizione=row.commento
            	
            
            
                
            fattura.add_row(row.codice_articolo,row.descrizione,row.riferimento_ordine,row.u_m,row.quantita,prezzo,sconti,importo,codice_iva)
            
            
            
            
            r = db(db.ddt_cliente.id == ddt_id.ddt_id).select().first()
            r.update_record(fattura_emessa = "T")
    
    # print lista_codici_iva
    
    
   
    bollo= dati_cliente.bollo
  
    if bollo:
        print "SONO NEL BOLLO"
        codice_articolo="BOLLO"
        descrizione="art. 15 DPR 633/72"
        riferimento_ordine=""
        quantita="1"
        prezzo="2,00"
        sconti=""
        codice_iva="53"
        u_m="Nr"
        importo="2,00"
           

        fattura.add_row(codice_articolo,descrizione,riferimento_ordine,u_m,quantita,prezzo,sconti,importo,codice_iva)
        if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = 2
        else:
                    lista_codici_iva[codice_iva] +=2
        
            
    if scritta_esenzione:
        fattura.add_row("","","","","","","","","")
        fattura.add_row("","","","","","","","","")
        
        scritte = scritta_esenzione_cliente.split(",")
        
        for scritta in scritte:
            fattura.add_row("",scritta,"","","","","","","") 
    
    bollo_presente = False
   
    for k,v in lista_codici_iva.iteritems():
        codice_iva = k
        importo_netto = v
        # print "LISTA CODICI : ",codice_iva,importo_netto
        dettaglio_iva = db(db.anagrafica_codici_iva.codice_iva == codice_iva).select().first()
        percentuale_iva = dettaglio_iva.percentuale_iva
        descrizione_iva = dettaglio_iva.descrizione_codice_iva
        imposta_iva = return_imposta(v,percentuale_iva)
        if dettaglio_iva.bollo_su_importi_esenti is True:
            if not bollo_presente:
                bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
                bollo_presente = True
                
        fattura.footer_2(codice_iva,"",return_currency(importo_netto),descrizione_iva,return_currency(imposta_iva),"")
        
                
                
    if bollo:
        _bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
        importo_totale += float(_bollo)    
     
   
     
    importo_totale_da_salvare = importo_totale +imposta_iva
    
    if not "/" in pagamento:
              
     	importo_totale = Money(str(importo_totale),"EUR")
      	importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
     	fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
      	fattura.totale(str(ritorna_prezzo_europeo(importo_totale_da_salvare)))
    
     	scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
      	if "r.b." in pagamento.lower() or "riba" in pagamento.lower():
          riba=True
        else:
          riba=False
        db.fatture_salvate.insert(scadenza=scadenza,nome_cliente=nome_cliente,data_fattura = start_date,numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = importo_totale_da_salvare,richiede_riba=riba,riba_emessa=False,user_id=auth.user_id)     
    
    else:
    	# Devo mettere due fatture con il pagamento e scadenza corretti
    	
    	
    	
    	first_half = round(importo_totale_da_salvare / 2,2)
        second_half= importo_totale_da_salvare - first_half
        
        s=pagamento
        
        st = int(s[s.index("/")+1:s.index("/")+4]) - int(s[s.index("/")-3:s.index("/")])
        second_date = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
        first_date = second_date - datetime.timedelta(days = int(st) +1)
        
        if "F.M" in pagamento:
        	      pass
        	      first_date = first_date.strftime("%d/%m/%Y")
                  # day_start,day_end = monthrange(first_date.year, first_date.month)
                  # first_date = str(day_end)+"/"+str(first_date.month)+"/"+str(first_date.year)
              
        else:
                  first_date = first_date.strftime("%d/%m/%Y")
                  
        second_date = second_date.strftime("%d/%m/%Y")
    	
    	if "r.b." in pagamento.lower() or "riba" in pagamento.lower():
          riba=True
        else:
          riba=False
          
        first_date = datetime.datetime.strptime(first_date,"%d/%m/%Y")
        second_date = datetime.datetime.strptime(second_date,"%d/%m/%Y")
        
        
        importo_totale = Money(str(importo_totale),"EUR")
      	importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
     	fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
      	fattura.totale(str(ritorna_prezzo_europeo(importo_totale_da_salvare)))
        
        db.fatture_salvate.insert(scadenza=first_date,nome_cliente=nome_cliente,data_fattura = start_date,numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = first_half,richiede_riba=riba,riba_emessa=False,user_id=auth.user_id)
        db.fatture_salvate.insert(scadenza=second_date,nome_cliente=nome_cliente,data_fattura = start_date,numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = second_half,richiede_riba=riba,riba_emessa=False,user_id=auth.user_id)
        
    	
    
    
    # print "SCADENZA {0}".format(scadenza)    
        
    
   
    
    """
    fattura.foote,Field('nome_cliente')sr("Totale merce","Sconto","Netto merce","spese varie","spese_trasporto","totale_imponibile","Totale imposta")
    fattura.footer_2("CodIva","Spese accessorie","Imponibile","Iva","Imposta","Bolli")
    fattura.footer_2("CodIva2","Spese accessorie2","Imponibile2","Iva2","Imposta2","Bolli2")
    fattura.totale("14567645")
    """
    
    fattura.add_row("","","","","","","","","")
    fattura.add_row("",annotazioni,"","","","","","","")
    
    fattura.insert_rows()
    fattura.create_pdf()
    
    db(db.fattura).delete()
    db.fattura.insert(numero_fattura = numero_fattura_da_salvare)
    db(db.ddt_da_fatturare.user_id == auth.user_id).delete()
   
def return_scadenza(fattura_id):
    ddts = db(db.fatture_salvate.id == fattura_id).select().first()["id_ddt"]
    ddts_list = eval(ddts)
    scadenza=""
    start_date = datetime.datetime.strptime("28/02/2017","%d/%m/%Y")
    for ddt in ddts_list:
        
        rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id ==ddt).select()
        # print "DDT ID : ",ddt
        
        for row in rows:
            """
            <Row {'n_riga': '3', 'prezzo': '8.9919', 'saved_ddt_id': '21', 'quantita': '11', 'evasione': datetime.datetime(2017, 1, 31, 8, 56), 'id': 10L, 'codice_articolo': '892069925', 'codice_iva': 'Iva 22%', 'descrizione': 'FLANGIA', 'sconti': None, 'u_m': 'Nr', 'user_id': '1', 'codice_ordine': '1/17', 'id_ordine': '26', 'riferimento_ordine': 'fdsfsdf'}>

            """
            
            """
            La riga del ddt contiene i dati relativi all'ordine (id_ordine)
            siccome il pagamento può essere modificato bisogna risalire all'ordine
            poi al tipo di pagamento, poi ai giorni e calcolare la data
            """
            
            id_ordine = row.id_ordine
            try:
                  try:
                      pagamento = db(db.ordine_cliente.id == id_ordine).select().first()["pagamento"]
                      # print "pagamento = ",pagamento
                  except:
                      pagamento = None
                      
                  if pagamento is None:
                        pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                   
                  if "F.M." in pagamento:
                      fine_mese = True
                  else:
                      fine_mese = False
                      
                   
                  
                    
                  
                  
                  if not fine_mese:
                       try:
                          giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                      
                      
                          scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                          scadenza_salvata = scadenza
                          scadenza = scadenza.strftime("%d/%m/%Y")
                       except:
                           response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                           return locals()
                  else:
                      
                       if "M.S." in pagamento:
                           
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                           scadenza = scadenza.date() + datetime.timedelta(days = 10)
                           scadenza = scadenza.strftime("%d/%m/%Y") 
                           
                       else:
                                          
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                       
                      
                      
            except Exception,e:
                 # print e
                 pass          
        
        
    
    
    return scadenza

@service.jsonrpc
@service.jsonrpc2
def crea_fattura_preview(args):
    
    
    id_cliente=args['0']
    # print "ID CLIENTE : ",id_cliente
    
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    
    # print "qui"
    
    """
    Dati cliente
    """
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    iban_cliente = dati_cliente.codice_iban
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    scritta_esenzione_cliente = dati_cliente.descrizione_esenzione_iva
    
    annotazioni=dati_cliente.annotazioni
    
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    for r in ddts_id:
        data_scelta = r.data_emissione
        
    m = datetime.datetime.strptime(data_scelta,"%d/%m/%Y").date()
    # print "MESE : "+str(m.month)
    
    day_start,day_end = monthrange(m.year, m.month)
    d = str(day_end)+"/"+str(m.month)+"/"+str(m.year)
    
    start_date = datetime.datetime.strptime(d,"%d/%m/%Y")
    print "-- DATE CHECK --"
    print start_date
    
    
    
    fattura = FATTURA("FATTURA DIFFERITA",start_date.strftime("%d/%m/%Y"),numero_fattura_da_salvare,anteprima=True)
    fattura.intestazione(nome_cliente,citta_cliente,indirizzo_cliente,cap_cliente,provincia_cliente,nazione_cliente,cf_cliente,pi_cliente)
    
    
    
    try:
        # print "IBAN : ",iban_cliente
        fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(iban_cliente),"PAGAMENTO","SCADENZA")
    
    except:
                  response.flash="Controllare il tipo di pagamento in anagrafica"
                  return locals()
    
    
    
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []
    
    for ddt_id in ddts_id:
        
        
        lista_ddt.append(ddt_id.ddt_id)
        
        riferimento_ddt = "Rif. DDT : " + ddt_id.numero_ddt + " del " + ddt_id.data_emissione
        
        fattura.add_row("",riferimento_ddt,"","","","","","","")
        print ddt_id
        rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt_id.ddt_id).select()
        print "PAst creation ---##"
        # print "DDT ID : ",ddt_id.ddt_id
       
        scritta_esenzione = False
        
        for row in rows:
            print row
            """
            <Row {'n_riga': '3', 'prezzo': '8.9919', 'saved_ddt_id': '21', 'quantita': '11', 'evasione': datetime.datetime(2017, 1, 31, 8, 56), 'id': 10L, 'codice_articolo': '892069925', 'codice_iva': 'Iva 22%', 'descrizione': 'FLANGIA', 'sconti': None, 'u_m': 'Nr', 'user_id': '1', 'codice_ordine': '1/17', 'id_ordine': '26', 'riferimento_ordine': 'fdsfsdf'}>

            """
            
            """
            La riga del ddt contiene i dati relativi all'ordine (id_ordine)
            siccome il pagamento può essere modificato bisogna risalire all'ordine
            poi al tipo di pagamento, poi ai giorni e calcolare la data
            """
            if not "commento" in row.codice_articolo:
                id_ordine = row.id_ordine
                try:
                      
                      try:
                          pagamento = db(db.ordine_cliente.id == id_ordine).select().first()["pagamento"]
                          # print "pagamento = ",pagamento
                      except:
                          pagamento = None
                      
                      
                      
                      if pagamento is None:
                            pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                       
                      if "F.M." in pagamento:
                          fine_mese = True
                      else:
                          fine_mese = False
                          
                       
                      
                        
                    
                     
                      if not fine_mese:
                          
                          try:
                              giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                              
                              if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                          
                              scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                              scadenza_salvata = scadenza
                              scadenza = scadenza.strftime("%d/%m/%Y")
                          except:
                               response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                               return locals()
                              
                      else:
                          
                           if ("M.S." or "ms") in pagamento:
                               
                               giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                               if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                               
                               giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                               scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                               day_start,day_end = monthrange(scadenza.year, scadenza.month)
                               scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                               scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                               scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                               scadenza = scadenza.strftime("%d/%m/%Y") 
                               
                           else:
                               # Fine mese senza M.S.               
                               giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                               if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                               
                               scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                               day_start,day_end = monthrange(scadenza.year, scadenza.month)
                               scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                              
                                       
                          
                           
                      
                      
                      fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(iban_cliente),pagamento,str(scadenza))
                except Exception,e:
                      # print e
                      response.flash="Controllare il tipo di pagamento in anagrafica"
                      return locals()
                
                # print "Aggiunta rig"
                sconti = row.sconti
                if row.sconti is None:
                    
                    sconti=""
                
                try:
                    if row.prezzo == "0":
                        row.prezzo = ""
                    f = float(row.prezzo)
                    # print "SONO QUI : PREZZO = ".format(f)
                except:
                    msg = "Prezzo non presente " + riferimento_ddt + " Cod.Art : " + row.codice_articolo
                    response.flash=msg
                    return locals()
                   
                try:
                	f=float(row.quantita)
                except:
                	msg = "Quantità non valida Cod.Art : " + row.codice_articolo + " Qta : "
                	response.flash=msg
                	return locals()
                	pass
                
                importo = saved_importo = float(row.quantita) * float(row.prezzo)
                
                importo = Money(str(importo),"EUR")
                importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                prezzo = str(row.prezzo).replace(".",",")
                
                codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                
                # print "VALLLLE " + row.codice_iva
                
                descrizione_codice_iva = db(db.righe_in_ordine_cliente.id == row.id_riga_ordine, db.righe_in_ordine_cliente.n_riga==row.n_riga).select().first()["codice_iva"]
                codice_iva=db(db.anagrafica_codici_iva.descrizione_codice_iva == descrizione_codice_iva).select().first()["codice_iva"]
                
                
                row.codice_iva=codice_iva
                
                
                # print "Nuovo codice iva : "+row.codice_iva
                
                if "Esenzione" in descrizione_codice_iva:
                    scritta_esenzione = True
                
                percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == descrizione_codice_iva).select().first()["percentuale_iva"]
                
                importo_totale +=saved_importo
                
               
                imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                
                if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = saved_importo
                else:
                    lista_codici_iva[codice_iva] += saved_importo
                
             
                
            else:
            	"""
            	Passo il commento ma resetto tutti i campi
            	"""
            	# print row
            	row.riferimento_ordine=""
            	row.u_m=""
            	row.quantita=""
            	prezzo=""
            	sconti=""
            	importo=""
            	codice_iva=""
            	row.codice_articolo=""
            	# row.descrizione=row.commento
            	
            	
            	
            	
            	
            
            
            fattura.add_row(row.codice_articolo,row.descrizione,row.riferimento_ordine,row.u_m,row.quantita,prezzo,sconti,importo,codice_iva)
        
    
    
    # print lista_codici_iva
    
    
   
            
        
    bollo= dati_cliente.bollo
  
    if bollo:
        print "SONO NEL BOLLO"
        codice_articolo="BOLLO"
        descrizione="art. 15 DPR 633/72"
        riferimento_ordine=""
        quantita="1"
        prezzo="2,00"
        sconti=""
        codice_iva="53"
        u_m="Nr"
        importo="2,00"
           

        fattura.add_row(codice_articolo,descrizione,riferimento_ordine,u_m,quantita,prezzo,sconti,importo,codice_iva)
        if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = 2
        else:
                    lista_codici_iva[codice_iva] +=2
        
            
    if scritta_esenzione:
        fattura.add_row("","","","","","","","","")
        fattura.add_row("","","","","","","","","")
        
        scritte = scritta_esenzione_cliente.split(",")
        
        for scritta in scritte:
            fattura.add_row("",scritta,"","","","","","","") 
    
    bollo_presente = False
   
    for k,v in lista_codici_iva.iteritems():
        codice_iva = k
        importo_netto = v
        # print "LISTA CODICI : ",codice_iva,importo_netto
        dettaglio_iva = db(db.anagrafica_codici_iva.codice_iva == codice_iva).select().first()
        percentuale_iva = dettaglio_iva.percentuale_iva
        descrizione_iva = dettaglio_iva.descrizione_codice_iva
        imposta_iva = return_imposta(v,percentuale_iva)
        if dettaglio_iva.bollo_su_importi_esenti is True:
            if not bollo_presente:
                bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
                bollo_presente = True
                
        fattura.footer_2(codice_iva,"",return_currency(importo_netto),descrizione_iva,return_currency(imposta_iva),"")
        
                
                
    if bollo:
        _bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
        importo_totale += float(_bollo)    
     
   
     
    importo_totale_da_salvare = importo_totale +imposta_iva
    # print "Imposta iva {0}".format(imposta_iva)
    # print "Importo calcolato {0}".format(importo_totale_da_salvare)
    
              
    importo_totale = Money(str(importo_totale),"EUR")
    importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
    fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
    fattura.totale(str(ritorna_prezzo_europeo(importo_totale_da_salvare)))
    
    # db.fatture_salvate.insert(scadenza=scadenza_salvata,nome_cliente=nome_cliente,data_fattura = datetime.datetime.now().strftime("%d/%m/%Y"),numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = importo_totale_da_salvare)     
    
    # print "SCADENZA {0}".format(scadenza)    
        
    
   
    
    """
    fattura.foote,Field('nome_cliente')sr("Totale merce","Sconto","Netto merce","spese varie","spese_trasporto","totale_imponibile","Totale imposta")
    fattura.footer_2("CodIva","Spese accessorie","Imponibile","Iva","Imposta","Bolli")
    fattura.footer_2("CodIva2","Spese accessorie2","Imponibile2","Iva2","Imposta2","Bolli2")
    fattura.totale("14567645")
    """
    
    fattura.add_row("","","","","","","","","")
    fattura.add_row("",annotazioni,"","","","","","","")
    
    fattura.insert_rows()
    fattura.create_pdf()
    
    # db(db.fattura).delete()
    # db.fattura.insert(numero_fattura = numero_fattura_da_salvare)


@service.jsonrpc
@service.jsonrpc2
def crea_fattura_preview_istantanea(args):
    
    
    id_cliente=args['0']
    # print "ID CLIENTE : ",id_cliente
    
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    
   
    """
    Dati cliente
    """
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    annotazioni=dati_cliente.annotazioni
    scritta_esenzione_cliente = dati_cliente.descrizione_esenzione_iva


   
    bollo= dati_cliente.bollo
  
    if bollo:
        db(db.righe_in_fattura_istantanea.codice_articolo=="BOLLO").delete()
        db.righe_in_fattura_istantanea.insert(
            codice_articolo="BOLLO",
            descrizione="art. 15 DPR 633/72",
            riferimento_ordine="",
            qta="1",
            prezzo="2",
            sconti="",
            codice_iva="Esenzione Iva",
            commento=""
   
            
            )
     

    scritta_esenzione = False
    # print "1"
    # print dettagli_banca
    # print "2"
    
    start_date = datetime.datetime.now()
    
    fattura = FATTURA("FATTURA IMMEDIATA",datetime.datetime.now().date().strftime("%d/%m/%Y"),numero_fattura_da_salvare,anteprima=True)
    fattura.intestazione(nome_cliente,citta_cliente,indirizzo_cliente,cap_cliente,provincia_cliente,nazione_cliente,cf_cliente,pi_cliente)
    
    try:
        fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),"PAGAMENTO","SCADENZA")
        
    except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica cliente"
                  return locals()
    
    
    
    
    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []

    scritta_esenzione = False

    
    

    if True:
        
        rows = db(db.righe_in_fattura_istantanea).select()
        
        for row in rows:
            
            try:
                 
                  
                  pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                        
                  if "F.M." in pagamento:
                      fine_mese = True
                  else:
                      fine_mese = False
                      
                   
                  
                    
                  
                  
                  if not fine_mese:
                       try:
                          giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                          if start_date.date().month==12 or start_date.date().month==1:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                      
                          scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                          scadenza_salvata = scadenza
                          scadenza = scadenza.strftime("%d/%m/%Y")
                       except:
                           response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                           return locals()
                  else:
                      
                       if ("M.S." or "ms") in pagamento:
                           
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                           scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                           scadenza = scadenza.strftime("%d/%m/%Y") 
                           
                       else:
                           # Fine mese senza M.S.               
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           
                           if start_date.date().month==12 or start_date.date().month==1:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                           
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                       
                      
                      
                       pass 
                   
                   
                  
                  fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),pagamento,str(scadenza))
            except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica"
                  return locals()
            
            
            sconti = row.sconti
            if row.sconti is None:
                
                sconti=""
            
            if len(row.codice_articolo) > 0 and not 'commento' in row.codice_articolo:
                try:
                    if row.prezzo == "0":
                        row.prezzo = ""
                    f = float(row.prezzo)
                    # print "SONO QUI : PREZZO = ".format(f)
                except:
                    msg = "Prezzo non presente Cod.Art : " + row.codice_articolo
                    response.flash=msg
                    return locals()
                   
                try:
                	f=float(row.qta)
                except:
                	msg = "Quantità non valida Cod.Art : " + row.codice_articolo
                	response.flash=msg
                	return locals()
                	pass
            
                importo = saved_importo = float(row.qta) * float(row.prezzo)
                importo = Money(str(importo),"EUR")
                importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                prezzo = str(row.prezzo).replace(".",",")
                
                codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]
                descrizione_codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["descrizione_codice_iva"]
                if "Esenzione" in descrizione_codice_iva:
                    scritta_esenzione = True
                
                importo_totale +=saved_importo
                imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                
                if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = saved_importo
                else:
                    lista_codici_iva[codice_iva] += saved_importo
            
            else:
                row.u_m,row.codice_articolo,prezzo,sconti,importo,codice_iva,row.riferimento_ordine,row.qta = "","","","","","","",""
            	row.codice_articolo,prezzo,sconti,importo,codice_iva,row.riferimento_ordine,row.qta = "","","","","","",""
                row.descrizione=row.commento
                row.u_m=""
            
            fattura.add_row(row.codice_articolo,row.descrizione,row.riferimento_ordine,row.u_m,row.qta,prezzo,sconti,importo,codice_iva)
        
    
    
    # print lista_codici_iva


    if scritta_esenzione:
        fattura.add_row("","","","","","","","","")
        fattura.add_row("","","","","","","","","")
        
        scritte = scritta_esenzione_cliente.split(",")
        
        for scritta in scritte:
            fattura.add_row("",scritta,"","","","","","","")
    
    
    scadenza=""
    bollo_presente = False
    bollo = 0
    for k,v in lista_codici_iva.iteritems():
        codice_iva = k
        importo_netto = v
        # print "LISTA CODICI : ",codice_iva,importo_netto
        dettaglio_iva = db(db.anagrafica_codici_iva.codice_iva == codice_iva).select().first()
        percentuale_iva = dettaglio_iva.percentuale_iva
        descrizione_iva = dettaglio_iva.descrizione_codice_iva
        imposta_iva = return_imposta(v,percentuale_iva)
        if dettaglio_iva.bollo_su_importi_esenti is True:
            if not bollo_presente:
                bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
                bollo_presente = True
                
        fattura.footer_2(codice_iva,"",return_currency(importo_netto),descrizione_iva,return_currency(imposta_iva),"")
        bollo = 0
                
    """            
    if bollo_presente:
        bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
        importo_totale += float(bollo)
    """ 
    importo_totale_da_salvare = importo_totale +imposta_iva
    
    
              
    importo_totale = Money(str(importo_totale),"EUR")
    importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
    fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
    fattura.totale(str(importo_totale_da_salvare))
    
    # db.fatture_salvate.insert(scadenza=scadenza_salvata,nome_cliente=nome_cliente,data_fattura = datetime.datetime.now().strftime("%d/%m/%Y"),numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = importo_totale_da_salvare)     
    
    # print "SCADENZA {0}".format(scadenza)    
        
    
   
    
    """
    fattura.foote,Field('nome_cliente')sr("Totale merce","Sconto","Netto merce","spese varie","spese_trasporto","totale_imponibile","Totale imposta")
    fattura.footer_2("CodIva","Spese accessorie","Imponibile","Iva","Imposta","Bolli")
    fattura.footer_2("CodIva2","Spese accessorie2","Imponibile2","Iva2","Imposta2","Bolli2")
    fattura.totale("14567645")
    """
    fattura.add_row("","","","","","","","","")
    fattura.add_row("",annotazioni,"","","","","","","")
    fattura.insert_rows()
    fattura.create_pdf()
    
    # db(db.fattura).delete()
    # db.fattura.insert(numero_fattura = numero_fattura_da_salvare)


@service.jsonrpc
@service.jsonrpc2
def crea_fattura_preview_istantanea_accredito(args):
    
    # print "In preview instantanea accredito"
    id_cliente=args['0']
    # print "ID CLIENTE : ",id_cliente
    
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    
   
    """
    Dati cliente
    """
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    annotazioni=dati_cliente.annotazioni
    
    
    # print "1"
    # print dettagli_banca
    # print "2"
    
    
    start_date = datetime.datetime.now()
    
    fattura = FATTURA("NOTA DI ACCREDITO",datetime.datetime.now().date().strftime("%d/%m/%Y"),numero_fattura_da_salvare,anteprima=True)
    fattura.intestazione(nome_cliente,citta_cliente,indirizzo_cliente,cap_cliente,provincia_cliente,nazione_cliente,cf_cliente,pi_cliente)
    
    try:
        fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),"PAGAMENTO","SCADENZA")
        
    except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica cliente"
                  return locals()
    
    
    
    
    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []
    if True:
        
        rows = db(db.righe_in_fattura_istantanea).select()
        
        for row in rows:
            
            try:
                 
                  
                  pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                        
                  if "F.M." in pagamento:
                      fine_mese = True
                  else:
                      fine_mese = False
                      
                   
                  
                    
                  
                  
                  if not fine_mese:
                       try:
                          giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                      
                      
                          scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                          scadenza_salvata = scadenza
                          scadenza = scadenza.strftime("%d/%m/%Y")
                       except:
                           response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                           return locals()
                  else:
                      
                       if ("M.S." or "ms") in pagamento:
                           
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                           scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                           scadenza = scadenza.strftime("%d/%m/%Y") 
                           
                       else:
                           # Fine mese senza M.S.               
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                       
                      
                      
                       pass 
                   
                   
                  
                  fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),pagamento,str(scadenza))
            except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica"
                  return locals()
            
            
            sconti = row.sconti
            if row.sconti is None:
                
                sconti=""
            
            if len(row.codice_articolo) > 0 and not 'commento' in row.codice_articolo:
                try:
                    if row.prezzo == "0":
                        row.prezzo = ""
                    f = float(row.prezzo)
                    # print "SONO QUI : PREZZO = ".format(f)
                except:
                    msg = "Prezzo non presente   Cod.Art : " + row.codice_articolo
                    response.flash=msg
                    return locals()
            
                try:
                	f=float(row.qta)
                except:
                	msg = "Quantità non valida Cod.Art : " + row.codice_articolo
                	response.flash=msg
                	return locals()
                	pass
                	
                
                importo = saved_importo = float(row.qta) * float(row.prezzo)
                importo = Money(str(importo),"EUR")
                importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                prezzo = str(row.prezzo).replace(".",",")
                
                codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]
                
                importo_totale +=saved_importo
                imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                
                if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = saved_importo
                else:
                    lista_codici_iva[codice_iva] += saved_importo
            
            else:
                row.codice_articolo,prezzo,sconti,importo,codice_iva,row.riferimento_ordine,row.qta = "","","","","","",""
                row.descrizione=row.commento
            
            fattura.add_row(row.codice_articolo,row.descrizione,row.riferimento_ordine,row.u_m,row.qta,prezzo,sconti,importo,codice_iva)
        
    
    
    # print lista_codici_iva
    
    
    scadenza=""
    bollo_presente = False
    bollo = 0
    for k,v in lista_codici_iva.iteritems():
        codice_iva = k
        importo_netto = v
        # print "LISTA CODICI : ",codice_iva,importo_netto
        dettaglio_iva = db(db.anagrafica_codici_iva.codice_iva == codice_iva).select().first()
        percentuale_iva = dettaglio_iva.percentuale_iva
        descrizione_iva = dettaglio_iva.descrizione_codice_iva
        imposta_iva = return_imposta(v,percentuale_iva)
        if dettaglio_iva.bollo_su_importi_esenti is True:
            if not bollo_presente:
                bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
                bollo_presente = True
                
        fattura.footer_2(codice_iva,"",return_currency(importo_netto),descrizione_iva,return_currency(imposta_iva),return_currency(bollo))
        bollo = 0
                
                
    if bollo_presente:
        bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
        importo_totale += float(bollo)
     
    importo_totale_da_salvare = importo_totale +imposta_iva
    
    
    # print "Importo totale "+str(importo_totale_da_salvare)      
    importo_totale = Money(str(importo_totale),"EUR")
    importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
    fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
    fattura.totale(str(importo_totale_da_salvare))
    
    # db.fatture_salvate.insert(scadenza=scadenza_salvata,nome_cliente=nome_cliente,data_fattura = datetime.datetime.now().strftime("%d/%m/%Y"),numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = importo_totale_da_salvare)     
    
    # print "SCADENZA {0}".format(scadenza)    
        
    
   
    
    """
    fattura.foote,Field('nome_cliente')sr("Totale merce","Sconto","Netto merce","spese varie","spese_trasporto","totale_imponibile","Totale imposta")
    fattura.footer_2("CodIva","Spese accessorie","Imponibile","Iva","Imposta","Bolli")
    fattura.footer_2("CodIva2","Spese accessorie2","Imponibile2","Iva2","Imposta2","Bolli2")
    fattura.totale("14567645")
    """
    fattura.add_row("","","","","","","","","")
    fattura.add_row("",annotazioni,"","","","","","","")
    
    fattura.insert_rows()
    fattura.create_pdf()
    
    # db(db.fattura).delete()
    # db.fattura.insert(numero_fattura = numero_fattura_da_salvare)

@service.jsonrpc
@service.jsonrpc2
def crea_fattura_istantanea(args):
    
    
    id_cliente=args['0']
    # print "ID CLIENTE : ",id_cliente
    
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    
   
    """
    Dati cliente
    """
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    annotazioni=dati_cliente.annotazioni

    bollo= dati_cliente.bollo
  
    if bollo:
        db(db.righe_in_fattura_istantanea.codice_articolo=="BOLLO").delete()
        db.righe_in_fattura_istantanea.insert(
            codice_articolo="BOLLO",
            descrizione="art. 15 DPR 633/72",
            riferimento_ordine="",
            qta="1",
            prezzo="2",
            sconti="",
            codice_iva="Esenzione Iva",
            commento=""
   
            
            )
    
    
    scritta_esenzione = False
    # print "1"
    # print dettagli_banca
    # print "2"
    
    start_date = datetime.datetime.now()
    
    fattura = FATTURA("FATTURA IMMEDIATA",datetime.datetime.now().date().strftime("%d/%m/%Y"),numero_fattura_da_salvare)
    fattura.intestazione(nome_cliente,citta_cliente,indirizzo_cliente,cap_cliente,provincia_cliente,nazione_cliente,cf_cliente,pi_cliente)
    
    try:
        fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),"PAGAMENTO","SCADENZA")
        
    except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica cliente"
                  return locals()
    
    
    
    
    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []
    if True:
        
        rows = db(db.righe_in_fattura_istantanea).select()
        
        for row in rows:
            
            try:
                 
                  
                  pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                        
                  if "F.M." in pagamento:
                      fine_mese = True
                  else:
                      fine_mese = False
                      
                   
                  
                    
                  
                  
                  if not fine_mese:
                       try:
                          giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                      
                      
                          scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                          scadenza_salvata = scadenza
                          scadenza = scadenza.strftime("%d/%m/%Y")
                       except:
                           response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                           return locals()
                  else:
                      
                       if ("M.S." or "ms") in pagamento:
                           
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                           scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                           scadenza = scadenza.strftime("%d/%m/%Y") 
                           
                       else:
                           # Fine mese senza M.S.               
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                       
                      
                      
                       pass 
                   
                   
                  
                  fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),pagamento,str(scadenza))
            except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica"
                  return locals()
            
            
            sconti = row.sconti
            if row.sconti is None:
                
                sconti=""
            
            if len(row.codice_articolo) > 0 and 'commento' not in row.codice_articolo:
                try:
                    if row.prezzo == "0":
                        row.prezzo = ""
                    f = float(row.prezzo)
                    # print "SONO QUI : PREZZO = ".format(f)
                except:
                    msg = "Prezzo non presente  Cod.Art : " + row.codice_articolo
                    response.flash=msg
                    return locals()
                   
                try:
                	f=float(row.qta)
                except:
                	msg = "Quantità non valida Cod.Art : " + row.codice_articolo
                	response.flash=msg
                	# print "!QWUEIQWEUQWUE"
                	return locals()
                	pass
            
                importo = saved_importo = float(row.qta) * float(row.prezzo)
                importo = Money(str(importo),"EUR")
                importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                prezzo = str(row.prezzo).replace(".",",")
                
                codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]

                descrizione_codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["descrizione_codice_iva"]
                if "Esenzione" in descrizione_codice_iva:
                    scritta_esenzione = True
               
                
                importo_totale +=saved_importo
                imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                
                if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = saved_importo
                else:
                    lista_codici_iva[codice_iva] += saved_importo
            
            else:
                row.u_m,row.codice_articolo,prezzo,sconti,importo,codice_iva,row.riferimento_ordine,row.qta = "","","","","","","",""
                row.descrizione=row.commento
            
            fattura.add_row(row.codice_articolo,row.descrizione,row.riferimento_ordine,row.u_m,row.qta,prezzo,sconti,importo,codice_iva)
        
    
    if scritta_esenzione:
        scritta_esenzione_cliente = dati_cliente.descrizione_esenzione_iva
        fattura.add_row("","","","","","","","","")
        fattura.add_row("","","","","","","","","")
        scritte = scritta_esenzione_cliente.split(",")
        
        for scritta in scritte:
            fattura.add_row("",scritta,"","","","","","","")
    # print lista_codici_iva
    
    
    
    bollo_presente = False
    bollo = 0
    for k,v in lista_codici_iva.iteritems():
        codice_iva = k
        importo_netto = v
        # print "LISTA CODICI : ",codice_iva,importo_netto
        dettaglio_iva = db(db.anagrafica_codici_iva.codice_iva == codice_iva).select().first()
        percentuale_iva = dettaglio_iva.percentuale_iva
        descrizione_iva = dettaglio_iva.descrizione_codice_iva
        imposta_iva = return_imposta(v,percentuale_iva)
        if dettaglio_iva.bollo_su_importi_esenti is True:
            if not bollo_presente:
                bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
                bollo_presente = True
                
        fattura.footer_2(codice_iva,"",return_currency(importo_netto),descrizione_iva,return_currency(imposta_iva),return_currency(bollo))
        bollo = 0
                
    """            
    if bollo_presente:
        bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
        importo_totale += float(bollo)
    """

    importo_totale_da_salvare = importo_totale +imposta_iva
    
    
              
    importo_totale = Money(str(importo_totale),"EUR")
    importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
    fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
    fattura.totale(str(importo_totale_da_salvare))
    
    lista_ddt=[] #Fattura senza ddt = istantanea
    
    db.fatture_salvate.insert(scadenza=scadenza,nome_cliente=nome_cliente,data_fattura = datetime.datetime.now().strftime("%d/%m/%Y"),numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = importo_totale_da_salvare)     
    
    # print "SCADENZA {0}".format(scadenza)    
        
    
   
    
    """
    fattura.foote,Field('nome_cliente')sr("Totale merce","Sconto","Netto merce","spese varie","spese_trasporto","totale_imponibile","Totale imposta")
    fattura.footer_2("CodIva","Spese accessorie","Imponibile","Iva","Imposta","Bolli")
    fattura.footer_2("CodIva2","Spese accessorie2","Imponibile2","Iva2","Imposta2","Bolli2")
    fattura.totale("14567645")
    """
    fattura.add_row("","","","","","","","","")
    fattura.add_row("",annotazioni,"","","","","","","")
    
    fattura.insert_rows()
    fattura.create_pdf()
    
    db(db.fattura).delete()
    db.fattura.insert(numero_fattura = numero_fattura_da_salvare)


@service.jsonrpc
@service.jsonrpc2
def crea_fattura_istantanea_accredito(args):
    
    
    id_cliente=args['0']
    # print "ID CLIENTE : ",id_cliente
    
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    
   
    """
    Dati cliente
    """
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    annotazioni=dati_cliente.annotazioni
    
    
    # print "1"
    # print dettagli_banca
    # print "2"
    
    start_date = datetime.datetime.now()
    
    fattura = FATTURA("NOTA DI ACCREDITO",datetime.datetime.now().date().strftime("%d/%m/%Y"),numero_fattura_da_salvare)
    fattura.intestazione(nome_cliente,citta_cliente,indirizzo_cliente,cap_cliente,provincia_cliente,nazione_cliente,cf_cliente,pi_cliente)
    
    try:
        fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),"PAGAMENTO","SCADENZA")
        
    except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica cliente"
                  return locals()
    
    
    
    
    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []
    if True:
        
        rows = db(db.righe_in_fattura_istantanea).select()
        
        for row in rows:
            
            try:
                 
                  
                  pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                        
                  if "F.M." in pagamento:
                      fine_mese = True
                  else:
                      fine_mese = False
                      
                   
                  
                    
                  
                  
                  if not fine_mese:
                       try:
                          giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                      
                      
                          scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                          scadenza_salvata = scadenza
                          scadenza = scadenza.strftime("%d/%m/%Y")
                       except:
                           response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                           return locals()
                  else:
                      
                       if ("M.S." or "ms") in pagamento:
                           
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                           scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                           scadenza = scadenza.strftime("%d/%m/%Y") 
                           
                       else:
                           # Fine mese senza M.S.               
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                       
                      
                      
                       pass 
                   
                   
                  
                  fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),pagamento,str(scadenza))
            except Exception,e:
                  # print e
                  response.flash="Controllare il tipo di pagamento in anagrafica"
                  return locals()
            
            
            sconti = row.sconti
            if row.sconti is None:
                
                sconti=""
            
            if len(row.codice_articolo) > 0 and not 'commento' in row.codice_articolo:
                try:
                    if row.prezzo == "0":
                        row.prezzo = ""
                    f = float(row.prezzo)
                    # print "SONO QUI : PREZZO = ".format(f)
                except:
                    msg = "Prezzo non presente  Cod.Art : " + row.codice_articolo
                    response.flash=msg
                    return locals()
                   
                   
                try:
                	f=float(row.qta)
                except:
                	msg = "Quantità non valida Cod.Art : " + row.codice_articolo
                	response.flash=msg
                	return locals()
                	pass
            
                importo = saved_importo = float(row.qta) * float(row.prezzo)
                importo = Money(str(importo),"EUR")
                importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                prezzo = str(row.prezzo).replace(".",",")
                
                codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]
                
                importo_totale +=saved_importo
                imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                
                if not codice_iva in lista_codici_iva:
                    lista_codici_iva[codice_iva] = saved_importo
                else:
                    lista_codici_iva[codice_iva] += saved_importo
            
            else:
                row.codice_articolo,prezzo,sconti,importo,codice_iva,row.riferimento_ordine,row.qta = "","","","","","",""
                row.descrizione=row.commento
                row.u_m=""
            
            fattura.add_row(row.codice_articolo,row.descrizione,row.riferimento_ordine,row.u_m,row.qta,prezzo,sconti,importo,codice_iva)
        
    
    
    # print lista_codici_iva
    
    
    
    bollo_presente = False
    bollo = 0
    for k,v in lista_codici_iva.iteritems():
        codice_iva = k
        importo_netto = v
        # print "LISTA CODICI : ",codice_iva,importo_netto
        dettaglio_iva = db(db.anagrafica_codici_iva.codice_iva == codice_iva).select().first()
        percentuale_iva = dettaglio_iva.percentuale_iva
        descrizione_iva = dettaglio_iva.descrizione_codice_iva
        imposta_iva = return_imposta(v,percentuale_iva)
        if dettaglio_iva.bollo_su_importi_esenti is True:
            if not bollo_presente:
                bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
                bollo_presente = True
                
        fattura.footer_2(codice_iva,"",return_currency(importo_netto),descrizione_iva,return_currency(imposta_iva),return_currency(bollo))
        bollo = 0
                
                
    if bollo_presente:
        bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
        importo_totale += float(bollo)
     
    importo_totale_da_salvare = importo_totale +imposta_iva
    
    
              
    importo_totale = Money(str(importo_totale),"EUR")
    importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
    fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
    fattura.totale(str(importo_totale_da_salvare))
    
    lista_ddt=[] #Fattura senza ddt = istantanea
    
    db.fatture_salvate.insert(scadenza=scadenza,nome_cliente=nome_cliente,data_fattura = datetime.datetime.now().strftime("%d/%m/%Y"),numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = importo_totale_da_salvare)     
    
    # print "SCADENZA {0}".format(scadenza)    
        
    
   
    
    """
    fattura.foote,Field('nome_cliente')sr("Totale merce","Sconto","Netto merce","spese varie","spese_trasporto","totale_imponibile","Totale imposta")
    fattura.footer_2("CodIva","Spese accessorie","Imponibile","Iva","Imposta","Bolli")
    fattura.footer_2("CodIva2","Spese accessorie2","Imponibile2","Iva2","Imposta2","Bolli2")
    fattura.totale("14567645")
    """
    fattura.add_row("","","","","","","","","")
    fattura.add_row("",annotazioni,"","","","","","","")
    fattura.insert_rows()
    fattura.create_pdf()
    
    db(db.fattura).delete()
    db.fattura.insert(numero_fattura = numero_fattura_da_salvare)

def ritorna_righe_in_ddt(id_ddt):
    righe = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == id_ddt).select()
    r=[]
    
    for riga in righe:
        r.append(riga.codice_articolo+"\n")
    
    return r

def del_saved_rows(table, row_id):
    db(db.saved_righe_in_ddt_cliente.saved_ddt_id == row_id).delete()
    return "ok"

def del_ddt_clienti():
    db.ddt_cliente.righe=Field.Virtual("righe", lambda row: ritorna_righe_in_ddt(row.ddt_cliente.id))
    
    fields = [db.ddt_cliente.nome_cliente,db.ddt_cliente.data_richiesta,db.ddt_cliente.numero_ddt,db.ddt_cliente.righe]
    form = SQLFORM.grid(db.ddt_cliente,formname='del',maxtextlength=100,create=False,editable=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,fields=fields,ondelete=del_saved_rows)
    return locals()

def controllo_errori():
    db(db.errori).delete()
    
    
    
    clienti = db(db.clienti).select()
    for cliente in clienti:
        if cliente.codice_banca is None or len(cliente.codice_banca)<1:
            errore = "Codice banca assente per il cliente {0}".format(cliente.nome)
            db.errori.insert(tipo_errore = errore)
        else:
             banca_cliente =cliente.codice_banca
             dati_banca_cliente = db(db.anagrafica_banche.descrizione == banca_cliente).select().first()
             if dati_banca_cliente is None:
		     errore = "Banca non in anagrafica per il cliente {0}".format(cliente.nome)
		     db.errori.insert(tipo_errore = errore)
             
            
            
        if cliente.citta is None or len(cliente.citta)<1:
            errore = "Città assente per il cliente {0}".format(cliente.nome)
            db.errori.insert(tipo_errore = errore)
            
        if cliente.pagamento is None or len(cliente.pagamento)<1:
            errore = "Pagamento assente per il cliente {0}".format(cliente.nome)
            db.errori.insert(tipo_errore = errore)
    
    
    clienti = db(db.fornitori).select()
    for cliente in clienti:
        if cliente.codice_banca is None or len(cliente.codice_banca)<1:
            errore = "Codice banca assente per il fornitore {0}".format(cliente.nome)
            db.errori.insert(tipo_errore = errore)
            
        if cliente.citta is None or len(cliente.citta)<1:
            errore = "Città assente per il fornitore {0}".format(cliente.nome)
            db.errori.insert(tipo_errore = errore)
            
        if cliente.pagamento is None or len(cliente.pagamento)<1:
            errore = "Pagamento assente per il fornitore {0}".format(cliente.nome)
            db.errori.insert(tipo_errore = errore)
    
    
    clienti = db(db.anagrafica_banche).select()
    for cliente in clienti:
        if cliente.codice_abi is None or len(cliente.codice_abi)!=5:
            errore = "Lunghezza codice ABI non corretta per la banca {0}".format(cliente.descrizione)
            db.errori.insert(tipo_errore = errore)
            
        if cliente.codice_cab is None or len(cliente.codice_cab)!=5:
            errore = "Lunghezza codice CAB non corretta per la banca {0}".format(cliente.descrizione)
            db.errori.insert(tipo_errore = errore)
            
        
    
        """
        if cliente.domicilio is None or len(cliente.domicilio)<1:
            errore = "Domicilio assente per il fornitore {0}".format(cliente.nome)
            db.errori.insert(tipo_errore = errore)
        """
        
    count = db.saved_ddt.numero_ddt.count()
    ddts = db().select(db.saved_ddt.numero_ddt,groupby = db.saved_ddt.numero_ddt, having=count > 1)
    
    for ddt in ddts:
        errore = "DDT duplicato numero {0} del {1} per il cliente {2}".format(ddt.numero_ddt,ritorna_data_inserimento(ddt.numero_ddt),ritorna_cliente_da_numero_ddt(ddt.numero_ddt))
        db.errori.insert(tipo_errore = errore)
    
    
    
    pagamenti = db(db.ordine_cliente).select()
    for pagamento in pagamenti:
        if db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento.pagamento).isempty():
             if pagamento.pagamento is None:
                 errore = "Pagamento non esistente per ordine cliente {0}. Verrà usato il pagamento associato al cliente".format(pagamento.ultimo_codice_ordine)
             else:
                 errore = "Pagamento '{0}' ordine cliente {1} non esistente in anagrafica pagamenti".format(pagamento.pagamento,pagamento.ultimo_codice_ordine)
             db.errori.insert(tipo_errore = errore)
    
    ddts=db(db.saved_ddt).select()
    for ddt in ddts:
        if db(db.ddt_cliente.id ==ddt.saved_ddt_id).isempty():
            # db(db.saved_ddt.id == ddt.id).delete()
            errore = "Cancellato ddt orfano salvato {0}".format(ddt.id)
            db.errori.insert(tipo_errore = errore)
       
       
    ordini=db(db.ordine_cliente).select()
    for ordine in ordini:
        if db(db.righe_in_ordine_cliente.id_ordine_cliente == ordine.id).isempty():
            # db(db.saved_ddt.id == ddt.id).delete()
            errore = "Ordine cliente {0} senza righe associate".format(ordine.ultimo_codice_ordine)
            db.errori.insert(tipo_errore = errore) 
            
        if tutte_le_righe_completate_in_ordine_id(ordine.id):
            # print "ORDINE ID : ",ordine.id
            ordine.update_record(ddt_completato='T')
        else:
             ordine.update_record(ddt_completato='F')
             
    articoli=db(db.anagrafica_articoli).select()
    for articolo in articoli:
        
             
            # articolo.update_record(tipo_articolo="Prodotto finito",tipo_ordine="Ordine acquisto",codice_sottoconto="8820125")
            
            if articolo.giacenza is None:
                errore = "Articolo {0} senza giacenza".format(articolo.codice_articolo)
                db.errori.insert(tipo_errore = errore)
                articolo.update_record(giacenza=0)
              
            try:
                if int(articolo.giacenza) < 0:
                    errore = "Articolo {0} con giacenza negativa".format(articolo.codice_articolo)
                    db.errori.insert(tipo_errore = errore)
                    # articolo.update_record(giacenza=0)
            except:
            	errore = "Articolo {0} con giacenza in errore".format(articolo.codice_articolo)
                db.errori.insert(tipo_errore = errore)
                articolo.update_record(giacenza=0)
                pass
            
            if articolo.codice_iva is None:
                errore = "Articolo {0} senza iva".format(articolo.codice_articolo)
                db.errori.insert(tipo_errore = errore)
                # articolo.update_record(giacenza=0)
                
            if articolo.trattamento is None:
                errore = "Articolo {0} senza trattamento".format(articolo.codice_articolo)
                db.errori.insert(tipo_errore = errore)
                articolo.update_record(trattamento="Si")   
               
                           
            if articolo.giacenza == "5000":
                errore = "Articolo {0} senza giacenza".format(articolo.codice_articolo)
                db.errori.insert(tipo_errore = errore)
                articolo.update_record(giacenza=0)                              
    
    
    anagrafica_banche_azienda = db(db.anagrafica_banche_azienda).select()
    if anagrafica_banche_azienda is None:
        errore = "INSERIRE ANAGRAFICA NOSTRA BANCA PER RIBA"
        db.errori.insert(tipo_errore = errore)
        
    
    """
    per rimuovere il "|" dai ddt fattura
    Commentare una volta eseguita questa routine!!
    
    fatture = db(db.fatture_salvate).select()
    for fattura in fatture:
        saved_date = fattura.scadenza
        data_fattura = fattura.data_fattura
        
        
        
        if "|" in fattura.id_ddt:
            # print "ok"
            lista_ddt = fattura.id_ddt.split("|")
            
            lista_ddt = filter(None,lista_ddt)
            # print lista_ddt
            fattura.data_fattura=datetime.datetime.strptime("12/01/1979","%d/%m/%Y")
            fattura.update_record(id_ddt=str(lista_ddt))
            # print fattura
            # db(db.fatture_salvate.id==fattura.id).update(id_ddt=lista_ddt)
        
        
        if saved_date is None:
            # print "Scadenza trovata = {0} ".format(return_scadenza(fattura.id))
            fattura.update_record(scadenza=datetime.datetime.strptime(return_scadenza(fattura.id),"%d/%m/%Y"))
        
        # print data_fattura
        if fattura.id <= 100:
           fattura.update_record(data_fattura=datetime.datetime.strptime("28/02/2017","%d/%m/%Y")) 
        
            
        # print fattura.id
        pagamento,scadenza = ritorna_tipo_pagamento_da_fattura(fattura.id)
        # print "si"
        if "R.B." in pagamento:
            fattura.update_record(richiede_riba='T')
        else:
            fattura.update_record(richiede_riba='F')
            
            
     """     
    """
    rows=db(db.saved_righe_in_ddt_cliente).select()
    for row in rows:
        count_ddt = db(db.ddt_cliente.id == row.saved_ddt_id).count()
        if count == 0:
             errore = "Trovata riga non associata a ddt : id_riga = {0}".format(row.id)
             db.errori.insert(tipo_errore = errore)
             db(db.saved_righe_in_ddt_cliente.id == row.id).delete()
             
    """
        
    form = SQLFORM.grid(db.errori,maxtextlength=500,editable=False,deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False)
    
    
    return locals()


def ritorna_data_inserimento(ddt_id):
    data = db(db.saved_ddt.numero_ddt == ddt_id).select().first()["data_inserimento"]
    data_ddt=datetime.datetime.strptime(data[0:10],"%Y-%m-%d").date()
    data_ddt=data_ddt.strftime("%d/%m/%Y")
    return data_ddt

def ritorna_cliente_da_numero_ddt(ddt_id):
    # ddt_id = db(db.saved_ddt.numero_ddt == ddt_id).select().first()["id"]
    # print ddt_id
    try:
        nome_cliente = db(db.ddt_cliente.numero_ddt == ddt_id).select()["nome_cliente"]
        
    except:
        nome_cliente = "NON ASSEGNATO"
    return nome_cliente

@service.jsonrpc
@service.jsonrpc2
def insert_ddt_preview(*args):
    
    
    id_ddt=args[0]
    consegna = args[1]
    trasporto = args[2]
    ditta = args[3]
    domicilio = args[4]
    aspetto = args[5]
    colli = args[6]
    porto = args[7]
    annotazioni = args[8]
    peso = args[9]
    causale = args[10]
    data_scelta = args[11]
    
    
    
    
    ddt_id = db(db.ddt_cliente.id == id_ddt).select().first()
    
    id_cliente = ddt_id.id_cliente
    nome_cliente = ddt_id.nome_cliente
    
    row = db(db.clienti.id==id_cliente).select().first()
    
    try:
        consegna = consegna.split(",")
    except:
        consegna = "Come intestazione ,,,,,,".split(",")
    """
    Insert into saved ddt table
    
    """
    
    numero_ddt_salvato = db(db.ddt).select().first()["numero_ddt"]
    n = numero_ddt_salvato.split("/")[0]
    a = numero_ddt_salvato.split("/")[1]
    new_n = str(int(n) + 1)
    numero_ddt_corrente = new_n + "/" + a
    
    # ddt_id.update_record(numero_ddt=numero_ddt_corrente)
    
    
    # db.saved_ddt.insert(numero_ddt = numero_ddt_corrente,saved_ddt_id = ddt_id.id, data_inserimento = datetime.datetime.now(), user_id = auth.user_id)
    # row2 = db(db.ddt).select().first()
    # row2.update_record(numero_ddt = numero_ddt_corrente)
    
    
    
    if len(data_scelta)>0:
        d = data_scelta
    else:
        d = datetime.datetime.now().date().strftime("%d/%m/%Y")
    
    pa = DDT(d,numero_ddt_corrente,"Cliente",anteprima=True)
    # print "DDT CORRENTE : ",numero_ddt_corrente
    pa.rows=[]
    # p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    pa.intestazione(row.nome, row.citta,row.indirizzo, row.cap, row.provincia, row.partita_iva, row.nazione,row.codice_fiscale)
    # p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    try:
      pa.consegna(consegna[0],consegna[1],consegna[2],consegna[3],consegna[4])
    except:
           pa.consegna("null","null","null","null","null")
    # p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    pa.info_trasporto(trasporto, ditta, causale,"", domicilio, "")
    # p.footer("scatola su bancale","100","ASSEGNATO","NOTE","123")
    pa.footer(aspetto,colli,porto,annotazioni,peso)
    
    rows = db(db.righe_in_ddt_cliente.user_id == auth.user_id).select()
    
    # tutte_le_righe_completate = True
    
    try:
      for row in rows:
         
         id_ordine = row["id_ordine"]
         codice_articolo = row["codice_articolo"]
         codice_ordine = row["codice_ordine"]
         
         if "commento" not in codice_articolo:
             quantita = row['quantita_prodotta']
             prezzo = row['prezzo']
            
             riferimento_ordine = row["riferimento_ordine"]+" - POS."+row["n_riga"]
            
            
             n_riga = row["n_riga"]
             codice_iva = row["codice_iva"]
             evasione = row["evasione"]
             id_riga_ordine = row["id_riga_ordine"]
        
             q = db(db.produzione_righe_per_ddt.id_riga_ordine == id_riga_ordine).select().first()
         
             if q is not None:
                 try:
                     quantita_richiesta = int(row["quantita_richiesta"])
                     quantita_prodotta = int(row["quantita_prodotta"])
                     quantita_prodotta_fino_ad_ora = 0
             
                     quantita_prodotta_fino_ad_ora = int(q.quantita_prodotta) + quantita_prodotta
                     # r = db(db.produzione_righe_per_ddt.id_riga_ordine == str(id_riga_ordine)).select().first()
                     # r.update_record(quantita_prodotta=str(quantita_prodotta_fino_ad_ora))
                 except Exception,e:
                     response.flash="Controlla le quantità"
                     return "ok"
                     # print e
                     
             else:
                 """
                 E' la prima volta che inserisco la riga della quantità
                 """
                 # print "E' la prima volta che inserisco la riga della quantita"
                 quantita_prodotta_fino_ad_ora = int(row["quantita_prodotta"])
                 quantita_prodotta = int(row["quantita_prodotta"])
                 quantita_richiesta = int(row["quantita_richiesta"])
                 # db.produzione_righe_per_ddt.insert(id_riga_ordine = id_riga_ordine,quantita_prodotta = quantita_prodotta)
                 
             
                 if  quantita_prodotta_fino_ad_ora >= int(quantita_richiesta):
                     # print "Chiudo la riga"
                     # to_update = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
                     # to_update.update_record(riga_emessa_in_ddt = True)
                     pass
                 else:
                   # tutte_le_righe_completate = Fals
                   pass
             
                 # print "SONO QUII"
                 # print "{0}".format(tutte_le_righe_completate)
                 quantita_totale_prodotta = int(quantita_prodotta) + int(quantita_prodotta_fino_ad_ora)
         
         
         
             
                  
         # print "CODICE ARTICOLO : ",codice_articolo
         if len(codice_articolo)>0:
               
               if "commento" not in codice_articolo:
               
                   descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
               
               else:
                   d = db(db.righe_in_ordine_cliente.id == row.id_riga_ordine).select().first()["commento"]
                   descrizione = d
                   row.codice_articolo=" "
                   n_riga=" "
                   riferimento_ordine=" "
                   quantita_prodotta=0
                   prezzo=" "
                   evasione=" "
                   row["u_m"]=" "
                   
                   
               pa.add_row(row.codice_articolo,descrizione,riferimento_ordine,row["u_m"],str(row.quantita_prodotta))
               
               # db.saved_righe_in_ddt_cliente.insert(saved_ddt_id = ddt_id.id,id_ordine = id_ordine,codice_ordine = codice_ordine, n_riga = n_riga,codice_articolo=codice_articolo,descrizione=descrizione,riferimento_ordine=row["riferimento_ordine"],u_m=row["u_m"],quantita=quantita_prodotta,prezzo=prezzo,evasione=evasione,user_id = auth.user_id,codice_iva=row["codice_iva"])
         else:
               descrizione =row.descrizione
               pa.add_row(row.codice_articolo,descrizione,"","","")
    
         
      
          
      
    except Exception,e:
        
        response.flash="Errore inserimento ddt {0}".format(e)
        return locals()     
        
         # print row
    
    # p.insert_rows()
    pa.insert_rows()
    # print pa.rows
    pa.create_pdf()
    
    # print request.folder
    # redirect(URL('ddt_clienti'))
    return "ok"


@service.jsonrpc
@service.jsonrpc2
def insert_ddt(*args):
    
    
    id_ddt=args[0]
    consegna = args[1]
    trasporto = args[2]
    ditta = args[3]
    domicilio = args[4]
    aspetto = args[5]
    colli = args[6]
    porto = args[7]
    annotazioni = args[8]
    peso = args[9]
    causale = args[10]
    data_scelta = args[11]
    # print consegna
    
    
    ddt_id = db(db.ddt_cliente.id == id_ddt).select().first()
    
    ddt_id.update_record(porto=porto,aspetto=aspetto,peso=peso,annotazioni=annotazioni,trasporto_a_mezzo=trasporto,causale_del_trasporto=causale,inizio_del_trasporto="",ditta_vettore=ditta,domicilio_vettore=domicilio,data_e_ora_del_ritiro="",user_id = auth.user_id,consegna=str(consegna))
    
    # print "Aggiornato"
    # return locals()
    id_cliente = ddt_id.id_cliente
    nome_cliente = ddt_id.nome_cliente
    
    row = db(db.clienti.id==id_cliente).select().first()
    
    
    
    try:
        consegna = consegna.split(",")
    except:
        consegna = "Come intestazione ,,,,,,".split(",")
    """
    Insert into saved ddt table
    
    """
    
    numero_ddt_salvato = db(db.ddt).select().first()["numero_ddt"]
    n = numero_ddt_salvato.split("/")[0]
    a = numero_ddt_salvato.split("/")[1]
    new_n = str(int(n) + 1)
    numero_ddt_corrente = new_n + "/" + a
    
    ddt_id.update_record(numero_ddt=numero_ddt_corrente)
    
    
    
    db.saved_ddt.insert(numero_ddt = numero_ddt_corrente,saved_ddt_id = ddt_id.id, data_inserimento = datetime.datetime.now(), user_id = auth.user_id)
    row2 = db(db.ddt).select().first()
    row2.update_record(numero_ddt = numero_ddt_corrente)
    
    
    
    if len(data_scelta)>0:
        d = data_scelta
    else:
        d = datetime.datetime.now().date().strftime("%d/%m/%Y")
    
    pa = DDT(d,numero_ddt_corrente,"Cliente")
    # print "DDT CORRENTE : ",numero_ddt_corrente
    pa.rows=[]
    # p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    pa.intestazione(row.nome, row.citta,row.indirizzo, row.cap, row.provincia, row.partita_iva, row.nazione,row.codice_fiscale)
    # p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    try:
      pa.consegna(consegna[0],consegna[1],consegna[2],consegna[3],consegna[4])
    except:
           pa.consegna("null","null","null","null","null")
    # p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    pa.info_trasporto(trasporto, ditta, causale,"", domicilio, "")
    # p.footer("scatola su bancale","100","ASSEGNATO","NOTE","123")
    pa.footer(aspetto,colli,porto,annotazioni,peso)
    
    rows = db(db.righe_in_ddt_cliente.user_id == auth.user_id).select()
    
    # tutte_le_righe_completate = True
    
    try:
      for row in rows:
         
         id_ordine = row["id_ordine"]
         codice_articolo = row["codice_articolo"]
         codice_ordine = row["codice_ordine"]
         
         if "commento" in codice_articolo:
             id_riga_ordine = row["id_riga_ordine"]
             evasione = row["evasione"]
             n_riga = row["n_riga"]
             
         
         elif "commento" not in codice_articolo:
             quantita = row['quantita_prodotta']
             prezzo = row['prezzo']
            
             riferimento_ordine = row["riferimento_ordine"]+" - POS."+row["n_riga"]
            
            
             n_riga = row["n_riga"]
             codice_iva = row["codice_iva"]
             evasione = row["evasione"]
             id_riga_ordine = row["id_riga_ordine"]
        
             q = db(db.produzione_righe_per_ddt.id_riga_ordine == id_riga_ordine).select().first()
         
             if q is not None:
                 try:
                     quantita_richiesta = int(row["quantita_richiesta"])
                     quantita_prodotta = int(row["quantita_prodotta"])
                     quantita_prodotta_fino_ad_ora = 0
             
                     quantita_prodotta_fino_ad_ora = int(q.quantita_prodotta) + quantita_prodotta
                     r = db(db.produzione_righe_per_ddt.id_riga_ordine == str(id_riga_ordine)).select().first()
                     r.update_record(quantita_prodotta=str(quantita_prodotta_fino_ad_ora))
                     
                     if  quantita_prodotta_fino_ad_ora >= int(quantita_richiesta):
                         # print "Chiudo la riga"
                         to_update = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
                         to_update.update_record(riga_emessa_in_ddt = True)
                         db(db.riserva_quantita.id_riga_ordine==id_riga_ordine).delete()
                     
                 except Exception,e:
                     response.flash="Controlla le quantità"
                     return "ok"
                     # print e
                     
             else:
                 """
                 E' la prima volta che inserisco la riga della quantità
                 """
                 # print "E' la prima volta che inserisco la riga della quantita"
                 quantita_prodotta_fino_ad_ora = int(row["quantita_prodotta"])
                 quantita_prodotta = int(row["quantita_prodotta"])
                 quantita_richiesta = int(row["quantita_richiesta"])
                 db.produzione_righe_per_ddt.insert(id_riga_ordine = id_riga_ordine,quantita_prodotta = quantita_prodotta)
                 
             
                 if  quantita_prodotta_fino_ad_ora >= int(quantita_richiesta):
                     # print "Chiudo la riga"
                     to_update = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
                     to_update.update_record(riga_emessa_in_ddt = True)
                     # db(db.riserva_quantita.id_riga_ordine==id_riga_ordine).delete()
                 
                 else:
                   # tutte_le_righe_completate = Fals
                   pass
             
                 # print "SONO QUII"
                 # print "{0}".format(tutte_le_righe_completate)
                 quantita_totale_prodotta = int(quantita_prodotta) + int(quantita_prodotta_fino_ad_ora)
         
         
         
             
                  
         # print "CODICE ARTICOLO : ",codice_articolo
         if len(codice_articolo)>0:
               
               if "commento" not in codice_articolo:
               
                   descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
                   
                   da_rimuovere = int(quantita_prodotta) * -1
                   db.riserva_quantita.insert(codice_articolo = row.codice_articolo,quantita = da_rimuovere,id_riga_ordine = id_riga_ordine,user_id=auth.user_id)
                   
                   rimuovi_giacenza(codice_articolo,row.quantita_prodotta)
               
                   """Metto negativo per liberare la prenotazione articolo"""
               
               else:
                   d = db(db.righe_in_ordine_cliente.id == row.id_riga_ordine).select().first()["commento"]
                   descrizione = d
                   row.codice_articolo=" "
                   # n_riga=" "
                   riferimento_ordine=" "
                   quantita_prodotta=0
                   prezzo=" "
                   evasione=datetime.datetime.now()
                   row["u_m"]=" "
                   
                   
               pa.add_row(row.codice_articolo,descrizione,riferimento_ordine,row["u_m"],str(row.quantita_prodotta))
               
               db.saved_righe_in_ddt_cliente.insert(id_riga_ordine=id_riga_ordine,saved_ddt_id = ddt_id.id,id_ordine = id_ordine,codice_ordine = codice_ordine, n_riga = n_riga,codice_articolo=codice_articolo,descrizione=descrizione,riferimento_ordine=row["riferimento_ordine"],u_m=row["u_m"],quantita=quantita_prodotta,prezzo=prezzo,evasione=evasione,user_id = auth.user_id,codice_iva=row["codice_iva"])
               
               
              
               
               
               
               
               
         else:
               descrizione =row.descrizione
               pa.add_row(row.codice_articolo,descrizione,"","","")
    
         
      
         # print descrizione
      """
      if tutte_le_righe_completate:
             ordine = db(db.ordine_cliente.id == id_ordine).select().first()
             ordine.update_record(ddt_completato = True)
      """
      if tutte_le_righe_completate():
          ordine = db(db.ordine_cliente.id == id_ordine).select().first()
          ordine.update_record(ddt_completato = True)
          
      
    except Exception,e:
        
        response.flash="Errore inserimento ddt {0}".format(e)
        return locals()     
        
         # print row
    
    # p.insert_rows()
    pa.insert_rows()
    # print pa.rows
    pa.create_pdf()
    
    # print request.folder
    redirect(URL('ddt_clienti'))
    return "ok"


def rimuovi_giacenza(codice_articolo,quantita_prodotta):
    
    # print codice_articolo,quantita_prodotta
    row = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first()
    # print row
    attuale = int(row.giacenza)
    da_aggiornare = str(attuale - int(quantita_prodotta))
    
    # print "Attuale : {0} Da aggiornare = {1}".format(attuale,da_aggiornare)
    
    row.update_record(giacenza = da_aggiornare)
    
    
    

def manutenzione_righe_ordini_clienti():
    
    form = SQLFORM.grid(db.righe_in_ordine_cliente)
    return locals()

@service.jsonrpc
@service.jsonrpc2
def insert_mod_ddt(*args):
    
    
    id_ddt=args[0]
    consegna = args[1]
    trasporto = args[2]
    ditta = args[3]
    domicilio = args[4]
    aspetto = args[5]
    colli = args[6]
    porto = args[7]
    annotazioni = args[8]
    peso = args[9]
    causale = args[10]
    
    # print "Consegna ",consegna
    ddt_id = db(db.ddt_cliente.id == id_ddt).select().first()
    # print ddt_id
    ddt_id.update_record(porto=porto,aspetto=aspetto,peso=peso,annotazioni=annotazioni,trasporto_a_mezzo=trasporto,causale_del_trasporto=causale,inizio_del_trasporto="",ditta_vettore=ditta,domicilio_vettore=domicilio,data_e_ora_del_ritiro="",user_id = auth.user_id,consegna=consegna)
    
    # print "CIAOOOO ",ddt_id
    
    # return locals()
    id_cliente = ddt_id.id_cliente
    nome_cliente = ddt_id.nome_cliente
    
    row = db(db.clienti.id==id_cliente).select().first()
    
    
    
    try:
        consegna = consegna.split(",")
    except:
        consegna = "Come intestazione ,,,,,,".split(",")
    """
    Insert into saved ddt table
    
    """
    
    
    numero_ddt_corrente = ddt_id.numero_ddt
        
    # print numero_ddt_corrente
    # db.saved_ddt.insert(numero_ddt = numero_ddt_corrente,saved_ddt_id = ddt_id.id, data_inserimento = datetime.datetime.now(), user_id = auth.user_id)
    
    data_scelta=""
    if len(data_scelta)>0:
        d = data_scelta
    else:
        d = datetime.datetime.now().date().strftime("%d/%m/%Y")
    
    pa = DDT(d,numero_ddt_corrente,"Cliente")
    # print "DDT CORRENTE : ",numero_ddt_corrente
    pa.rows=[]
    # p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    pa.intestazione(row.nome, row.citta,row.indirizzo, row.cap, row.provincia, row.partita_iva, row.nazione,row.codice_fiscale)
    # p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    try:
      pa.consegna(consegna[0],consegna[1],consegna[2],consegna[3],consegna[4])
    except:
           pa.consegna("null","null","null","null","null")
    # p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    pa.info_trasporto(trasporto, ditta, causale,"", domicilio, "")
    # p.footer("scatola su bancale","100","ASSEGNATO","NOTE","123")
    pa.footer(aspetto,colli,porto,annotazioni,peso)
    
    # print "ciao ",ddt_id
    
    """
    1) salvare le righe del ddt in una tabella per creare UNDO
    2) cancellare i riferimenti a saved_righe_in_ddt_cliente
    3) inserire le righe ddt as usual
    """
    produzione_da_rimuovere=0
    old_rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id ==ddt_id.id).select()
    
    # print old_rows
    for r in old_rows:
        # print old_rows
        db.saved_righe_in_ddt_cliente_undo.insert(**db.saved_righe_in_ddt_cliente._filter_fields(r))
        db(db.saved_righe_in_ddt_cliente.id == r.id).delete()
        produzione_da_rimuovere = r.quantita
        """
        Ritornare id riga ordine anche se NULL
        """
        
        if r.id_riga_ordine is None or len(r.id_riga_ordine)<1:
                id_riga_ordine=db((db.righe_in_ordine_cliente.id_ordine_cliente == r.id_ordine) & (db.righe_in_ordine_cliente.n_riga ==r.n_riga)).select().first()["id"]
        else:
                id_riga_ordine = r.id_riga_ordine
        
        db((db.produzione_righe_per_ddt.quantita_prodotta == produzione_da_rimuovere) & (db.produzione_righe_per_ddt.id_riga_ordine == id_riga_ordine)).delete()
   
    # return ""
    
    
    # tutte_le_righe_completate = True
    
    
    rows = db(db.righe_in_ddt_cliente.user_id == auth.user_id).select()
    db(db.saved_righe_in_ddt_cliente.saved_ddt_id ==ddt_id.id).delete()
    try:
      for row in rows:
         
         id_ordine = row["id_ordine"]
         codice_articolo = row["codice_articolo"]
         codice_ordine = row["codice_ordine"]
         
         
         if row.id_riga_ordine is None or len(row.id_riga_ordine)<1:
                id_riga_ordine=db((db.righe_in_ordine_cliente.id_ordine_cliente == row.id_ordine) & (db.righe_in_ordine_cliente.n_riga ==row.n_riga)).select().first()["id"]
         else:
                id_riga_ordine = row.id_riga_ordine
                
         # print "ID RIGA ORDINE ",id_riga_ordine
         
         
         if "commento" not in codice_articolo:
             quantita = row['quantita_prodotta']
             prezzo = row['prezzo']
            
             riferimento_ordine = row["riferimento_ordine"]+" - POS."+row["n_riga"]
            
            
             n_riga = row["n_riga"]
             codice_iva = row["codice_iva"]
             evasione = row["evasione"]
             # id_riga_ordine = row["id_riga_ordine"]
             
             # print id_riga_ordine
             
                    
             
             
             """
             q = db(db.produzione_righe_per_ddt.id_riga_ordine == id_riga_ordine).select().first()
             # print "Quantita trovata già prodotta : ",q
             if q is not None:
                 try:
                     quantita_richiesta = int(row["quantita_richiesta"])
                     quantita_prodotta = int(row["quantita_prodotta"])
                     quantita_prodotta_fino_ad_ora = 0
             
                     quantita_prodotta_fino_ad_ora =  quantita_prodotta
                     r = db(db.produzione_righe_per_ddt.id_riga_ordine == str(id_riga_ordine)).select().first()
                     r.update_record(quantita_prodotta=str(quantita_prodotta_fino_ad_ora))
                 except Exception,e:
                     response.flash="Controlla le quantità"
                     # print e
                     return "ok"
                     
                     
             else:
             """
             if True:
                 """
                 E' la prima volta che inserisco la riga della quantità
                 """
                 # print "E' la prima volta che inserisco la riga della quantita"
                 quantita_prodotta_fino_ad_ora = int(row["quantita_prodotta"])
                 quantita_prodotta = int(row["quantita_prodotta"])
                 quantita_richiesta = int(row["quantita_richiesta"])
                 db.produzione_righe_per_ddt.insert(id_riga_ordine = id_riga_ordine,quantita_prodotta = quantita_prodotta)
                 
                 # print "qui"
                 if  quantita_prodotta_fino_ad_ora >= int(quantita_richiesta):
                     # print "Chiudo la riga"
                     to_update = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
                     to_update.update_record(riga_emessa_in_ddt = 'T')
                     db.riserva_quantita.insert
                     
                     rimuovi_giacenza(codice_articolo,row.quantita_prodotta)
               
                     """Metto negativo per liberare la prenotazione articolo"""
                 
                 else:
                   # print "Riapro la riga"
                   # print "ID RIGA ORDINE : ",id_riga_ordine
                   to_update = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
                   # print to_update.id
                   to_update.update_record(riga_emessa_in_ddt = 'F')
                   
                   
                   
                   
                 da_rimuovere = int(quantita_prodotta_fino_ad_ora) * -1
                 db.riserva_quantita.insert(codice_articolo = row.codice_articolo,quantita = da_rimuovere,id_riga_ordine = id_riga_ordine,user_id=auth.user_id)
                 db.riserva_quantita.insert(codice_articolo = row.codice_articolo,quantita = quantita_prodotta_fino_ad_ora,id_riga_ordine = id_riga_ordine,user_id=auth.user_id)
                   
                            
                 giacenza = int(produzione_da_rimuovere)
                 
                 # print "produzione da rimuovere = ",giacenza
                 vecchia_giacenza = int(db(db.anagrafica_articoli.codice_articolo ==codice_articolo ).select().first()["giacenza"])
                 # print "vecchia giacenza ",vecchia_giacenza
                 
                 
                 nuova_giacenza = vecchia_giacenza - giacenza
                 
                 # print "nuova giacenza ",nuova_giacenza
                 
                 nuova_giacenza +=  int(quantita_prodotta_fino_ad_ora)
                 
                 # print "nuova giacenza 2 ",nuova_giacenza
                 g = db(db.anagrafica_articoli.codice_articolo ==codice_articolo).select().first()
                 g.update_record(giacenza = str(nuova_giacenza))
                 
                 
                 
                 
                 quantita_totale_prodotta = int(quantita_prodotta) + int(quantita_prodotta_fino_ad_ora)
         
         
         
             
                  
         # print "CODICE ARTICOLO : ",codice_articolo
         if len(codice_articolo)>0:
               
               if "commento" not in codice_articolo:
               
                   descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
               
               else:
                   d = db(db.righe_in_ordine_cliente.id == row.id_riga_ordine).select().first()["commento"]
                   descrizione = d
                   row.codice_articolo=" "
                   n_riga=" "
                   riferimento_ordine=" "
                   quantita_prodotta=0
                   prezzo=" "
                   evasione=datetime.datetime.now()
                   row["u_m"]=" "
                   
                   
               pa.add_row(row.codice_articolo,descrizione,riferimento_ordine,row["u_m"],str(row.quantita_prodotta))
               
               db.saved_righe_in_ddt_cliente.insert(id_riga_ordine=row.id_riga_ordine,saved_ddt_id = ddt_id.id,id_ordine = id_ordine,codice_ordine = codice_ordine, n_riga = n_riga,codice_articolo=codice_articolo,descrizione=descrizione,riferimento_ordine=row["riferimento_ordine"],u_m=row["u_m"],quantita=quantita_prodotta,prezzo=prezzo,evasione=evasione,user_id = auth.user_id,codice_iva=row["codice_iva"])
         else:
               descrizione =row.descrizione
               pa.add_row(row.codice_articolo,descrizione,"","","")
    
         
      
         # print descrizione
      """
      if tutte_le_righe_completate:
             ordine = db(db.ordine_cliente.id == id_ordine).select().first()
             ordine.update_record(ddt_completato = True)
      """
      if tutte_le_righe_completate():
          ordine = db(db.ordine_cliente.id == id_ordine).select().first()
          ordine.update_record(ddt_completato = True)
      else:
          ordine = db(db.ordine_cliente.id == id_ordine).select().first()
          ordine.update_record(ddt_completato = False)
          
          
      
    except Exception,e:
        
        response.flash="Errore inserimento ddt {0}".format(e)
        return locals()     
        
         # print row
    
    # p.insert_rows()
    pa.insert_rows()
    # print pa.rows
    pa.create_pdf()
    
    # print request.folder
    redirect(URL('ddt_clienti'))
    return "ok"


@service.jsonrpc
@service.jsonrpc2
def insert_mod_ddt_preview(*args):
    
    
    id_ddt=args[0]
    consegna = args[1]
    trasporto = args[2]
    ditta = args[3]
    domicilio = args[4]
    aspetto = args[5]
    colli = args[6]
    porto = args[7]
    annotazioni = args[8]
    peso = args[9]
    causale = args[10]
    
    
    ddt_id = db(db.ddt_cliente.id == id_ddt).select().first()
    
    # ddt_id.update_record(porto=porto,aspetto=aspetto,peso=peso,annotazioni=annotazioni,trasporto_a_mezzo=trasporto,causale_del_trasporto=causale,inizio_del_trasporto="",ditta_vettore=ditta,domicilio_vettore=domicilio,data_e_ora_del_ritiro="",user_id = auth.user_id)
    
    # print "CIAOOOO ",ddt_id
    
    id_cliente = ddt_id.id_cliente
    nome_cliente = ddt_id.nome_cliente
    
    row = db(db.clienti.id==id_cliente).select().first()
    
    
    
    try:
        consegna = consegna.split(",")
    except:
        consegna = "Come intestazione ,,,,,,".split(",")
    """
    Insert into saved ddt table
    
    """
    
    
    numero_ddt_corrente = ddt_id.numero_ddt
        
    # print numero_ddt_corrente
    # db.saved_ddt.insert(numero_ddt = numero_ddt_corrente,saved_ddt_id = ddt_id.id, data_inserimento = datetime.datetime.now(), user_id = auth.user_id)
    
    data_scelta =""
    
    if len(data_scelta)>0:
        d = data_scelta
    else:
        d = datetime.datetime.now().date().strftime("%d/%m/%Y")
    
    pa = DDT(d,numero_ddt_corrente,"Cliente",anteprima=True)
    # print "DDT CORRENTE : ",numero_ddt_corrente
    pa.rows=[]
    # p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    pa.intestazione(row.nome, row.citta,row.indirizzo, row.cap, row.provincia, row.partita_iva, row.nazione,row.codice_fiscale)
    # p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    try:
      pa.consegna(consegna[0],consegna[1],consegna[2],consegna[3],consegna[4])
    except:
           pa.consegna("null","null","null","null","null")
    # p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    pa.info_trasporto(trasporto, ditta, causale,"", domicilio, "")
    # p.footer("scatola su bancale","100","ASSEGNATO","NOTE","123")
    pa.footer(aspetto,colli,porto,annotazioni,peso)
    
    # print "ciao ",ddt_id
    
    """
    1) salvare le righe del ddt in una tabella per creare UNDO
    2) cancellare i riferimenti a saved_righe_in_ddt_cliente
    3) inserire le righe ddt as usual
    """
        
   
    # return ""
    
    
    # tutte_le_righe_completate = True
    
    
    rows = db(db.righe_in_ddt_cliente.user_id == auth.user_id).select()
    try:
      for row in rows:
         
         id_ordine = row["id_ordine"]
         codice_articolo = row["codice_articolo"]
         codice_ordine = row["codice_ordine"]
         
         if "commento" not in codice_articolo:
             quantita = row['quantita_prodotta']
             prezzo = row['prezzo']
            
             riferimento_ordine = row["riferimento_ordine"]+" - POS."+row["n_riga"]
            
            
             n_riga = row["n_riga"]
             codice_iva = row["codice_iva"]
             evasione = row["evasione"]
             id_riga_ordine = row["id_riga_ordine"]
             # print row
        
             q = db(db.produzione_righe_per_ddt.id_riga_ordine == id_riga_ordine).select().first()
             # print "Quantita trovata già prodotta : ",q
             if q is not None:
                 try:
                     quantita_richiesta = int(row["quantita_richiesta"])
                     quantita_prodotta = int(row["quantita_prodotta"])
                     quantita_prodotta_fino_ad_ora = 0
             
                     quantita_prodotta_fino_ad_ora = int(q.quantita_prodotta) + quantita_prodotta
                     # r = db(db.produzione_righe_per_ddt.id_riga_ordine == str(id_riga_ordine)).select().first()
                     # r.update_record(quantita_prodotta=str(quantita_prodotta_fino_ad_ora))
                 except Exception,e:
                     response.flash="Controlla le quantità"
                     # print e
                     return "ok"
                     
                     
             else:
                 """
                 E' la prima volta che inserisco la riga della quantità
                 """
                 # print "E' la prima volta che inserisco la riga della quantita"
                 quantita_prodotta_fino_ad_ora = int(row["quantita_prodotta"])
                 quantita_prodotta = int(row["quantita_prodotta"])
                 quantita_richiesta = int(row["quantita_richiesta"])
                 db.produzione_righe_per_ddt.insert(id_riga_ordine = id_riga_ordine,quantita_prodotta = quantita_prodotta)
                 
             
                 if  quantita_prodotta_fino_ad_ora >= int(quantita_richiesta):
                     # print "Chiudo la riga"
                     # to_update = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
                     # to_update.update_record(riga_emessa_in_ddt = True)
                     pass
                 else:
                   # tutte_le_righe_completate = Fals
                   pass
             
                 # print "SONO QUII"
                 # print "{0}".format(tutte_le_righe_completate)
                 quantita_totale_prodotta = int(quantita_prodotta) + int(quantita_prodotta_fino_ad_ora)
         
         
         
             
                  
         # print "CODICE ARTICOLO : ",codice_articolo
         if len(codice_articolo)>0:
               
               if "commento" not in codice_articolo:
               
                   descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
               
               else:
                   d = db(db.righe_in_ordine_cliente.id == row.id_riga_ordine).select().first()["commento"]
                   # print "COMMENTO {0}, RIGA ORDINE {1}".format(d,row.id_riga_ordine)
                   
                   descrizione = d
                   row.codice_articolo=" "
                   n_riga=" "
                   riferimento_ordine=" "
                   quantita_prodotta=0
                   prezzo=" "
                   evasione=" "
                   row["u_m"]=" "
                   
                   
               pa.add_row(row.codice_articolo,descrizione,riferimento_ordine,row["u_m"],str(row.quantita_prodotta))
               
               # db.saved_righe_in_ddt_cliente.insert(saved_ddt_id = ddt_id.id,id_ordine = id_ordine,codice_ordine = codice_ordine, n_riga = n_riga,codice_articolo=codice_articolo,descrizione=descrizione,riferimento_ordine=row["riferimento_ordine"],u_m=row["u_m"],quantita=quantita_prodotta,prezzo=prezzo,evasione=evasione,user_id = auth.user_id,codice_iva=row["codice_iva"])
         else:
               descrizione =row.descrizione
               pa.add_row(row.codice_articolo,descrizione,"","","")
    
         
      
         # print descrizione
      """
      if tutte_le_righe_completate:
             ordine = db(db.ordine_cliente.id == id_ordine).select().first()
             ordine.update_record(ddt_completato = True)
      
      
      """
          
      
    except Exception,e:
        
        response.flash="Errore inserimento ddt {0}".format(e)
        return locals()     
        
         # print row
    
    # p.insert_rows()
    pa.insert_rows()
    # print pa.rows
    pa.create_pdf()
    
    # print request.folder
    redirect(URL('ddt_clienti'))
    return "ok"


def tutte_le_righe_completate():
    rows = db(db.righe_in_ddt_cliente.user_id == auth.user_id).select()
    
    righe_completate = True
    # print "IN TUTTE LE RIGHE COMPLETATE -----------------"
    try:
      for row in rows:
         
         
         if row.id_riga_ordine is None or len(row.id_riga_ordine)<1:
                id_riga_ordine=db((db.righe_in_ordine_cliente.id_ordine_cliente == row.id_ordine) & (db.righe_in_ordine_cliente.n_riga ==row.n_riga)).select().first()["id"]
         else:
                id_riga_ordine = row.id_riga_ordine
         
         
         # print row
         # print "-----"
         
         
         
         
         codice_articolo = row["codice_articolo"]
         
         if "commento" not in codice_articolo:
            riga = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
            # print riga
            if not riga.riga_emessa_in_ddt:
                 # print "non tutte le righe sono state completate"     
                 righe_completate = False    
             
                
    except Exception,e:
         # print e
                     # quantita_totale_prodotta = int(quantita_prodotta) + int(quantita_prodotta_fino_ad_ora)
         pass
    return righe_completate
    

def riga_completata(id_riga_ordine):
    row = db(db.righe_in_ordine_cliente.id == id_riga_ordine ).select().first()
    # print row
    return row.riga_emessa_in_ddt



def tutte_le_righe_completate_in_ordine_id(id_ordine):
    rows = db(db.righe_in_ordine_cliente.id_ordine_cliente == id_ordine).select()
    
    righe_completate = True
   
    try:
      for row in rows:
                
         codice_articolo = row["codice_articolo"]
         
         if "commento" not in codice_articolo:
            
            
            if not row.riga_emessa_in_ddt:
                 # print "non tutte le righe sono state completate"     
                 righe_completate = False    
             
                
    except Exception,e:
         # print e
         # quantita_totale_prodotta = int(quantita_prodotta) + int(quantita_prodotta_fino_ad_ora)
         pass
    return righe_completate


@service.jsonrpc
@service.jsonrpc2
def insert_ddt_fornitori(*args):
    
    
    id_ddt=args[0]
    consegna = args[1]
    trasporto = args[2]
    ditta = args[3]
    domicilio = args[4]
    aspetto = args[5]
    colli = args[6]
    porto = args[7]
    annotazioni = args[8]
    peso = args[9]
    causale = args[10]
    data_scelta = args[11]
    
    if len(data_scelta)>0:
        d = data_scelta
    else:
        d = datetime.datetime.now().date().strftime("%d/%m/%Y")
    
    
    # print args
    ddt_id = db(db.ddt_fornitore.id == id_ddt).select().first()
    
    ddt_id.update_record(porto=porto,aspetto=aspetto,peso=peso,annotazioni=annotazioni,trasporto_a_mezzo=trasporto,causale_del_trasporto=causale,inizio_del_trasporto="",ditta_vettore=ditta,domicilio_vettore=domicilio,data_e_ora_del_ritiro="",user_id = auth.user_id)
    
    id_fornitore = ddt_id.id_fornitore
    nome_fornitore = ddt_id.nome_fornitore
    
    row = db(db.fornitori.id==id_fornitore).select().first()
    
    consegna = consegna.split(",")
    
    """
    Insert into saved ddt table
    
    """
    
    numero_ddt_salvato = db(db.ddt).select().first()["numero_ddt"]
    n = numero_ddt_salvato.split("/")[0]
    a = numero_ddt_salvato.split("/")[1]
    new_n = str(int(n) + 1)
    numero_ddt_corrente = new_n + "/" + a
    
    ddt_id.update_record(numero_ddt=numero_ddt_corrente)
    
    
    db.saved_ddt_fornitori.insert(numero_ddt = numero_ddt_corrente,saved_ddt_id = ddt_id.id, data_inserimento = d, user_id = auth.user_id)
    row2 = db(db.ddt).select().first()
    row2.update_record(numero_ddt = numero_ddt_corrente)
    
    
    
    
    pa = DDT(d,numero_ddt_corrente,"Fornitore")
    # print "DDT CORRENTE : ",numero_ddt_corrente
    pa.rows=[]
    # p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    pa.intestazione(row.nome, row.citta,row.indirizzo, row.cap, row.provincia, row.partita_iva, row.nazione,row.codice_fiscale)
    # p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    try:
      pa.consegna(consegna[0],consegna[1],consegna[2],consegna[3],consegna[4])
    except:
           pa.consegna("null","null","null","null","null")
    # p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    pa.info_trasporto(trasporto, ditta, causale,"", domicilio, "")
    # p.footer("scatola su bancale","100","ASSEGNATO","NOTE","123")
    pa.footer(aspetto,colli,porto,annotazioni,peso)
    
    rows = db(db.righe_in_ddt_fornitore.user_id == auth.user_id).select()
    
    for row in rows:
         quantita = row['quantita']
         prezzo = row['prezzo']
         codice_articolo = row["codice_articolo"]
         riferimento_ordine = row["codice_ordine"]+" - POS."+row["n_riga"]
         id_ordine = row["id_ordine"]
         codice_ordine = row["codice_ordine"]
         n_riga = row["n_riga"]
         codice_iva = row["codice_iva"]
         evasione = row["evasione"]

         ordine=db(db.ordine_fornitore.id == id_ordine).select().first()
         ordine.update_record(ddt_completato = True)
         
         # print "CODICE ARTICOLO : ",codice_articolo
         if len(codice_articolo)>0:
               # descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
               
               if "commento" not in codice_articolo:
               
                   descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
               
               else:
                   descrizione = row.descrizione
                   row.codice_articolo=""
                   n_riga=""
                   
               
               pa.add_row(row.codice_articolo,descrizione,riferimento_ordine,row["u_m"],row["quantita"])
               db.saved_righe_in_ddt_fornitore.insert(saved_ddt_id = ddt_id.id,id_ordine = id_ordine,codice_ordine = codice_ordine, n_riga = n_riga,codice_articolo=codice_articolo,descrizione=descrizione,riferimento_ordine=row["riferimento_ordine"],u_m=row["u_m"],quantita=quantita,prezzo=prezzo,evasione=evasione,user_id = auth.user_id,codice_iva=row["codice_iva"])
         else:
               descrizione =row.descrizione
               pa.add_row(row.codice_articolo,descrizione,"","","")
         # print descrizione
         
        
         # print row
    
    # p.insert_rows()
    pa.insert_rows()
    pa.create_pdf()

    
    
    # print request.folder
    redirect(URL('ddt_fornitori'))
    return "ok"


@service.jsonrpc
@service.jsonrpc2
def insert_ddt_fornitori_preview(*args):
    
    
    id_ddt=args[0]
    consegna = args[1]
    trasporto = args[2]
    ditta = args[3]
    domicilio = args[4]
    aspetto = args[5]
    colli = args[6]
    porto = args[7]
    annotazioni = args[8]
    peso = args[9]
    causale = args[10]
    data_scelta = args[11]
    
    if len(data_scelta)>0:
        d = data_scelta
    else:
        d = datetime.datetime.now().date().strftime("%d/%m/%Y")
    
    
    # print args
    ddt_id = db(db.ddt_fornitore.id == id_ddt).select().first()
    
    id_fornitore = ddt_id.id_fornitore
    nome_fornitore = ddt_id.nome_fornitore
    
    row = db(db.fornitori.id==id_fornitore).select().first()
    
    consegna = consegna.split(",")
    
    """
    Insert into saved ddt table
    
    """
    
    numero_ddt_salvato = db(db.ddt).select().first()["numero_ddt"]
    n = numero_ddt_salvato.split("/")[0]
    a = numero_ddt_salvato.split("/")[1]
    new_n = str(int(n) + 1)
    numero_ddt_corrente = new_n + "/" + a
    
    # ddt_id.update_record(numero_ddt=numero_ddt_corrente)
    
    
    # db.saved_ddt_fornitori.insert(numero_ddt = numero_ddt_corrente,saved_ddt_id = ddt_id.id, data_inserimento = datetime.datetime.now(), user_id = auth.user_id)
    row2 = db(db.ddt).select().first()
    # row2.update_record(numero_ddt = numero_ddt_corrente)
    
    
    
    
    pa = DDT(d,numero_ddt_corrente,"Fornitore",anteprima=True)
    # print "DDT CORRENTE : ",numero_ddt_corrente
    pa.rows=[]
    # p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    pa.intestazione(row.nome, row.citta,row.indirizzo, row.cap, row.provincia, row.partita_iva, row.nazione,row.codice_fiscale)
    # p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    try:
      pa.consegna(consegna[0],consegna[1],consegna[2],consegna[3],consegna[4])
    except:
           pa.consegna("null","null","null","null","null")
    # p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    pa.info_trasporto(trasporto, ditta, causale,"", domicilio, "")
    # p.footer("scatola su bancale","100","ASSEGNATO","NOTE","123")
    pa.footer(aspetto,colli,porto,annotazioni,peso)
    
    rows = db(db.righe_in_ddt_fornitore.user_id == auth.user_id).select()
    
    for row in rows:
         quantita = row['quantita']
         prezzo = row['prezzo']
         codice_articolo = row["codice_articolo"]
         riferimento_ordine = row["codice_ordine"]+" - POS."+row["n_riga"]
         id_ordine = row["id_ordine"]
         codice_ordine = row["codice_ordine"]
         n_riga = row["n_riga"]
         codice_iva = row["codice_iva"]
         evasione = row["evasione"]
         
         # print "CODICE ARTICOLO : ",codice_articolo
         if len(codice_articolo)>0:
               # descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
               
               if "commento" not in codice_articolo:
               
                   descrizione = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first().descrizione
               
               else:
                   descrizione = row.descrizione
                   row.codice_articolo=""
                   n_riga=""
                   
               
               pa.add_row(row.codice_articolo,descrizione,riferimento_ordine,row["u_m"],row["quantita"])
               # db.saved_righe_in_ddt_fornitore.insert(saved_ddt_id = ddt_id.id,id_ordine = id_ordine,codice_ordine = codice_ordine, n_riga = n_riga,codice_articolo=codice_articolo,descrizione=descrizione,riferimento_ordine=row["riferimento_ordine"],u_m=row["u_m"],quantita=quantita,prezzo=prezzo,evasione=evasione,user_id = auth.user_id,codice_iva=row["codice_iva"])
         else:
               descrizione =row.descrizione
               pa.add_row(row.codice_articolo,descrizione,"","","")
         # print descrizione
         
        
         # print row
    
    # p.insert_rows()
    pa.insert_rows()
    pa.create_pdf()
    
    # print request.folder
  
    return "ok"


def fatture_per_riba():
    fields=[db.fatture_scelte.numero_fattura,db.fatture_scelte.totale]
    form = SQLFORM.grid(db.fatture_scelte,create=False,editable=False,deletable=True,csv=False,fields=fields)
    return locals()


@service.jsonrpc
@service.jsonrpc2
def aggiungi_fattura(args):
    id_fattura = args['0']
    fattura = db(db.fatture_salvate.id ==id_fattura).select().first()
    
    db((db.fatture_scelte.id_fattura == id_fattura) & (db.fatture_scelte.user_id == auth.user_id)).delete()
    db.fatture_scelte.insert(scadenza=fattura.scadenza,id_cliente=fattura.id_cliente,cliente=fattura.nome_cliente,id_fattura=fattura.id,numero_fattura=fattura.numero_fattura,totale=fattura.totale,user_id = auth.user_id)
    
    return "ok"
    

@service.jsonrpc
@service.jsonrpc2
def add_row_to_ddt(args):
    
    id_ordine = args['0']
    
    # ritorna_quantita_saldo
    
    # auth.user_id
    # print "ID ORDINE : ",id_ordine
    
    db((db.righe_in_ddt_cliente.user_id == auth.user_id) & (db.righe_in_ddt_cliente.id_ordine == id_ordine)).delete()
    
    
    row = db(db.ordine_cliente.id == id_ordine).select().first()
    
    ultimo_codice_ordine = row['ultimo_codice_ordine']
    nome_cliente = row['nome_cliente']
    data_inserimento = row['data_inserimento']
    listino = row['listino']
    riferimento_ordine_cliente = row['riferimento_ordine_cliente']
    listino = row['listino']
    magazzino_interno = row['magazzino_interno']
    numero_ordine = row['ultimo_codice_ordine']
    saldo=0
    quantita_da_produrre=0
    
    
    rows = db((db.righe_in_ordine_cliente.id_ordine_cliente == id_ordine),(db.righe_in_ordine_cliente.riga_emessa_in_ddt == 'F')).select()
    for row in rows:
        # print "riga emessa in DDT"+str(row.riga_emessa_in_ddt)
        if "commento" in row.codice_articolo:
            quantita_da_produrre = prenotato = quantita_prodotta = saldo = 0
            db.righe_in_ddt_cliente.insert(saldo=0,codice_ordine=numero_ordine,quantita_richiesta=0,quantita_prodotta = 0, prezzo=0,sconti=0,codice_iva=row.codice_iva,evasione=row.evasione,user_id=auth.user_id,riferimento_ordine=riferimento_ordine_cliente,id_ordine=id_ordine,n_riga=row.n_riga,codice_articolo=row.codice_articolo,id_riga_ordine=row.id) 
            pass
        
        elif not row.riga_emessa_in_ddt:
            
            """
            Vado a vedere la quantità attualmente prodotta salvata nella tabella "produzione_righe_per_ddt"
            """
            row_id = row.id
            dettagli_produzione_riga = db(db.produzione_righe_per_ddt.id_riga_ordine == row.id).select().first()
            
            if dettagli_produzione_riga is not None:
                # print "Riga trovata"
                """
                Se ho trovato la riga vuol dire che è stata immessa una quantità in saldo.
                Vado a recuperare la quantità prodotta
                """
                # quantita_da_produrre= int(row.quantita) - int(dettagli_produzione_riga.quantita_prodotta)
                
                quantita_da_produrre = prenotato = ritorna_totale_prenotazione_da_codice_articolo_e_riga_id(row.codice_articolo,row_id) 
                
                
                quantita_prodotta = dettagli_produzione_riga.quantita_prodotta
                saldo=ritorna_quantita_saldo(row_id)
                
            else:
                # print "Riga non trovata"
                """
                Metto la quantita prodotta = alla quantita richiesta per velocizzare l'inserimento
                row.quantita è l'iniziale quantita richiesta nell'ordine
                """
                quantita_da_produrre = prenotato = ritorna_totale_prenotazione_da_codice_articolo_e_riga_id(row.codice_articolo,row_id) 
                quantita_prodotta = 0
                saldo=ritorna_quantita_saldo(row_id)
                
            
            
            
            
            db.righe_in_ddt_cliente.insert(saldo=saldo,codice_ordine=numero_ordine,quantita_richiesta=row.quantita,quantita_prodotta = quantita_da_produrre, prezzo=row.prezzo,sconti=row.sconti,codice_iva=row.codice_iva,evasione=row.evasione,user_id=auth.user_id,riferimento_ordine=riferimento_ordine_cliente,id_ordine=id_ordine,n_riga=row.n_riga,codice_articolo=row.codice_articolo,id_riga_ordine=row.id)
    
    
    return "ok"

@service.jsonrpc
@service.jsonrpc2
def add_row_to_ddt_mod(args):
    
    
    id_ordine = args['0']
    
    # auth.user_id
    # print "ID ORDINE : ",id_ordine
    
    db((db.righe_in_ddt_cliente.user_id == auth.user_id) & (db.righe_in_ddt_cliente.id_ordine == id_ordine)).delete()
    
    
    row = db(db.ordine_cliente.id == id_ordine).select().first()
    
    ultimo_codice_ordine = row['ultimo_codice_ordine']
    nome_cliente = row['nome_cliente']
    data_inserimento = row['data_inserimento']
    listino = row['listino']
    riferimento_ordine_cliente = row['riferimento_ordine_cliente']
    listino = row['listino']
    magazzino_interno = row['magazzino_interno']
    numero_ordine = row['ultimo_codice_ordine']
    
    rows = db(db.righe_in_ordine_cliente.id_ordine_cliente == id_ordine).select()
    
    quantita_prodotta=0
    row_id=0
    # print rows
    for row in rows:
        
        
        # print str(row.riga_emessa_in_ddt)
        # print type(row.riga_emessa_in_ddt)
        
        if "commento" in row.codice_articolo:
            quantita_da_produrre = prenotato = quantita_prodotta = saldo = 0
            
            pass
        
        elif not row.riga_emessa_in_ddt:
            """
            Vado a vedere la quantità attualmente prodotta salvata nella tabella "produzione_righe_per_ddt"
            """
            row_id = row.id
            dettagli_produzione_riga = db(db.produzione_righe_per_ddt.id_riga_ordine == row.id).select().first()
            if dettagli_produzione_riga is not None:
                # print "Riga trovata"
                """
                Se ho trovato la riga vuol dire che è stata immessa una quantità in saldo.
                Vado a recuperare la quantità prodotta
                """
                quantita_da_produrre= int(row.quantita) - int(dettagli_produzione_riga.quantita_prodotta)
                quantita_prodotta = dettagli_produzione_riga.quantita_prodotta
                
            else:
                # print "Riga non trovata"
                """
                Metto la quantita prodotta = alla quantita richiesta per velocizzare l'inserimento
                row.quantita è l'iniziale quantita richiesta nell'ordine
                """
                quantita_da_produrre = 0
                quantita_prodotta = 0
            
            
         
        quantita = 0  
            
        if row.quantita:
        	quantita = row.quantita
        
        # print row
        	
        db.righe_in_ddt_cliente.insert(saldo=ritorna_quantita_saldo(row_id),codice_ordine=numero_ordine,quantita_richiesta=quantita,quantita_prodotta = quantita_prodotta, prezzo=row.prezzo,sconti=row.sconti,codice_iva=row.codice_iva,evasione=row.evasione,user_id=auth.user_id,riferimento_ordine=riferimento_ordine_cliente,id_ordine=id_ordine,n_riga=row.n_riga,codice_articolo=row.codice_articolo,id_riga_ordine=row.id)
    
    
    return "ok"

def ritorna_quantita_richiesta_da_riga_salvata(id_riga_salvata):
    
    # print "IN RITORNA QUANTITA DA RIGA SALVATA ",id_riga_salvata
    try:
        riga_salvata = db(db.righe_in_ordine_cliente.id == id_riga_salvata).select().first()
                
        # print "ECCOLO E ",riga_salvata
    except Exception,e:
        # print e
        riga_salvata.quantita = 0
        
    return riga_salvata.quantita
    return 0
    

@service.jsonrpc
@service.jsonrpc2
def add_row_to_ddt_fornitori(args):
    
    id_ordine = args['0']
    
    # auth.user_id
    # print "ID ORDINE : ",id_ordine
    
    db((db.righe_in_ddt_fornitore.user_id == auth.user_id) & (db.righe_in_ddt_fornitore.id_ordine == id_ordine)).delete()
    
    
    row = db(db.ordine_fornitore.id == id_ordine).select().first()
    
    ultimo_codice_ordine = row['ultimo_codice_ordine']
    nome_fornitore = row['nome_fornitore']
    data_inserimento = row['data_inserimento']
    listino = row['listino']
    riferimento_ordine_fornitore = ""#row['riferimento_ordine_fornitore']
    listino = row['listino']
    magazzino_interno = row['magazzino_interno']
    numero_ordine = row['ultimo_codice_ordine']
    
    rows = db((db.righe_in_ordine_fornitore.id_ordine_fornitore == id_ordine),(db.righe_in_ordine_fornitore.riga_emessa_in_ddt == 'F')).select()
    for row in rows:
        
        
        # print str(row.riga_emessa_in_ddt)
        # print type(row.riga_emessa_in_ddt)
        if not row.riga_emessa_in_ddt:
                       
            
            db.righe_in_ddt_fornitore.insert(codice_ordine=numero_ordine,quantita=row.quantita,prezzo=row.prezzo,sconti=row.sconti,codice_iva=row.codice_iva,evasione=row.evasione,user_id=auth.user_id,riferimento_ordine=riferimento_ordine_fornitore,id_ordine=id_ordine,n_riga=row.n_riga,codice_articolo=row.codice_articolo,descrizione=row.commento)
    
    
    return "ok"

def return_fatture_in_scadenza():
    try:
        month = int(request.vars['m'])
    except:
        month = datetime.datetime.now().month
      
        
    day_start,day_end = monthrange(datetime.datetime.now().year, month)
    day_start = 1
    
    st = str(day_start)+"/"+str(month)+"/"+str(datetime.datetime.now().year)
    start_date = datetime.datetime(datetime.datetime.now().year,month,day_start)
    end_date = datetime.datetime(datetime.datetime.now().year,month,day_end)
    # print start_date,end_date
    
    
    fields=[db.fatture_salvate.nome_cliente,db.fatture_salvate.numero_fattura,db.fatture_salvate.scadenza,db.fatture_salvate.totale]
    links=[lambda row: BUTTON("Aggiungi fattura",_onclick=XML('aggiungiFatturaAEffetti('+str(row.id)+')'),_class='button btn btn-default')]
    form = SQLFORM.grid(db.fatture_salvate.scadenza <=end_date,user_signature=True,args=request.args[:1],create=False,editable=True,deletable=False,links=links,fields=fields,csv=False)
    return dict(form=form)

def return_scadenziario():
    try:
        month = int(request.vars['m'])
    except:
        month = datetime.datetime.now().month
      
    year = int(datetime.datetime.now().year)
			
    
    if  datetime.datetime.now().month > month:
    	year = year +1
    	
    # year=str(year)
    	
    
    day_start,day_end = monthrange(year, month)
    day_start = 1
    
    st = str(day_start)+"/"+str(month)+"/"+str(year)
    start_date = datetime.datetime(year,month,day_start)
    end_date = datetime.datetime(year,month,day_end)
    # print start_date,end_date
    
    db(db.scadenziario).delete()
    
    rows = db((db.righe_in_ordine_cliente.evasione >=start_date) & (db.righe_in_ordine_cliente.evasione <=end_date) & (db.righe_in_ordine_cliente.riga_emessa_in_ddt == 'F') & (db.righe_in_ordine_cliente.codice_articolo == db.anagrafica_articoli.codice_articolo) & (db.righe_in_ordine_cliente.id_ordine_cliente == db.ordine_cliente.id)).select(orderby = db.righe_in_ordine_cliente.evasione)
    for row in rows:
         # print row
         
         quantita_prodotta_fino_ad_ora = 0
         q = db(db.produzione_righe_per_ddt.id_riga_ordine == row.righe_in_ordine_cliente.id).select().first()
         
         if q is not None:
             quantita_prodotta_fino_ad_ora = int(q.quantita_prodotta)
             quantita_da_produrre = int(row.righe_in_ordine_cliente.quantita) - quantita_prodotta_fino_ad_ora
         else:
             quantita_da_produrre = row.righe_in_ordine_cliente.quantita
         
         row.quantita_da_produrre = quantita_da_produrre
         
         # print row.righe_in_ordine_cliente.prezzo
         
         
         
         try:
             prezzo = float(quantita_da_produrre) * float(row.righe_in_ordine_cliente.prezzo)
             # print prezzo
             
             prezzo = Money(str(prezzo),"EUR")
             prezzo = prezzo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
             # prezzo = str(row.prezzo).replace(".",",")
             """
             prezzo=0
             """
             # prezzo = float(quantita_da_produrre) * float(row.righe_in_ordine_cliente.prezzo)
         except:
             prezzo="Null"
             
         if "commento" not in row.righe_in_ordine_cliente.codice_articolo:
             if quantita_da_produrre >0:
                 db.scadenziario.insert(data_consegna = row.righe_in_ordine_cliente.evasione,cliente= row.ordine_cliente.nome_cliente,riferimento_ordine=row.ordine_cliente.riferimento_ordine_cliente,codice_ordine = row.ordine_cliente.ultimo_codice_ordine,codice_articolo = row.anagrafica_articoli.codice_articolo,descrizione = row.anagrafica_articoli.descrizione,qta_ordine = row.righe_in_ordine_cliente.quantita,qta_saldo = quantita_da_produrre,prezzo=prezzo,id_riga=row.righe_in_ordine_cliente.id)
    
    db.scadenziario.id.readable = False
    form = SQLFORM.grid(db.scadenziario,user_signature=True,args=request.args[:1],create=False,editable=False,deletable=False)
    return dict(form=form)


def ritorna_quantita_saldo(id_riga_ordine_cliente):
    
    quantita_prodotta_fino_ad_ora = 0
    q = db(db.produzione_righe_per_ddt.id_riga_ordine == id_riga_ordine_cliente).select().first()
    quantita_da_produrre = 0
    
    riga = db(db.righe_in_ordine_cliente.id == id_riga_ordine_cliente).select().first()
    
    quantita_riga=0
    if riga:
     	quantita_riga = int(riga.quantita)
    
    
    # print "ID RIGA ORDINE ",id_riga_ordine_cliente
    # print "quantita riga : ",quantita_riga
    
    if q is not None:
             quantita_prodotta_fino_ad_ora = int(q.quantita_prodotta)
             # print "Prodotta fino ad ora ",quantita_prodotta_fino_ad_ora
             quantita_da_produrre = quantita_riga - quantita_prodotta_fino_ad_ora
    else:
             quantita_da_produrre = quantita_riga
         
            
    
    return str(quantita_da_produrre)


def articoli_in_produzione():
    db.articoli_in_produzione.id.readable = False
    links=[lambda row: A(XML('Stampa RCP'),_class='button btn btn-default',_onClick=XML('stampaRcp('+str(row.id)+')'))]
    form = SQLFORM.grid(db.articoli_in_produzione,create=False,editable=False,deletable=False,maxtextlength=100,paginate=10,links=links)
    return dict(form=form)


def articoli_in_produzione_cron():
  
  
    def ritorna_dettaglio_cliente(id_ordine,ordini_clienti):
    	
    	# print "IN RITORNA DETTAGLIO"
        # print "ID ORDINE CERCATO ",id_ordine
    	
    	for ordine_cliente in ordini_clienti:
    		# print "ORDINE ID : ",ordine_cliente.id
    		if str(ordine_cliente.id) == str(id_ordine):
    			# print "TROVATO"
    			# print ordine_cliente
    			return ordine_cliente
    		    
    		
    	return None
  
    # print "qui"
    db(db.articoli_in_produzione).delete()
    # print "qui2"
    # rows = db((db.righe_in_ordine_cliente.riga_emessa_in_ddt == 'F') & (db.righe_in_ordine_cliente.codice_articolo == db.anagrafica_articoli.codice_articolo) & (db.righe_in_ordine_cliente.id_ordine_cliente == db.ordine_cliente.id)).select(orderby = db.righe_in_ordine_cliente.evasione)
    # rows = db((db.righe_in_ordine_cliente.riga_emessa_in_ddt == 'F') & (db.righe_in_ordine_cliente.codice_articolo == db.anagrafica_articoli.codice_articolo) & (db.righe_in_ordine_cliente.id_ordine_cliente == db.ordine_cliente.id)).select()
    
    
    rows=db((db.righe_in_ordine_cliente.riga_emessa_in_ddt == 'F') & (db.righe_in_ordine_cliente.codice_articolo == db.anagrafica_articoli.codice_articolo)).select(orderby = db.righe_in_ordine_cliente.evasione)
    # print rows
    
    dati_clienti =  db(db.ordine_cliente).select()

    

    iterazione=0
    for row in rows:
         # print iterazione
         iterazione+=1
         
         
         dettaglio_cliente = ritorna_dettaglio_cliente(row.righe_in_ordine_cliente.id_ordine_cliente,dati_clienti)
         # ( db(db.ordine_cliente.id == db.righe_in_ordine_cliente.id_ordine_cliente).select().first()
         
         if dettaglio_cliente is not None:
	         quantita_prodotta_fino_ad_ora = 0
	         q = db(db.produzione_righe_per_ddt.id_riga_ordine == row.righe_in_ordine_cliente.id).select().first()
	         
	         if q is not None:
	             quantita_prodotta_fino_ad_ora = int(q.quantita_prodotta)
	             # print "Fino ad ora ",quantita_prodotta_fino_ad_ora
	             
	             quantita_da_produrre = int(row.righe_in_ordine_cliente.quantita) - quantita_prodotta_fino_ad_ora
	         else:
	             quantita_da_produrre = row.righe_in_ordine_cliente.quantita
	         
	         row.quantita_da_produrre = quantita_da_produrre
	         
	         # print row.righe_in_ordine_cliente.prezzo
	         
	         
	         
	         try:
	             prezzo = float(quantita_da_produrre) * float(row.righe_in_ordine_cliente.prezzo)
	             # print prezzo
	             
	             prezzo = Money(str(prezzo),"EUR")
	             prezzo = prezzo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
	             # prezzo = str(row.prezzo).replace(".",",")
	             """
	             prezzo=0
	             """
	             # prezzo = float(quantita_da_produrre) * float(row.righe_in_ordine_cliente.prezzo)
	         except:
	             prezzo="Null"
	             # print "Eccezzione"
	             
	         if "commento" not in row.righe_in_ordine_cliente.codice_articolo:
	             if quantita_da_produrre > 0:
	                 # print "Inserisco"
	                 dettaglio_cliente
	                 # dettaglio_cliente = dettaglio_cliente.ordine_cliente
	                 db.articoli_in_produzione.insert(data_consegna = row.righe_in_ordine_cliente.evasione,cliente= dettaglio_cliente.nome_cliente,riferimento_ordine=dettaglio_cliente.riferimento_ordine_cliente,codice_ordine = dettaglio_cliente.ultimo_codice_ordine,codice_articolo = row.anagrafica_articoli.codice_articolo,descrizione = row.anagrafica_articoli.descrizione,qta_ordine = row.righe_in_ordine_cliente.quantita,qta_saldo = quantita_da_produrre,prezzo=prezzo,id_riga=str(row.righe_in_ordine_cliente.id))
    
    return locals()

def scadenziario():
    current_month = 1
    return locals()

def gestione_numero_fattura():
    form = SQLFORM.grid(db.fattura,csv=False,create=False,editable=True,searchable=False)
    return locals()

def gestione_numero_ddt():
    form = SQLFORM.grid(db.ddt,csv=False,create=False,editable=True,searchable=False,deletable=False)
    return locals()

def ritorna_numero_ddt_da_ddt_id(id):
    ddt_id = db(db.ddt_da_fatturare.id==id).select()
    # print ddt_id
    # numero_ddt = db(db.ddt_cliente.ddt_id == ddt_id).select().first()["numero_ddt"]
    return ddt_id

def ddt_da_fatturare():
    
    db.ddt_da_fatturare.user_id.default = auth.user_id
    # db.ddt_da_fatturare.numero_ddt = Field.Virtual("Numero_ddt",lambda row:ritorna_numero_ddt_da_ddt_id(row.ddt_da_fatturare.id))
    fields = [db.ddt_da_fatturare.numero_ddt,db.ddt_da_fatturare.data_emissione,db.ddt_da_fatturare.totale]
    form = SQLFORM.grid(db.ddt_da_fatturare,fields=fields,csv=False,create=False,editable=False,searchable=False)
    return locals()

def righe_in_ddt_cliente():
    
    db.righe_in_ddt_cliente.user_id.default = auth.user_id
    db.righe_in_ddt_cliente.quantita_richiesta.writable=False
    db.righe_in_ddt_cliente.quantita_richiesta.readonly=True
    
    if len(request.args) > 1 and ('edit' in request.args):
         # print "ECCOLO"
         fields = [db.righe_in_ddt_cliente.quantita_richiesta,db.righe_in_ddt_cliente.quantita_prodotta,db.righe_in_ddt_cliente.prezzo]
         form = SQLFORM.grid(db.righe_in_ddt_cliente,fields=fields,csv=False,user_signature=True,args=request.args[:1])
    else:       
    
         fields = [db.righe_in_ddt_cliente.codice_ordine,db.righe_in_ddt_cliente.codice_articolo,db.righe_in_ddt_cliente.n_riga,db.righe_in_ddt_cliente.riferimento_ordine,db.righe_in_ddt_cliente.quantita_richiesta,db.righe_in_ddt_cliente.saldo,db.righe_in_ddt_cliente.quantita_prodotta,db.righe_in_ddt_cliente.prezzo,db.righe_in_ddt_cliente.evasione]
         form = SQLFORM.grid(db.righe_in_ddt_cliente.user_id==auth.user_id,fields=fields,csv=False)
         
    return locals()

def righe_in_ddt_cliente_mod():
    
    db.righe_in_ddt_cliente.user_id.default = auth.user_id
    db.righe_in_ddt_cliente.quantita_richiesta.writable=False
    db.righe_in_ddt_cliente.quantita_richiesta.readonly=True
    
    if len(request.args) > 1 and ('edit' in request.args):
         # print "ECCOLO"
         fields = [db.righe_in_ddt_cliente.quantita_richiesta,db.righe_in_ddt_cliente.quantita_prodotta,db.righe_in_ddt_cliente.prezzo]
         form = SQLFORM.grid(db.righe_in_ddt_cliente,fields=fields,csv=False,user_signature=True,args=request.args[:1])
    else:       
    
         fields = [db.righe_in_ddt_cliente.codice_ordine,db.righe_in_ddt_cliente.codice_articolo,db.righe_in_ddt_cliente.n_riga,db.righe_in_ddt_cliente.riferimento_ordine,db.righe_in_ddt_cliente.quantita_richiesta,db.righe_in_ddt_cliente.saldo,db.righe_in_ddt_cliente.quantita_prodotta,db.righe_in_ddt_cliente.prezzo,db.righe_in_ddt_cliente.evasione]
         form = SQLFORM.grid(db.righe_in_ddt_cliente.user_id==auth.user_id,fields=fields,csv=False)
         
         
    return locals()

def righe_in_ddt_fornitore():
    
    db.righe_in_ddt_fornitore.user_id.default = auth.user_id
    fields = [db.righe_in_ddt_fornitore.codice_ordine,db.righe_in_ddt_fornitore.codice_articolo,db.righe_in_ddt_fornitore.n_riga,db.righe_in_ddt_fornitore.riferimento_ordine,db.righe_in_ddt_fornitore.u_m,db.righe_in_ddt_fornitore.quantita,db.righe_in_ddt_fornitore.prezzo,db.righe_in_ddt_fornitore.sconti,db.righe_in_ddt_fornitore.codice_iva,db.righe_in_ddt_fornitore.evasione]
    form = SQLFORM.grid(db.righe_in_ddt_fornitore.user_id == auth.user_id,fields=fields,csv=False)
    return locals()

def aspetto_esteriore_dei_beni():
    form = SQLFORM.grid(db.aspetto_esteriore_dei_beni)
    return locals()

def causali():
    form = SQLFORM.grid(db.causali)
    return locals()

def porto():
    form = SQLFORM.grid(db.porto)
    return locals()

def modifica_ddt():
    
    
    errore = False
    try:
        ddt_id = request.vars.a
        id_cliente = request.vars.b
        
        # print "DDT ID : "+ddt_id
        nome_cliente = db(db.clienti.id==id_cliente).select().first()["nome"]
        
        db(db.righe_in_ddt_cliente.user_id==auth.user_id).delete() 
        
        
        d = db(db.saved_ddt.saved_ddt_id == ddt_id).select().first()
        numero_ddt_corrente = numero_ddt=d["numero_ddt"]
        data_ddt=datetime.datetime.strptime(d["data_inserimento"][0:10],"%Y-%m-%d").date()
        
        data_ddt=data_ddt.strftime("%d/%m/%Y")
        
        righe_form="ok"
        
        
        db(db.righe_in_ddt_cliente).delete()
        # print "SONO QUI"
        
        query=db(db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt_id).select()
        
        for r in query:
            
            
            if "commento" in r.codice_articolo:
                quantita_da_produrre = prenotato = quantita_prodotta = saldo = 0
            
                pass
            
            elif "commento" not in r.codice_articolo:
                # print "prima"
                """
                Vado a vedere la quantità attualmente prodotta salvata nella tabella "produzione_righe_per_ddt"
                """
                # print "RIGA VEFIASDFA"
                # print "ciao"
                if r.id_riga_ordine is None or len(r.id_riga_ordine)<1:
                    # print "riciao"
                    id_riga_ordine=db((db.righe_in_ordine_cliente.id_ordine_cliente == r.id_ordine) & (db.righe_in_ordine_cliente.n_riga ==r.n_riga)).select().first()
                    if id_riga_ordine is not None:
                        id_riga_ordine = id_riga_ordine["id"]
                    else:
                        errore = True
                        # print r
                        msg = "La riga {0} dell'ordine {1} è stata cancellata dalle righe dell'ordine".format(r.n_riga,r.id_ordine)
                        response.flash=msg
                else:
                    # print "provo"
                    id_riga_ordine = r.id_riga_ordine
                    
                # print "ID RIGA ORDINE ",id_riga_ordine
                
                row_id = r.id
                dettagli_produzione_riga = db(db.produzione_righe_per_ddt.id_riga_ordine == id_riga_ordine).select().first()
                dettagli_produzione_riga = db((db.saved_righe_in_ddt_cliente.id_riga_ordine == id_riga_ordine) &  (db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt_id)).select().first()
                # print dettagli_produzione_riga
                if dettagli_produzione_riga is not None:
                    # print "Riga trovata"
                    """
                    Se ho trovato la riga vuol dire che è stata immessa una quantità in saldo.
                    Vado a recuperare la quantità prodotta
                    """
                    # quantita_da_produrre= int(ritorna_quantita_richiesta_da_riga_salvata(id_riga_ordine)) - int(dettagli_produzione_riga.quantita_prodotta)
                    
                    # quantita_da_produrre= int(dettagli_produzione_riga.quantita_prodotta)
                    quantita_da_produrre= int(dettagli_produzione_riga.quantita)
                    
                    # print "quantita da produrre ",quantita_da_produrre
                    quantita_prodotta = dettagli_produzione_riga.quantita
                    
                else:
                    # print "Riga non trovata"
                    """
                    Metto la quantita prodotta = alla quantita richiesta per velocizzare l'inserimento
                    row.quantita è l'iniziale quantita richiesta nell'ordine
                    """
                    # quantita_da_produrre = r.quantita
                    quantita_da_produrre = 0
                    quantita_prodotta = 0
            
            
            
                
            db.righe_in_ddt_cliente.insert(saldo=ritorna_quantita_saldo(id_riga_ordine),user_id = auth.user_id,codice_articolo = r.codice_articolo,descrizione=r.descrizione,riferimento_ordine=r.riferimento_ordine,u_m=r.u_m,prezzo=r.prezzo,sconti=r.sconti,codice_iva=r.codice_iva,n_riga=r.n_riga,evasione=r.evasione,id_ordine=r.id_ordine,codice_ordine=r.codice_ordine,quantita_richiesta=ritorna_quantita_richiesta_da_riga_salvata(id_riga_ordine),quantita_prodotta=quantita_da_produrre,id_riga_ordine=r.id_riga_ordine)
        
        
        # print "SONO QUIkk"
        # print ddt_id
        ordine_id = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt_id).select().first()["id_ordine"]
        # print "SONO QUI2"
        numero_riga_corrente = db(db.righe_in_ordine_cliente.id_ordine_cliente==ordine_id).count()+1
        db.righe_in_ordine_cliente.n_riga.default = numero_riga_corrente
        db.righe_in_ordine_cliente.n_riga.writable = False
        
        db.righe_in_ordine_cliente.id_ordine_cliente.default = ordine_id
        db.righe_in_ordine_cliente.id_ordine_cliente.writable = False
        
        db.righe_in_ordine_cliente.prezzo.default = 0
        # db.righe_in_ordine_cliente.prezzo.writable = False
        # fields=['']
        
        
        cliente = db(db.clienti.id == id_cliente).select().first()
        db.righe_in_ordine_cliente.codice_iva.default=cliente.codice_iva
       
        ddt_id2 = db(db.ddt_cliente.id == ddt_id).select()
        
        links=[lambda row: BUTTON("Aggiungi righe",_onclick=XML('aggiungiRigheMod('+str(row.id)+')'),_class='button btn btn-default')]
        fields=[db.ordine_cliente.ultimo_codice_ordine,db.ordine_cliente.riferimento_ordine_cliente,db.ordine_cliente.data_ordine_cliente]
        query=((db.ordine_cliente.id_cliente== id_cliente) & (db.ordine_cliente.ddt_completato =='F'))
        # query=(db.ordine_cliente.ddt_completato == '0')
        
        righe_in_ordine_cliente_form = SQLFORM.grid(query=query,formname='ordini_clienti_ddt',maxtextlength=100,create=False,editable=True,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,links=links,user_signature=True,args=request.args[:1],fields=fields)
        
        
        
        
        
        luoghi = []
        
        row = db(db.clienti.id == id_cliente).select().first()
        
        error = False
        if row.citta is None:
            response.flash="Il cliente non ha la città in anagrafica\nAggiornare l'anagrafica per poter emettere il DDT"
            error=True
        
        try:
            if len(row.luogo_consegna_1) > 0:
                luoghi.append(row.luogo_consegna_1)
                
            if len(row.luogo_consegna_2) > 0:
                luoghi.append(row.luogo_consegna_2)
            
            if len(row.luogo_consegna_3) > 0:
                luoghi.append(row.luogo_consegna_3)
            
            if len(row.luogo_consegna_4) > 0:
                luoghi.append(row.luogo_consegna_4)
            
            if len(row.luogo_consegna_5) > 0:
                luoghi.append(row.luogo_consegna_5)
                
                
            if len(row.luogo_consegna_6) > 0:
                luoghi.append(row.luogo_consegna_6)
        except:
            luoghi.append("Cliente,,,,,,")
            
        trasporto_a_mezzo = Set()
        trasporto_a_mezzo.add("Mittente")
        trasporto_a_mezzo.add("Destinatario")
        trasporto_a_mezzo.add("Vettore")
        
        aspetto_esteriore_dei_beni = Set()
        rows = db(db.aspetto_esteriore_dei_beni).select()
        for row in rows:
            aspetto_esteriore_dei_beni.add(row.nome)
            
        causali = Set()
        rows = db(db.causali).select()
        for row in rows:
            causali.add(row.nome)
            
            
        porto = Set()
        rows = db(db.porto).select()
        for row in rows:
            porto.add(row.nome)
    except Exception, e:
        # print e
        errore=True;
    
    return locals()


def fatturazione_istantanea_2():
 
    # print request.args
    id_cliente = request.args[0]
    # print request.args[0]
    # print "ID CLIENTE = {0}".format(id_cliente)
    
    nome_cliente =db(db.clienti.id==id_cliente).select().first()["nome"]
   
    
    # print nome_cliente
    form_righe = form = SQLFORM.grid(db.righe_in_fattura_istantanea,formname='mod',maxtextlength=100,create=True,editable=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,user_signature=True,args=request.args[:1])    
    
    new_order = False
    if 'new' in request.args:
        new_order = True
    
    return locals()

def nota_di_accredito_2():
 
    id_cliente = request.args[0]
    # print request.args[0]
    # print "ID CLIENTE = {0}".format(id_cliente)
    
    nome_cliente =db(db.clienti.id==id_cliente).select().first()["nome"]
    if "leonardo" in nome_cliente.lower():
        enti=db(db.enti_leonardo).select()
    else:
        enti=""
    
    # print nome_cliente
    form_righe = form = SQLFORM.grid(db.righe_in_fattura_istantanea,formname='mod',maxtextlength=100,create=True,editable=True,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,user_signature=True,args=request.args[:1])    

    new_order = False
    if 'new' in request.args:
        new_order = True
    return locals()


def mod_ddt_clienti_2():
 
    id_cliente = request.args[0]
    nome_cliente =db(db.clienti.id==id_cliente).select().first()["nome"]    
  
    
    """
    Ritornare i ddt collegati al cliente
    """
    db(db.righe_in_ddt_cliente.user_id == auth.user_id).delete()
    
    fields = [db.ddt_cliente.numero_ddt,db.ddt_cliente.data_richiesta]
    query=((db.ddt_cliente.id_cliente == id_cliente) & (db.ddt_cliente.numero_ddt !="None")) 
    links=[lambda row: A("Modifica",_href=URL('modifica_ddt',vars=dict(a=row.id,b=id_cliente)),_class='button btn btn-default')]
    form = SQLFORM.grid(query=query,formname='mod',maxtextlength=100,create=False,editable=True,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,fields=fields,user_signature=True,args=request.args[:1],links=links)
    # form ="hello"
    return locals()

def mod_ddt_clienti_3():
    id_ddt = request.args[0]
    
    # db(db.righe_in_ddt_cliente.user_id == auth.user_id).delete()
    
    
    ddt_id = db(db.ddt_cliente.id == id_ddt).select().first()
    id_cliente = ddt_id.id_cliente
    nome_cliente = ddt_id.nome_cliente
    
    
    numero_ddt_salvato = db(db.ddt).select().first()["numero_ddt"]
    n = numero_ddt_salvato.split("/")[0]
    a = numero_ddt_salvato.split("/")[1]
    new_n = str(int(n) + 1)
    numero_ddt_corrente = new_n + "/" + a
    
    # print "ID CLIENTE IN DDT2 = ",id_cliente
    
    
    luoghi = []
    
    row = db(db.clienti.id == id_cliente).select().first()
    
    error = False
    if row.citta is None:
        response.flash="Il cliente non ha la città in anagrafica\nAggiornare l'anagrafica per poter emettere il DDT"
        error=True
    
    try:
        if len(row.luogo_consegna_1) > 0:
            luoghi.append(row.luogo_consegna_1)
            
        if len(row.luogo_consegna_2) > 0:
            luoghi.append(row.luogo_consegna_2)
        
        if len(row.luogo_consegna_3) > 0:
            luoghi.append(row.luogo_consegna_3)
        
        if len(row.luogo_consegna_4) > 0:
            luoghi.append(row.luogo_consegna_4)
        
        if len(row.luogo_consegna_5) > 0:
            luoghi.append(row.luogo_consegna_5)
            
        if len(row.luogo_consegna_6) > 0:
            luoghi.append(row.luogo_consegna_6)
    except:
        luoghi.append("Cliente,,,,,,")
        
    trasporto_a_mezzo = Set()
    trasporto_a_mezzo.add("Mittente")
    trasporto_a_mezzo.add("Destinatario")
    trasporto_a_mezzo.add("Vettore")
    
    aspetto_esteriore_dei_beni = Set()
    rows = db(db.aspetto_esteriore_dei_beni).select()
    for row in rows:
        aspetto_esteriore_dei_beni.add(row.nome)
        
    causali = Set()
    rows = db(db.causali).select()
    for row in rows:
        causali.add(row.nome)
        
        
    porto = Set()
    rows = db(db.porto).select()
    for row in rows:
        porto.add(row.nome)
    
    

    ddt_id2 = db(db.ddt_cliente.id == id_ddt).select()
    
    links=[lambda row: BUTTON("Aggiungi righe",_onclick=XML('aggiungiRighe('+str(row.id)+')'),_class='button btn btn-default')]
    fields=[db.ordine_cliente.ultimo_codice_ordine,db.ordine_cliente.riferimento_ordine_cliente,db.ordine_cliente.data_ordine_cliente]
    query=((db.ordine_cliente.id_cliente== id_cliente) & (db.ordine_cliente.ddt_completato =='F'))
    # query=(db.ordine_cliente.ddt_completato == '0')
    
    righe_in_ordine_cliente_form = SQLFORM.grid(query=query,formname='ordini_clienti_ddt',maxtextlength=100,create=False,editable=True,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,links=links,user_signature=True,args=request.args[:1],fields=fields)
    
    
    
    
    return locals()


def ddt_clienti_2():
    id_ddt = request.args[0]
    
    # db(db.righe_in_ddt_cliente.user_id == auth.user_id).delete()
    
    
    ddt_id = db(db.ddt_cliente.id == id_ddt).select().first()
    id_cliente = ddt_id.id_cliente
    nome_cliente = ddt_id.nome_cliente
    
    
    numero_ddt_salvato = db(db.ddt).select().first()["numero_ddt"]
    n = numero_ddt_salvato.split("/")[0]
    a = numero_ddt_salvato.split("/")[1]
    new_n = str(int(n) + 1)
    numero_ddt_corrente = new_n + "/" + a
    
    # print "ID CLIENTE IN DDT2 = ",id_cliente
    
    
    luoghi = []
    
    row = db(db.clienti.id == id_cliente).select().first()
    
    error = False
    if row.citta is None:
        response.flash="Il cliente non ha la città in anagrafica\nAggiornare l'anagrafica per poter emettere il DDT"
        error=True
    
    try:
        if len(row.luogo_consegna_1) > 0:
            luoghi.append(row.luogo_consegna_1)
            
        if len(row.luogo_consegna_2) > 0:
            luoghi.append(row.luogo_consegna_2)
        
        if len(row.luogo_consegna_3) > 0:
            luoghi.append(row.luogo_consegna_3)
        
        if len(row.luogo_consegna_4) > 0:
            luoghi.append(row.luogo_consegna_4)
        
        if len(row.luogo_consegna_5) > 0:
            luoghi.append(row.luogo_consegna_5)
        
        if len(row.luogo_consegna_6) > 0:
            luoghi.append(row.luogo_consegna_6)
    except:
        luoghi.append("Cliente,,,,,,")
    
    
    selected_trasporto = row.trasporto_a_mezzo
    selected_causale = row.causale_trasporto
    selected_porto=row.porto
    selected_vettore=row.vettore
    
    # print selected_causale
    
        
    trasporto_a_mezzo = Set()
    trasporto_a_mezzo.add("Mittente")
    trasporto_a_mezzo.add("Destinatario")
    trasporto_a_mezzo.add("Vettore")
    
    aspetto_esteriore_dei_beni = Set()
    rows = db(db.aspetto_esteriore_dei_beni).select()
    for row in rows:
        aspetto_esteriore_dei_beni.add(row.nome)
        
    causali = Set()
    rows = db(db.causali).select()
    for row in rows:
        causali.add(row.nome)
        
        
    porto = Set()
    rows = db(db.porto).select()
    for row in rows:
        porto.add(row.nome)
    
    

    ddt_id2 = db(db.ddt_cliente.id == id_ddt).select()
    
    links=[lambda row: BUTTON("Aggiungi righe",_onclick=XML('aggiungiRighe('+str(row.id)+')'),_class='button btn btn-default')]
    fields=[db.ordine_cliente.ultimo_codice_ordine,db.ordine_cliente.riferimento_ordine_cliente,db.ordine_cliente.data_ordine_cliente]
    query=((db.ordine_cliente.id_cliente== id_cliente) & (db.ordine_cliente.ddt_completato =='F'))
    # query=(db.ordine_cliente.ddt_completato == '0')
    
    righe_in_ordine_cliente_form = SQLFORM.grid(query=query,formname='ordini_clienti_ddt',maxtextlength=100,create=False,editable=True,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,links=links,user_signature=True,args=request.args[:1],fields=fields)
    
    
    
    
    return locals()

def ddt_fornitori_2():
    id_ddt = request.args[0]
    
    db(db.righe_in_ddt_fornitore.user_id == auth.user_id).delete()
    
    
    ddt_id = db(db.ddt_fornitore.id == id_ddt).select().first()
    id_fornitore = ddt_id.id_fornitore
    nome_fornitore = ddt_id.nome_fornitore
    
    try:
        numero_ddt_salvato = db(db.ddt).select().first()["numero_ddt"]
        n = numero_ddt_salvato.split("/")[0]
        a = numero_ddt_salvato.split("/")[1]
        new_n = str(int(n) + 1)
        numero_ddt_corrente = new_n + "/" + a
    except:
        db.ddt.insert(numero_ddt="0/17")
        numero_ddt_corrente = "1/17"
    
    
    row = db(db.fornitori.id == id_fornitore).select().first()
    
    error = False
    if row.citta is None:
        response.flash="Il fornitore non ha la città in anagrafica\nAggiornare l'anagrafica per poter emettere il DDT"
        error=True
    
    
    luoghi = []
    
   
    
    try:
        if len(row.luogo_consegna_1) is not Null:
            luoghi.append(row.luogo_consegna_1)
        
        if len(row.luogo_consegna_2) is not Null:
            luoghi.append(row.luogo_consegna_2)
    except:
        luoghi.append("Indirizzo fornitore,,,,,")
   
        
       
    trasporto_a_mezzo = Set()
    trasporto_a_mezzo.add("Mittente")
    trasporto_a_mezzo.add("Destinatario")
    trasporto_a_mezzo.add("Vettore")
    
    aspetto_esteriore_dei_beni = Set()
    rows = db(db.aspetto_esteriore_dei_beni).select()
    for row in rows:
        aspetto_esteriore_dei_beni.add(row.nome)
        
    causali = Set()
    rows = db(db.causali).select()
    for row in rows:
        causali.add(row.nome)
        
        
    porto = Set()
    rows = db(db.porto).select()
    for row in rows:
        porto.add(row.nome)

    ddt_id2 = db(db.ddt_cliente.id == id_ddt).select()
    
    links=[lambda row: BUTTON("Aggiungi righe",_onclick=XML('aggiungiRigheFornitore('+str(row.id)+')'),_class='button btn btn-default')]
    fields=[db.ordine_fornitore.ultimo_codice_ordine,db.ordine_fornitore.riferimento_ordine_cliente,db.ordine_fornitore.data_ordine_fornitore]
    query=((db.ordine_fornitore.id_fornitore== id_fornitore) & (db.ordine_fornitore.ddt_completato =='F'))
    # query=(db.ordine_cliente.ddt_completato == '0')
    
    righe_in_ordine_fornitore_form = SQLFORM.grid(query=query,formname='ordini_fornitorii_ddt',maxtextlength=100,create=False,editable=True,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,links=links,user_signature=True,args=request.args[:1],fields=fields)
    
    
    
    
    return locals()





def crea_riba():
    
    current_month = 1
    
    return locals()
    

@service.jsonrpc
@service.jsonrpc2
def ristampa_fattura_da_id(args):
    
    
    
    id_fattura=args['0']
    dati_fattura = db(db.fatture_salvate.id == id_fattura).select().first()
    
    # print dati_fattura
    
    id_cliente = dati_fattura.id_cliente
    
    ddts_id = dati_fattura.id_ddt
    # response.flash = ddts_id
    
    
    numero_fattura_da_salvare = dati_fattura.numero_fattura
     
    """
    Dati cliente
    """
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    
    
    
    fattura = FATTURA("FATTURA DIFFERITA",datetime.datetime.now().date().strftime("%d/%m/%Y"),numero_fattura_da_salvare)
    fattura.intestazione(nome_cliente,citta_cliente,indirizzo_cliente,cap_cliente,provincia_cliente,nazione_cliente,cf_cliente,pi_cliente)
    
    
    fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),"PAGAMENTO","SCADEMZA")
    
    
    
    ddts_id = eval(ddts_id)
    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    
    lista_ddt = []
    for ddt_id in ddts_id:
        
        
        lista_ddt.append(ddt_id)
        
        rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt_id).select()
        # print "DDT ID : ",ddt_id
        for row in rows:
            
            
            id_ordine = row.id_ordine
            try:
                  pagamento = db(db.ordine_cliente.id == id_ordine).select().first()["pagamento"]
                  # print "pagamento = ",pagamento
                  if pagamento is None:
                        pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                        
                  giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                  scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                  scadenza = scadenza.strftime("%d/%m/%Y")
                  fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(dettagli_banca.iban),pagamento,str(scadenza))
            except:
                  response.flash="Controllare il tipo di pagamento in anagrafica"
                  return locals()
            
            # print "Aggiunta rig"
            sconti = row.sconti
            if row.sconti is None:
                
                sconti=""
            
            importo = saved_importo = float(row.quantita) * float(row.prezzo)
            importo = Money(str(importo),"EUR")
            importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
            prezzo = str(row.prezzo).replace(".",",")
            
            codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
            percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]
            
            importo_totale +=saved_importo
            imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
            
            if not codice_iva in lista_codici_iva:
                lista_codici_iva[codice_iva] = saved_importo
            else:
                lista_codici_iva[codice_iva] += saved_importo
            
            fattura.add_row(row.codice_articolo,row.descrizione,row.riferimento_ordine,row.u_m,row.quantita,prezzo,sconti,importo,codice_iva)
        
    
    
    # print lista_codici_iva
    
    
    
    bollo_presente = False
    bollo = 0
    for k,v in lista_codici_iva.iteritems():
        codice_iva = k
        importo_netto = v
        # print "LISTA CODICI : ",codice_iva,importo_netto
        dettaglio_iva = db(db.anagrafica_codici_iva.codice_iva == codice_iva).select().first()
        percentuale_iva = dettaglio_iva.percentuale_iva
        descrizione_iva = dettaglio_iva.descrizione_codice_iva
        imposta_iva = return_imposta(v,percentuale_iva)
        if dettaglio_iva.bollo_su_importi_esenti is True:
            if not bollo_presente:
                bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
                bollo_presente = True
                
        fattura.footer_2(codice_iva,"",return_currency(importo_netto),descrizione_iva,return_currency(imposta_iva),return_currency(bollo))
        bollo = 0
                
                
    if bollo_presente:
        bollo = db(db.bolli.descrizione=="Fattura").select().first()["valore"]
        importo_totale += float(bollo)
     
    importo_totale_da_salvare = importo_totale +imposta_iva
    
    
              
    importo_totale = Money(str(importo_totale),"EUR")
    importo_totale = importo_totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    
    fattura.footer(str(importo_totale)," "," "," "," ",str(importo_totale),str(return_currency(imposta_totale)))    
    fattura.totale(str(importo_totale_da_salvare))
    
    # db.fatture_salvate.insert(nome_cliente=nome_cliente,data_fattura = datetime.datetime.now().strftime("%d/%m/%Y"),numero_fattura = numero_fattura_da_salvare,id_cliente=id_cliente,id_ddt = lista_ddt,totale = importo_totale_da_salvare)     
        
        
    
   
    
   
    fattura.insert_rows()
    fattura.create_pdf()
    

def ristampa_fattura():
      
    links=[lambda row: BUTTON("Ristampa",_onclick=XML('ristampaFattura('+str(row.id)+')'),_class='button btn btn-default')]
    fields=[db.fatture_salvate.data_fattura,db.fatture_salvate.numero_fattura,db.fatture_salvate.nome_cliente,db.fatture_salvate.totale]
    fatture_da_ristampare = SQLFORM.grid(db.fatture_salvate,formname='fatture_salvate',maxtextlength=100,create=False,editable=False,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,links=links,fields=fields)
    return locals()

def fatturazione_differita_2():
    id_fattura = request.args[0]
    
    fattura = db(db.fattura_cliente.id == id_fattura).select().first()
    id_cliente = fattura.id_cliente
    dal = fattura.dal
    al_fixed = fattura.al
    al = fattura.al + datetime.timedelta(days=2)
    nome_cliente = fattura.nome_cliente
    
    
    """
    """
        
    # print "ID CLIENTE IN FATTURA DIFFERITA = ",id_cliente
    
    """
    Select all ddts of the selected client.
    """
    # print fattura.dal,al
    ddts_id = ((db.ddt_cliente.id_cliente == id_cliente) & (db.ddt_cliente.data_richiesta >= fattura.dal) & (db.ddt_cliente.data_richiesta <= al) & (db.ddt_cliente.fattura_emessa == 'F') & (db.ddt_cliente.numero_ddt != 'None'))
    # ddts_id = ((db.ddt_cliente.id_cliente == id_cliente) & (db.ddt_cliente.data_richiesta >= fattura.dal) & (db.ddt_cliente.data_richiesta <= al) & (db.ddt_cliente.numero_ddt != 'None'))
    

    
    links=[lambda row: BUTTON("Aggiungi DDT",_onclick=XML('aggiungiDDT('+str(row.id)+')'),_class='button btn btn-default')]
    db.ddt_cliente.totale = Field.Virtual("Totale", lambda row: calcola_totale_iva_inclusa_da_ddt(row.ddt_cliente.id))
    # db.ddt_cliente.totale = Field.Virtual("Totale", lambda row: 0)
    fields=[db.ddt_cliente.data_richiesta,db.ddt_cliente.numero_ddt,db.ddt_cliente.totale]
    # query=((db.ordine_cliente.id_cliente== id_cliente) & (db.ordine_cliente.ddt_completato =='F'))
    # query=(db.ordine_cliente.ddt_completato == '0')
    print "---------------"
    ddt_da_fatturare = SQLFORM.grid(query=ddts_id,formname='ordini_clienti_ddt',maxtextlength=100,create=False,editable=False,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,links=links,user_signature=True,args=request.args[:1],fields=fields)
    
   
    
    return locals()

def calcola_totale_per_mese_da_ddt_cliente():
    current_month = 1
    return locals()

def calcola_totale_per_anno():
	current_year=2018
	return locals()

def calcola_totale_per_anno_data():
	
	lista=[]
	riga=[]
	riga.append("Cliente")
	riga.append("Totale")
	lista.append(riga)
    
	try:
		year = int(request.vars['y'])
	except:
		year = datetime.datetime.now().year
	  
		
	# day_start,day_end = monthrange(datetime.datetime.now().year, month)
	# day_start = 1
	
	# st = str(day_start)+"/"+str(month)+"/"+str(datetime.datetime.now().year)
	start_date = datetime.datetime(year,1,1)
	end_date = datetime.datetime(year,12,31).date()
	# print start_date,end_date
	
	   
	

	rows1= db(db.clienti).select()
	
	db(db.totali_ddt_mese_).delete()
	db.totali_ddt_mese_.id.readable=False;
	
	totalissimo=0
	nome_cliente=""
	for r1 in rows1:
		
		try:
			riga=[]
			totale = 0
			ddts = db((db.ddt_cliente.id_cliente == r1.id) & (db.ddt_cliente.data_richiesta >= start_date) & (db.ddt_cliente.data_richiesta <= end_date) & (db.ddt_cliente.numero_ddt != 'None')).select()
			
			
		   
			
			
			
			for ddt in ddts:
						  
			   
				nome_cliente = ddt.nome_cliente
				# print "NOME CLIENTE = ",nome_cliente,ddt.id
				totale += ritorna_int_calcola_totale_iva_esclusa_da_ddt(ddt.id)
			if totale > 0:	
				riga.append(nome_cliente)
				riga.append(totale)
				lista.append(riga)
				db.totali_ddt_mese_.insert(cliente=nome_cliente,totale=ritorna_prezzo_europeo(totale))
				totalissimo +=totale
		except Exception,e:
			# print "ECCEZZIONE ",e
			pass
			
	# print lista
	form = SQLFORM.grid(db.totali_ddt_mese_,deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,user_signature=True,args=request.args[:1])
	return dict(lista=json.dumps(lista),form=form,totalissimo = ritorna_prezzo_europeo(totalissimo))
	
	
	
	return locals()

def calcola_totale_per_anno_leonardo():
	current_year=1
	return locals()

def calcola_totale_per_anno_leonardo_data():
    
    
    lista=[]
    
    riga=[]
    riga.append("Cliente")
    riga.append("Totale")
    lista.append(riga)
    
    
    form=""
    totalissimo=1000
    
    
    try:
        year = int(request.vars['y'])
    except:
        year = datetime.datetime.now().year
      
        
    # day_start,day_end = monthrange(datetime.datetime.now().year, month)
    day_start = 1
    
    st = str(day_start)+"/"+str(1)+"/"+str(year)
    start_date = datetime.datetime(year,1,day_start)
    end_date = datetime.datetime(year,12,31).date() + timedelta(days=1)
    # print start_date,end_date
    
    # return dict(lista=json.dumps(lista),form=form,totalissimo = ritorna_prezzo_europeo(totalissimo))   
    

    rows1= db(db.clienti.id==41).select()
    
    db(db.totali_ddt_anno_).delete()
    db.totali_ddt_anno_.id.readable=False;
    
    totalissimo=0
    nome_cliente=""
    for r1 in rows1:
        
        try:
            riga=[]
            totale = 0
            dest1 = db((db.ddt_cliente.id_cliente == r1.id) & (db.ddt_cliente.data_richiesta >= start_date) & (db.ddt_cliente.data_richiesta <= end_date) & (db.ddt_cliente.numero_ddt != 'None') & (db.ddt_cliente.consegna.contains('CHIETI'))).select()
            dest2 = db((db.ddt_cliente.id_cliente == r1.id) & (db.ddt_cliente.data_richiesta >= start_date) & (db.ddt_cliente.data_richiesta <= end_date) & (db.ddt_cliente.numero_ddt != 'None') & (db.ddt_cliente.consegna.contains('BISENZIO'))).select()
            dest3 = db((db.ddt_cliente.id_cliente == r1.id) & (db.ddt_cliente.data_richiesta >= start_date) & (db.ddt_cliente.data_richiesta <= end_date) & (db.ddt_cliente.numero_ddt != 'None') & (db.ddt_cliente.consegna.contains('BAINSIZZA'))).select()
            dest4 = db((db.ddt_cliente.id_cliente == r1.id) & (db.ddt_cliente.data_richiesta >= start_date) & (db.ddt_cliente.data_richiesta <= end_date) & (db.ddt_cliente.numero_ddt != 'None') & (db.ddt_cliente.consegna.contains('NERVIANO'))).select()
            dest5 = db((db.ddt_cliente.id_cliente == r1.id) & (db.ddt_cliente.data_richiesta >= start_date) & (db.ddt_cliente.data_richiesta <= end_date) & (db.ddt_cliente.numero_ddt != 'None') & (db.ddt_cliente.consegna.contains('ADRIATICA'))).select()
            
            riga=[]
            totale=0
            for ddt in dest1:
                totale += ritorna_int_calcola_totale_iva_esclusa_da_ddt(ddt.id)
            if totale > 0:    
                consegna='CHIETI'
                riga.append(consegna)
                riga.append(totale)
                lista.append(riga)
                db.totali_ddt_anno_.insert(destinazione=consegna,totale=ritorna_prezzo_europeo(totale))
                totalissimo +=totale
            
            riga=[]
            totale=0
            for ddt in dest2:
                totale += ritorna_int_calcola_totale_iva_esclusa_da_ddt(ddt.id)
            if totale > 0:    
                consegna='CAMPI BISENZIO'
                riga.append(consegna)
                riga.append(totale)
                lista.append(riga)
                db.totali_ddt_anno_.insert(destinazione=consegna,totale=ritorna_prezzo_europeo(totale))
                totalissimo +=totale
            
            riga=[]
            totale=0                
            for ddt in dest3:
                totale += ritorna_int_calcola_totale_iva_esclusa_da_ddt(ddt.id)
            if totale > 0:    
                consegna='BORGO BAINSIZZA'
                riga.append(consegna)
                riga.append(totale)
                lista.append(riga)
                db.totali_ddt_anno_.insert(destinazione=consegna,totale=ritorna_prezzo_europeo(totale))
                totalissimo +=totale
            
            riga=[]
            totale=0
            for ddt in dest4:
                totale += ritorna_int_calcola_totale_iva_esclusa_da_ddt(ddt.id)
            if totale > 0:    
                consegna='NERVIANO'
                riga.append(consegna)
                riga.append(totale)
                lista.append(riga)
                db.totali_ddt_anno_.insert(destinazione=consegna,totale=ritorna_prezzo_europeo(totale))
                totalissimo +=totale
            
            riga=[]
            totale=0
            for ddt in dest5:
                totale += ritorna_int_calcola_totale_iva_esclusa_da_ddt(ddt.id)
            if totale > 0:    
                consegna='FOCACCIA GROUP SRL'
                riga.append(consegna)
                riga.append(totale)
                lista.append(riga)
                db.totali_ddt_anno_.insert(destinazione=consegna,totale=ritorna_prezzo_europeo(totale))
                totalissimo +=totale
                
            
        except Exception,e:
            # print "ECCEZZIONE ",e
            pass
            
    # print lista
    form = SQLFORM.grid(db.totali_ddt_anno_,deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,user_signature=True,args=request.args[:1])
    return dict(lista=json.dumps(lista),form=form,totalissimo = ritorna_prezzo_europeo(totalissimo))


def calcola_totale_per_mese_da_ddt_cliente_data():
    
    
    lista=[]
    
    riga=[]
    riga.append("Cliente")
    riga.append("Totale")
    lista.append(riga)
    
    try:
        month = int(request.vars['m'])
    except:
        month = datetime.datetime.now().month
      
        
    day_start,day_end = monthrange(datetime.datetime.now().year, month)
    day_start = 1
    
    st = str(day_start)+"/"+str(month)+"/"+str(datetime.datetime.now().year)
    start_date = datetime.datetime(datetime.datetime.now().year,month,day_start)
    end_date = datetime.datetime(datetime.datetime.now().year,month,day_end).date() + timedelta(days=1)
    # print start_date,end_date
    
       
    

    rows1= db(db.clienti).select()
    
    db(db.totali_ddt_mese_).delete()
    db.totali_ddt_mese_.id.readable=False;
    
    totalissimo=0
    nome_cliente=""
    for r1 in rows1:
        
        try:
            riga=[]
            totale = 0
            ddts = db((db.ddt_cliente.id_cliente == r1.id) & (db.ddt_cliente.data_richiesta >= start_date) & (db.ddt_cliente.data_richiesta <= end_date) & (db.ddt_cliente.numero_ddt != 'None')).select()
            
            
           
            
            
            
            for ddt in ddts:
                          
               
                nome_cliente = ddt.nome_cliente
                # print "NOME CLIENTE = ",nome_cliente,ddt.id
                totale += ritorna_int_calcola_totale_iva_esclusa_da_ddt(ddt.id)
            if totale > 0:    
                riga.append(nome_cliente)
                riga.append(totale)
                lista.append(riga)
                db.totali_ddt_mese_.insert(cliente=nome_cliente,totale=ritorna_prezzo_europeo(totale))
                totalissimo +=totale
        except Exception,e:
            # print "ECCEZZIONE ",e
            pass
            
    # print lista
    form = SQLFORM.grid(db.totali_ddt_mese_,deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,user_signature=True,args=request.args[:1])
    return dict(lista=json.dumps(lista),form=form,totalissimo = ritorna_prezzo_europeo(totalissimo))
    
    
    
def ritorna_prezzo_europeo(importo):
    importo = Money(str(importo),"EUR")
    importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
    return importo


def ritorna_int_calcola_totale_iva_esclusa_da_ddt(id_ddt):
    
        rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == id_ddt).select()
        # print "DDT ID : ",id_ddt
        totale = 0
        importo_totale = 0
        imposta_totale = 0
        
        for row in rows:
            if not "commento" in row.codice_articolo:             
                id_ordine = row.id_ordine
                try:
                      importo = saved_importo = float(row.quantita) * float(row.prezzo)
                      importo = Money(str(importo),"EUR")
                      importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                      prezzo = str(row.prezzo).replace(".",",")
                      
                      # codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                      # percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]
                      
                      importo_totale += saved_importo
                      # imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                except:
                      pass
                       
            
         
        
    
    
        totale = importo_totale+imposta_totale
       
        # print "DDT NUMERO : {0} TOTALE {1}".format(id_ddt,totale)
        
        return totale    

def ritorna_int_calcola_totale_iva_inclusa_da_ddt(id_ddt):
    
        rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == id_ddt).select()
        # print "DDT ID : ",id_ddt
        totale = 0
        importo_totale = 0
        imposta_totale = 0
        
        for row in rows:
            if not "commento" in row.codice_articolo:             
                id_ordine = row.id_ordine
                try:
                      importo = saved_importo = float(row.quantita) * float(row.prezzo)
                      importo = Money(str(importo),"EUR")
                      importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                      prezzo = str(row.prezzo).replace(".",",")
                      
                      codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                      percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]
                      
                      importo_totale += saved_importo
                      imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
                except:
                      pass
                       
            
         
        
    
    
        totale = importo_totale+imposta_totale
       
        # print "DDT NUMERO : {0} TOTALE {1}".format(id_ddt,totale)
        
        return totale
        
        

def calcola_totale_iva_inclusa_da_ddt(id_ddt):

        print "Dentro qui"
        print "DDT ID : ",id_ddt
        rows = db((db.saved_righe_in_ddt_cliente.saved_ddt_id == id_ddt) & (db.saved_righe_in_ddt_cliente.codice_articolo !="commento")).select()
        print "DDT ID : ",id_ddt
        totale = 0
        importo_totale = 0
        imposta_totale = 0
        print "sono qui"
        for row in rows:
                        
            id_ordine = row.id_ordine
            try:
                importo = saved_importo = float(row.quantita) * float(row.prezzo)
                importo = Money(str(importo),"EUR")
                importo = importo.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                prezzo = str(row.prezzo).replace(".",",")
                
                codice_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["codice_iva"]
                percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == row.codice_iva).select().first()["percentuale_iva"]
            
                    
                importo_totale += saved_importo
                imposta_totale += return_imposta(saved_importo,int(percentuale_iva))
            except Exception,e:
                print e
                pass
                
            
         
        
    
    
        totale = importo_totale+imposta_totale
        totale = Money(str(totale),"EUR")
        totale = totale.format("it_IT").encode('ascii', 'ignore').decode('ascii')
        print "Totale calcolato = ",totale
        return totale
        

def fatturazione_differita():
    fields = ['nome_cliente','dal','al']
    cliente_form = SQLFORM(db.fattura_cliente,formname='cliente_form',formstyle = 'table3cols',fields=fields)
    
    if cliente_form.process().accepted:
        id_cliente = db(db.clienti.nome == cliente_form.vars.nome_cliente).select().first()
        # print "ID CLIENTE = ",id_cliente
        db(db.ddt_da_fatturare.user_id == auth.user_id).delete()
        row = db(db.fattura_cliente.id == cliente_form.vars.id).select().first()
        row.update_record(id_cliente = id_cliente.id)
        redirect(URL('fatturazione_differita_2',args=cliente_form.vars.id))
    
    return locals()


def fatturazione_istantanea():
    
    fields = ['nome_cliente']
    cliente_form = SQLFORM(db.ddt_cliente,formname='cliente_form',formstyle = 'table3cols',fields=fields)
    
    if cliente_form.process().accepted:
        id_cliente = db(db.clienti.nome == cliente_form.vars.nome_cliente).select().first()
        # print "ID CLIENTE = ",id_cliente
        # print cliente_form.vars.id #LAST IMSERTED ID
        
        row = db(db.ddt_cliente.id == cliente_form.vars.id).select().first()
        # print "SELECTED ROW : ",row
        row.update_record(id_cliente = id_cliente.id)
        db(db.righe_in_fattura_istantanea).delete()
        redirect(URL('fatturazione_istantanea_2',args=id_cliente.id))
    
    return locals()

def nota_di_accredito():
    
    fields = ['nome_cliente']
    cliente_form = SQLFORM(db.ddt_cliente,formname='cliente_form',formstyle = 'table3cols',fields=fields)
    
    if cliente_form.process().accepted:
        id_cliente = db(db.clienti.nome == cliente_form.vars.nome_cliente).select().first()
        # print "ID CLIENTE = ",id_cliente
        # print cliente_form.vars.id #LAST IMSERTED ID
        
        row = db(db.ddt_cliente.id == cliente_form.vars.id).select().first()
        # print "SELECTED ROW : ",row
        row.update_record(id_cliente = id_cliente.id)
        db(db.righe_in_fattura_istantanea).delete()
        redirect(URL('nota_di_accredito_2',args=id_cliente.id))
        
    return locals()

def ddt_clienti():
    
    fields = ['nome_cliente']
    cliente_form = SQLFORM(db.ddt_cliente,formname='cliente_form',formstyle = 'table3cols',fields=fields)
    
    if cliente_form.process().accepted:
        id_cliente = db(db.clienti.nome == cliente_form.vars.nome_cliente).select().first()
        # print "ID CLIENTE = ",id_cliente
        # print cliente_form.vars.id #LAST IMSERTED ID
        
        row = db(db.ddt_cliente.id == cliente_form.vars.id).select().first()
        # print "SELECTED ROW : ",row
        row.update_record(id_cliente = id_cliente.id)
        db(db.righe_in_ddt_cliente.user_id == auth.user_id).delete()
        redirect(URL('ddt_clienti_2',args=cliente_form.vars.id))
    
    return locals()
    
def mod_ddt_clienti():
    
    fields = ['nome_cliente']
    cliente_form = SQLFORM(db.ddt_cliente,formname='cliente_form_mod',formstyle = 'table3cols',fields=fields)
    
    if cliente_form.process().accepted:
        id_cliente = db(db.clienti.nome == cliente_form.vars.nome_cliente).select().first()
        # print "ID CLIENTE = ",id_cliente
        # print cliente_form.vars.id #LAST IMSERTED ID
        
        row = db(db.ddt_cliente.id == cliente_form.vars.id).select().first()
        # print "SELECTED ROW : ",row
        # row.update_record(id_cliente = id_cliente.id)
        # db(db.righe_in_ddt_cliente.user_id == auth.user_id).delete()
        redirect(URL('mod_ddt_clienti_2',args=id_cliente.id))
    
    return locals()

def ddt_fornitori():
    
    fields = ['nome_fornitore']
    
    fornitore_form = SQLFORM(db.ddt_fornitore,formname='fornitore_form',formstyle = 'table3cols',fields=fields)
    
    if fornitore_form.process().accepted:
        # print fornitore_form.vars.nome_fornitore
        id_fornitore = db(db.fornitori.nome == fornitore_form.vars.nome_fornitore).select().first()
       
        
        row = db(db.ddt_fornitore.id == fornitore_form.vars.id).select().first()
        # print "SELECTED ROW : ",row
        row.update_record(id_fornitore = id_fornitore.id)
        redirect(URL('ddt_fornitori_2',args=fornitore_form.vars.id))
    
    return locals()

def ddt_clienti_old():
    
    links=[lambda row: A(XML('Crea bolla'),_class='button btn btn-default',_href=URL('dettaglio_bolla',args=row.id))]
    fields=[db.righe_in_ordine_cliente.n_riga,db.righe_in_ordine_cliente.codice_articolo,db.righe_in_ordine_cliente.quantita,db.righe_in_ordine_cliente.prezzo,db.righe_in_ordine_cliente.sconti,db.righe_in_ordine_cliente.codice_iva,db.righe_in_ordine_cliente.evasione]
    righe_in_ordine_cliente_form = SQLFORM.grid(db.ordine_cliente,formname='ordini_clienti',maxtextlength=100,create=False,editable=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,links=links)
    
    return dict(righe_in_ordine_cliente_form=righe_in_ordine_cliente_form)

def gestione_piano_dei_conti():
  
    
    return dict(message="ok")

def anagrafica_codici_iva():
    codici_iva_form = SQLFORM.grid(db.anagrafica_codici_iva,formname='codici_iva',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,exportclasses=export_classes)
    codici_iva_form.element('.web2py_counter', replace=None)

    return dict(codici_iva_form = codici_iva_form)

def anagrafica_banche():
    anagrafica_banche_form = SQLFORM.grid(db.anagrafica_banche,formname='anagrafica_banche_form',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,exportclasses=export_classes)
    anagrafica_banche_form.element('.web2py_counter', replace=None)
    try:
        anagrafica_banche_form.element('input[name=descrizione_sottoconto]')['_style'] = 'width:350px;height:25px;'
        anagrafica_banche_form.element('input[name=descrizione]')['_style'] = 'width:350px;height:25px;'
    except:
        pass
    return dict(anagrafica_banche_form = anagrafica_banche_form)

def anagrafica_banche_azienda():
    anagrafica_banche_form = SQLFORM.grid(db.anagrafica_banche_azienda,formname='anagrafica_banche_form',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True)
    anagrafica_banche_form.element('.web2py_counter', replace=None)
    try:
        anagrafica_banche_form.element('input[name=descrizione_sottoconto]')['_style'] = 'width:350px;height:25px;'
        anagrafica_banche_form.element('input[name=descrizione]')['_style'] = 'width:350px;height:25px;'
    except:
        pass
    return dict(anagrafica_banche_form = anagrafica_banche_form)    

def fatture_form():
    fields = [db.fatture_salvate.data_fattura,db.fatture_salvate.numero_fattura,db.fatture_salvate.totale,db.fatture_salvate.nome_cliente,db.fatture_salvate.scadenza]
    
    """Patch per sistemare la data
      
    
    """
    x = datetime.datetime(1999, 5, 17)
    fatture=db(db.fatture_salvate.scadenza > x).select()
    
    for fattura in fatture:
    	original_start_date = fattura.data_fattura
    	if original_start_date is not None:
    	 	
    	 	day_start,day_end = monthrange(original_start_date.year, original_start_date.month)
       		d = str(day_end)+"/"+str(original_start_date.month)+"/"+str(original_start_date.year)
    
      		start_date = datetime.datetime.strptime(d,"%d/%m/%Y")
      		# print original_start_date,start_date
      		fattura.data_fattura = start_date
      		fattura.update_record()
    
    
    if len(request.args) > 1 and ('edit' in request.args):
        db.fatture_salvate.numero_fattura.writable=False
        db.fatture_salvate.id_ddt.writable=False
        db.fatture_salvate.id_ddt.readable=False
        
        db.fatture_salvate.id_cliente.writable=False
        db.fatture_salvate.id_cliente.readable=False
        
        db.fatture_salvate.id_cliente.writable=False
        db.fatture_salvate.id_cliente.readable=False
        
        db.fatture_salvate.richiede_riba.writable=False
        db.fatture_salvate.richiede_riba.readable=False
        
        
        db.fatture_salvate.riba_emessa.writable=False
        db.fatture_salvate.riba_emessa.readable=False
        
    
    links=[lambda row: BUTTON("Aggiungi fattura",_onclick=XML('aggiungiFattura('+str(row.id)+')'),_class='button btn btn-default')]
        
    fatture_form = SQLFORM.grid(db.fatture_salvate.richiede_riba=='T',formname='fatture',maxtextlength=100,create=False,     deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,fields=fields,links=links,exportclasses=export_classes)   
        
    
   
    
    
    return locals()

@service.jsonrpc
@service.jsonrpc2
def successivo_riba(banca):
    
    if db(db.fatture_scelte).isempty():
        response.flash="Selezionare almeno una fattura"
        return 1/0
    
    
    db(db.temp_banca).delete()
    db.temp_banca.insert(banca=banca)
    
    return "ok"


@service.jsonrpc
@service.jsonrpc2
def accorpa(id,val):
    d=db(db.fatture_scelte.id == id).select().first()
    if "True" in str(val):
        d.update_record(accorpa=True)
    else:
         d.update_record(accorpa=False)
    
    
    return "ok"





def crea_indici_riba():
    """
    Formato : id_cliente,lista(id_fatture)
    """
    
    cliente = []
    lista_riba=[]
    
    fatture_accorpate = []
    fatture=db(db.fatture_scelte).select()
    
    for f in fatture:
        id_cliente = f.id_cliente
        
        fatture_accorpate = []
        lista_fatture = []
        if db((db.fatture_scelte.id_cliente == id_cliente) & (db.fatture_scelte.accorpa == 'T')).count() < 2:
            """
            Nessuna fattura da accorpare per questo cliente
            """
            lista_fatture.append(f.id_fattura)
            pass
        else:
            da_accorpare = db((db.fatture_scelte.id_cliente == id_cliente) & (db.fatture_scelte.accorpa == 'T')).select()
            for item in da_accorpare:
                if not item in lista_fatture:
                    
                    lista_fatture.append(item.id_fattura)
    
        cliente = []
        cliente.append(id_cliente)
        cliente.append(lista_fatture)
        if not cliente in lista_riba:
            lista_riba.append(cliente)
            
    return lista_riba

def ritorna_dettaglio_fattura(id_fattura):
    fattura = db(db.fatture_salvate.id ==id_fattura).select().first()
    
    msg = "Fattura numero "+fattura.numero_fattura +" Del " + fattura.data_fattura.strftime("%d/%m/%Y")+ " Tot. " + ritorna_prezzo_europeo(fattura.totale) + " <b>Scadenza</b> "+fattura.scadenza.strftime("%d/%m/%Y")
    return msg

def ritorna_nome_cliente_da_id(id):
    return db(db.clienti.id==id).select().first().nome


def ritorna_abi_nostra_banca_scelta():
    
    banca_scelta = db(db.temp_banca).select().first().banca
    return  db(db.anagrafica_banche_azienda.descrizione == banca_scelta).select().first().codice_abi

def ritorna_cab_nostra_banca_scelta():
    
    banca_scelta = db(db.temp_banca).select().first().banca
    return  db(db.anagrafica_banche_azienda.descrizione == banca_scelta).select().first().codice_cab

def ritorna_scadenza_e_totale_fattura_per_riba(id_fattura):
    d = db(db.fatture_salvate.id == id_fattura).select().first()
    scadenza = d.scadenza.strftime("%d%m%y")
    totale = d.totale
    # print "TOT : ".format(totale)
    return scadenza,totale


def ritorna_abi_cab_da_cliente_id(cliente_id):

    # print cliente_id
    codice_banca = db(db.clienti.id == cliente_id).select().first().codice_banca
    
    codice_abi=""
    codice_cab=""
    try:
	    d= db(db.anagrafica_banche.descrizione == codice_banca).select().first()
	    codice_abi=d.codice_abi
	    codice_cab=d.codice_cab
    except:
          pass
    
    return d.codice_abi,d.codice_cab
    
    
def truncate_float(number, length):
    """Truncate float numbers, up to the number specified
    in length that must be an integer"""

    number = number * pow(10, length)
    number = int(number)
    number = float(number)
    number /= pow(10, length)
    return number
    
def crea_file_riba():
    
    """Numero Univoco per ogni file riba creato?"""
    try:
        numero_disposizione = db(db.numero_disposizioni_riba).select().first().numero
        numero_disposizione = int(numero_disposizione)
    except:
        numero_disposizione = 1
    
    """Contenitore per il flusso CBI"""
    
    flow = wrapper.Flow()
    flow.header = wrapper.Record('IB')
    flow.footer = wrapper.Record('EF')
    
    
    
    codice_assegnato_dalla_sia_alla_azienda_emittente ="60I33"
    codice_abi_banca_assuntrice = ritorna_abi_nostra_banca_scelta()
    codice_cab_banca_assuntrice = ritorna_cab_nostra_banca_scelta()
    data_creazione = datetime.datetime.now().date().strftime("%d/%m/%y").replace("/","")
    nome_supporto = "OpenGest"
    codice_divisa = "E"
    
    flow.header['mittente'] = codice_assegnato_dalla_sia_alla_azienda_emittente
    flow.header['ricevente'] = codice_abi_banca_assuntrice
    flow.header['data_creazione'] = data_creazione
    flow.header['nome_supporto'] = nome_supporto
    flow.header['codice_divisa'] = codice_divisa
    
    flow.footer['mittente']=codice_assegnato_dalla_sia_alla_azienda_emittente
    flow.footer['ricevente']=codice_abi_banca_assuntrice
    flow.footer['data_creazione']=data_creazione
    flow.footer['nome_supporto']=nome_supporto
    flow.footer['codice_divisa']=codice_divisa
    
    numero_emissioni = crea_indici_riba()
    # print "NUMERO EMISSIONI = {0} ".format(len(numero_emissioni))
    flow.footer['numero_disposizioni']=str(len(numero_emissioni)).zfill(7)
    
    
    totalissimo = 0
    flow.disposals = []
    for numero_progressivo in range(1,len(numero_emissioni) +1):
        """Contiene tutti e 7 i record"""
        disposizione = wrapper.Disposal()
        
        # print "QUI"
        """instanza ai vari record cbi"""
        first_record = wrapper.Record('14')
        second_record = wrapper.Record('20')
        third_record = wrapper.Record('30')
        fourth_record = wrapper.Record('40')
        fifth_record = wrapper.Record('50')
        fifty_one = wrapper.Record('51')
        seventieth_record = wrapper.Record('70')
         
         
        emissione_corrente = numero_emissioni[numero_progressivo - 1]
        cliente_id = emissione_corrente[0]
        fatture = emissione_corrente[1]
        """
        Raccolta dati per il record 14 first_record
        """
        codice_abi_domiciliaria,codice_cab_domiciliaria=ritorna_abi_cab_da_cliente_id(cliente_id)
        codice_cliente_debitore = cliente_id
        # print ritorna_abi_cab_da_cliente_id
                                
                        
        importo_della_ricevuta_in_centesimi = 0
        riferimento_fattura = ""
        for id_fattura in fatture:
            data_pagamento,totale = ritorna_scadenza_e_totale_fattura_per_riba(id_fattura)
            
            importo_della_ricevuta_in_centesimi += float(totale)
            totalissimo += importo_della_ricevuta_in_centesimi
            
            riferimento_fattura+= db(db.fatture_salvate.id == id_fattura).select().first().numero_fattura+" del "+db(db.fatture_salvate.id == id_fattura).select().first().data_fattura.strftime("%d/%m/%Y") + " "
        
        importo_della_ricevuta_in_centesimi = '%.2f' % round(importo_della_ricevuta_in_centesimi,2)
        
        importo_della_ricevuta_in_centesimi = importo_della_ricevuta_in_centesimi.replace(".","").zfill(13)
        
        # print "importo : {0}".format(importo_della_ricevuta_in_centesimi)
        first_record['numero_progressivo']=str(numero_progressivo).zfill(7)
        first_record['data_pagamento']=data_pagamento
        first_record['importo']=str(importo_della_ricevuta_in_centesimi)
        first_record['codice_abi_banca']=codice_abi_banca_assuntrice
        first_record['cab_banca']=codice_cab_banca_assuntrice
        first_record['codice_abi_domiciliaria']=codice_abi_domiciliaria
        first_record['codice_cab_domiciliaria']=codice_cab_domiciliaria
        first_record['codice_azienda']=codice_assegnato_dalla_sia_alla_azienda_emittente
        first_record['codice_cliente_debitore']=codice_cliente_debitore
        first_record['codice_divisa']=codice_divisa
        first_record['causale']="30000"
        first_record['segno']="-"
        first_record['tipo_codice']="4"
           
        
        
        second_record['numero_progressivo']=str(numero_progressivo).zfill(7)
        second_record['1_segmento']="Microcarp"
        second_record['2_segmento']="Strada statale 416"
        second_record['3_segmento']="26020 Castelleone (CR)"
        second_record['4_segmento']="Italia"
        
        dati_cliente = db(db.clienti.id == cliente_id).select().first()
        
        third_record['numero_progressivo'] = str(numero_progressivo).zfill(7)
        third_record['codice_fiscale_cliente'] = dati_cliente.codice_fiscale
        third_record['1_segmento'] = dati_cliente.nome[:27]
        third_record['2_segmento'] = ""
        
        fourth_record['numero_progressivo'] = str(numero_progressivo).zfill(7)
        fourth_record['indirizzo'] = dati_cliente.indirizzo
        fourth_record['cap'] = dati_cliente.cap
        fourth_record['comune_e_sigla_provincia'] = dati_cliente.provincia
        fourth_record['completamento_indirizzo'] = ""
        fourth_record['codice_paese'] = "IT"
        
        riferimento_fattura =(riferimento_fattura[:30] + '..') if len(riferimento_fattura) > 30 else riferimento_fattura
        
        fifth_record['numero_progressivo'] =str(numero_progressivo).zfill(7)
        fifth_record['1_segmento'] = "R.F. " + riferimento_fattura
        fifth_record['2_segmento'] = "IMPORTO  " + importo_della_ricevuta_in_centesimi
        fifth_record['codifica_fiscale_creditore'] = str(dati_cliente.partita_iva)
        
        
        
        
        
        fifty_one['numero_progressivo'] = str(numero_progressivo).zfill(7)
        fifty_one['numero_ricevuta'] = str(numero_disposizione).zfill(10)
        fifty_one['denominazione_creditore'] = "MICROCARP S.R.L."
        
        seventieth_record['numero_progressivo'] = str(numero_progressivo).zfill(7)
        
        numero_disposizione +=1
        
        """ ALLA FINE DI TUTTI I RECORDS """
        
        disposizione.records.append(first_record)
        disposizione.records.append(second_record)
        disposizione.records.append(third_record)
        disposizione.records.append(fourth_record)
        disposizione.records.append(fifth_record)
        disposizione.records.append(fifty_one)
        disposizione.records.append(seventieth_record)
        
        
        flow.disposals.append(disposizione)
        disposizione = None
    
    
    # print "TOTALISSIMO {0}".format(totalissimo)
    # totalissimo = '%.2f' % totalissimo
    # totalissimo = str(totalissimo)[:]
    totalissimo = str(truncate_float(totalissimo,2))
    # print "TOTALISSIMO {0}".format(totalissimo)
    totalissimo = totalissimo.replace(".","").zfill(15)
    
    flow.footer['tot_importi_negativi']=totalissimo
    flow.footer['tot_importi_positivi']="".zfill(15)
    
    numero_record = str((len(numero_emissioni) * 7)+2).zfill(7)
    flow.footer['numero_record']=numero_record
    
    filename = os.getcwd()+"/applications/gestionale/static/"+"riba.txt"
    try:
        os.remove(filename)
    except:
        pass
    flow.writefile(filename)
    
    # print "LUNGHEZZA DISPOSIZIONE : ",len(flow.disposals)
    
    db.numero_disposizioni_riba.insert(numero=str(numero_disposizione))

def genera_riba():
    
    crea_file_riba()
    
    
    nomefile = "riba.txt"
    filename = os.getcwd()+"/applications/gestionale/static/"+"riba.txt"
    import cStringIO 
    # import contenttype as c
    s=cStringIO.StringIO()
    
    with open(filename,"r") as file:
        
        s.write(file.read())
        response.headers['Content-Type'] =gluon.contenttype.contenttype(filename)
        response.headers['Content-Disposition'] = "attachment; filename=%s" % nomefile  
        return s.getvalue() 
    
    

def emissione_riba_3():
    
    banca_scelta = db(db.temp_banca).select().first().banca
    try:
        numero_disposizione = db(db.numero_disposizioni_riba).select().first().numero
    except:
        numero_disposizione = 1
    
    lista_riba = crea_indici_riba()
    
    html ="""<table id="resoconto" class="table table-bordered">"""
    
    html += """<thead>"""
    html += """<tr>"""
    
    html += """<th>"""
    html += "Cliente" 
    
    html += """</th>"""
    
    html += """<th>"""
    html += "Dettaglio" 
    html += """</th>"""
    
    html += """<th>"""
    html += "Totale" 
    html += """</th>"""
    
    html += """</tr>"""
    
    html += """</thead>"""
    
    
    html += """<tbody>"""
    
    totale_distinta=0
    errore = False
    for item in lista_riba:
        html += """<tr>"""
        html += """<td>"""+ritorna_nome_cliente_da_id(item[0]) + """</td>"""
        html += """<td>"""
        
        banca_cliente = db(db.clienti.id==item[0]).select().first().codice_banca
        dati_banca_cliente = db(db.anagrafica_banche.descrizione == banca_cliente).select().first()
        
        if dati_banca_cliente is not None:
            abi = dati_banca_cliente.codice_abi
            cab = dati_banca_cliente.codice_cab
            
            if abi is None or len(abi) !=5:
                response.flash="La banca {0} collegata al cliente {1} non ha il codice ABI corretto".format(dati_banca_cliente.descrizione,ritorna_nome_cliente_da_id(item[0]))
                errore = True
            
            if cab is None or len(cab) !=5:
                response.flash="La banca {0} collegata al cliente {1} non ha il codice CAB corretto".format(dati_banca_cliente.descrizione,ritorna_nome_cliente_da_id(item[0]))
                errore = True
        else:
        
             response.flash="La banca {0} collegata al cliente {1} non è presente in anagrafica".format(banca_cliente,ritorna_nome_cliente_da_id(item[0]))
             errore = True
        
        
        totale = 0
        for fatture in item[1]:
          html += ritorna_dettaglio_fattura(fatture) +"<br>"
          totale += float(db(db.fatture_salvate.id ==fatture).select().first().totale)
          
        html += """</td>"""
        html += """<td>"""
        html += ritorna_prezzo_europeo(totale)
        html += """</td>"""
        
        totale_distinta += totale
        html += """</tr>"""
     
        # print "Cliente = ",ritorna_nome_cliente_da_id(item[0]) , "Fatture = ",item[1]
    html += """</tbody>"""    
    html +="""</table>"""
    html=XML(html)
    
    indietro = avanti =""
    if not errore:
        indietro = A(BUTTON("Indietro"),_href=URL('emissione_riba_2'))
        avanti = A(BUTTON("Crea e scarica file Riba"),_href=URL('genera_riba'))
    
    totale_distinta = ritorna_prezzo_europeo(totale_distinta)
    
    return locals()


def return_radio_button(id):
    
    return XML("<input type='checkbox' id ='check"+str(id)+"' onclick='accorpa("+str(id)+");'></input>")
    pass

def emissione_riba_2():
    
    db.fatture_scelte.a = Field.Virtual('accorpa',lambda row: return_radio_button(row.fatture_scelte.id))
    # db.fatture_scelte.a = Field.Virtual('radio','boolean')
    
    fields=[db.fatture_scelte.numero_fattura,db.fatture_scelte.totale,db.fatture_scelte.cliente,db.fatture_scelte.scadenza,db.fatture_scelte.a]
   
    # db.fatture_scelte.id.readable=False;
    riba_form =  SQLFORM.grid(db.fatture_scelte.user_id == auth.user_id,formname='riba_form',maxtextlength=100,create=False,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False, fields=fields)
    
    button = A(BUTTON("Successivo"),_href=URL('emissione_riba_3'))
    
    return locals()

def emissione_riba():
    
    db(db.fatture_scelte.user_id == auth.user_id).delete()
    
    banca_azienda = Set()
    
    b = db(db.anagrafica_banche_azienda).select()
    for e in b:
        banca_azienda.add(e.descrizione)
        
    
    return locals()
    

def ritorna_tipo_pagamento_da_fattura(fattura_id):
     row = db(db.fatture_salvate.id == fattura_id).select().first()
     scadenza = row.scadenza
     ids = eval(row.id_ddt)    
     for ddt in ids:
        
        try:
            id_ordine = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt).select().first().id_ordine
            pagamento = db(db.ordine_cliente.id == id_ordine).select().first().pagamento
        except:
            # print "ERRORE FATTURA ID ",fattura_id
            pagamento = scadenza =""
        return pagamento,scadenza
        
   

def anagrafica_clienti():
    clienti_form = SQLFORM.grid(db.clienti,formname='clienti',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True,exportclasses=export_classes)
    clienti_form.element('.web2py_counter', replace=None)
    try:
        clienti_form.element('select[name=codice_banca]')['_style'] = 'width:350px;height:25px;'
        clienti_form.element('input[name=luogo_consegna_1]')['_style'] = 'width:350px;height:25px;'
        clienti_form.element('input[name=luogo_consegna_2]')['_style'] = 'width:350px;height:25px;'
        clienti_form.element('input[name=luogo_consegna_3]')['_style'] = 'width:350px;height:25px;'
        clienti_form.element('input[name=luogo_consegna_4]')['_style'] = 'width:350px;height:25px;'
        clienti_form.element('input[name=luogo_consegna_5]')['_style'] = 'width:350px;height:25px;'
    except:
        pass
    
    # articli_form = SQLFORM.grid(db.clienti,formname='articoli',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=True)
    
    return dict(clienti_form = clienti_form)

def anagrafica_fornitori():
    fornitori_form = SQLFORM.grid(db.fornitori,formname='fornitori',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=4, formstyle = 'table3cols',csv=True,exportclasses=export_classes)
    fornitori_form.element('.web2py_counter', replace=None)

    return dict(fornitori_form = fornitori_form)


def gestione_codici_causali():
    form = SQLFORM.grid(db.codici_causali,formname='causali',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols')
    form.element('.web2py_counter', replace=None)
    return dict(form = form)

def gestione_codici_pagamenti():
    form = SQLFORM.grid(db.codici_pagamenti,formname='pagamenti',maxtextlength=100,create=True, editable=True,    deletable=False,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols')
    form.element('.web2py_counter', replace=None)
    return dict(form = form)




def anagrafica_piano_dei_conti():
    anagrafica_piano_dei_conti_form = SQLFORM.grid(db.anagrafica_piano_dei_conti,formname='anagrafica_piano_dei_conti',maxtextlength=100,create=True,     deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols')
    # anagrafica_piano_dei_conti_form.element('.web2py_counter', replace=None)

    return dict(anagrafica_piano_dei_conti_form = anagrafica_piano_dei_conti_form)

def index():
    response.flash = T("Home page")
    return dict(message=T(''))


@service.jsonrpc
@service.jsonrpc2
def return_listini(nome_cliente,tipo):
    
    
     nomi_listini = db(db.anagrafica_listini.nome_cliente == nome_cliente,db.anagrafica_listini.tipologia_listino == tipo).select()
     return nomi_listini.as_json()
    
    

@service.jsonrpc
@service.jsonrpc2
def return_pagamenti(*args):
    
    nome = args[0]
    if "cliente" in args[1]:
    # print "Nome cliente ",nome_cliente
    	nomi_listini = db(db.clienti.nome == nome).select().first()["pagamento"]
    else:
    	nomi_listini = db(db.fornitori.nome == nome).select().first()["pagamento"]
    return nomi_listini

@service.jsonrpc
@service.jsonrpc2
def aggiorna_quantita(id_riga_ordine,codice_articolo,quantita_prodotta):
    """
    questa quantità prodotta viene messa in relazione alla riga d'ordine.
    la quantità prodotta viene sommata a quella in magazzino
    Nell'anagrafica articoli viene visualizzata anche la quantità riservata
    
    Quando si emette un ddt ricordarsi di cancellare dalla tabella riserva_quantita le righe d'ordine associate.
    
    """
    
    
    record_giacenza_articolo_attuale = db(db.anagrafica_articoli.codice_articolo == str(codice_articolo)).select().first()
    giacenza = int(record_giacenza_articolo_attuale.giacenza) + int (quantita_prodotta)
    record_giacenza_articolo_attuale.update_record(giacenza = str(giacenza))
    
    db.riserva_quantita.insert(codice_articolo=codice_articolo,quantita=quantita_prodotta,id_riga_ordine=id_riga_ordine,user_id=auth.user_id)
    
    
    
    
    
    return "ok"

@service.jsonrpc
@service.jsonrpc2
def riserva_giacenza(id_riga_ordine,da_riservare):
    
        # print id_riga_ordine,da_riservare
        data = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
        codice_articolo = data.codice_articolo
        id_ordine_cliente = data.id_ordine_cliente
       
        data_articolo = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first()
        
        
        # print data_articolo.giacenza,da_riservare
        # data_articolo.update_record(giacenza = str(giacenza))
        
             
        db.riserva_quantita.insert(codice_articolo=codice_articolo,quantita=da_riservare,id_riga_ordine=id_riga_ordine,user_id=auth.user_id)
    
        return "ok"   
    


@service.jsonrpc
@service.jsonrpc2
def disdire_giacenza(id_riga_ordine,da_riservare):
    
        # print id_riga_ordine,da_riservare
        data = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
        codice_articolo = data.codice_articolo
        id_ordine_cliente = data.id_ordine_cliente
       
        data_articolo = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first()
        
        
        if int(ritorna_totale_prenotazione_da_codice_articolo(codice_articolo)) - int(da_riservare) <0:
            return 1/0
        
        da_riservare = int(da_riservare) *-1
        
      
                
             
        db.riserva_quantita.insert(codice_articolo=codice_articolo,quantita=da_riservare,id_riga_ordine=id_riga_ordine,user_id=auth.user_id)
    
        return "ok"  
   
@service.jsonrpc
@service.jsonrpc2
def aggiorna_giacenza(id_riga_ordine,da_riservare):
    
        # print id_riga_ordine,da_riservare
        data = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
        codice_articolo = data.codice_articolo
        id_ordine_cliente = data.id_ordine_cliente
       
        data_articolo = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first()
        
        
        try:
            giacenza = int(da_riservare)
            
            if giacenza < 0:
                return 1/0
            
            data_articolo.update_record(giacenza=str(giacenza))
            
        except:
            return 1/0
            
            
        return "ok"

def return_dettagli_articolo_da_riga_ordine():
    
    errore = False
    riga_evasa = False
    try:
        
        id_riga_ordine =request.vars['id_riga_ordine']
        data = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
        codice_articolo = data.codice_articolo
        id_ordine_cliente = data.id_ordine_cliente
        quantita_ordine = data.quantita
        data_articolo = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first()
        
        
        ubicazione = data_articolo.ubicazione
        if ubicazione is None:
            ubicazione = "Nessuna"
          
        data_ordine = db(db.ordine_cliente.id ==id_ordine_cliente).select().first()
        codice_ordine = data_ordine.ultimo_codice_ordine
        
        nome_cliente = data_ordine.nome_cliente
        
        riferimento_ordine = data_ordine.riferimento_ordine_cliente
       
        data_inserimento = data_ordine.data_inserimento
        
        
        descrizione = data_articolo.descrizione
        giacenza = data_articolo.giacenza
        quantita_saldo = ritorna_quantita_saldo(id_riga_ordine)
        
        prenotato = ritorna_totale_prenotazione_da_codice_articolo_e_riga_id(codice_articolo,id_riga_ordine)
        
        # print "PRENOTATO = ",prenotato
        
        # print "GIACENZA = ",giacenza
        
      
        
        giacenza_non_riservata = int(giacenza) - int(prenotato)
        
        
        # print "NON RISERVATA = ",giacenza_non_riservata
          
        produzione_da_riservare_per_completare_la_produzione = int(quantita_saldo) - int(prenotato)
        
        if produzione_da_riservare_per_completare_la_produzione < 1:
            produzione_da_riservare_per_completare_la_produzione = "PRODUZIONE COMPLETATA\n" + "SURPLUS DI " +str(abs(produzione_da_riservare_per_completare_la_produzione)) + " ARTICOLI"
        """
        """       
        
        if int(quantita_saldo) <1:
            quantita_saldo = "Quantità richiesta raggiunta"
        
        
        if riga_completata(id_riga_ordine):
           riga_evasa = True
           ddts = return_ddts_for_row_id(id_riga_ordine)
        
        
    except Exception, e:
        # print e
        errore = True
        id_riga_ordine=""
        codice_articolo = ""
        descrizione =""
        giacenza = ""
        cliente = ""
        codice_ordine = ""
        quantita_ordine =""
        prenotato =""
        giacenza_non_riservata =""
        produzione_da_riservare_per_completare_la_produzione=""
        riferimento_ordine=""
        data_inserimento=""
        quantita_saldo=""
        giacenza_non_riservata=""
        produzione_da_riservare_per_completare_la_produzione=""
        ubicazione=""
        return locals()
    return locals()

def return_dettagli_articolo_da_riga_ordine_per_cartellini():
    
    errore = False
    riga_evasa = False
    try:
        
        id_riga_ordine =request.vars['id_riga_ordine']
        data = db(db.righe_in_ordine_cliente.id == id_riga_ordine).select().first()
        codice_articolo = data.codice_articolo
        id_ordine_cliente = data.id_ordine_cliente
        quantita_ordine = data.quantita
        data_articolo = db(db.anagrafica_articoli.codice_articolo == codice_articolo).select().first()
        
        
        ubicazione = data_articolo.ubicazione
        if ubicazione is None:
            ubicazione = "Nessuna"
          
        data_ordine = db(db.ordine_cliente.id ==id_ordine_cliente).select().first()
        codice_ordine = data_ordine.ultimo_codice_ordine
        
        nome_cliente = data_ordine.nome_cliente
        
        riferimento_ordine = data_ordine.riferimento_ordine_cliente
       
        data_inserimento = data_ordine.data_inserimento
        
        
        descrizione = data_articolo.descrizione
        giacenza = data_articolo.giacenza
        quantita_saldo = ritorna_quantita_saldo(id_riga_ordine)
        
        prenotato = ritorna_totale_prenotazione_da_codice_articolo_e_riga_id(codice_articolo,id_riga_ordine)
        
        # print "PRENOTATO = ",prenotato
        
        # print "GIACENZA = ",giacenza
        
      
        
        giacenza_non_riservata = int(giacenza) - int(prenotato)
        
        
        # print "NON RISERVATA = ",giacenza_non_riservata
          
        produzione_da_riservare_per_completare_la_produzione = int(quantita_saldo) - int(prenotato)
        
        if produzione_da_riservare_per_completare_la_produzione < 1:
            produzione_da_riservare_per_completare_la_produzione = "PRODUZIONE COMPLETATA\n" + "SURPLUS DI " +str(abs(produzione_da_riservare_per_completare_la_produzione)) + " ARTICOLI"
        """
        """       
        
        if int(quantita_saldo) <1:
            quantita_saldo = "Quantità richiesta raggiunta"
        
        
        if riga_completata(id_riga_ordine):
           riga_evasa = True
           ddts = return_ddts_for_row_id(id_riga_ordine)
        
        
        quantita_prodotta = return_quantity_for_row_id(id_riga_ordine)
    except Exception, e:
        # print e
        errore = True
        id_riga_ordine=""
        codice_articolo = ""
        descrizione =""
        giacenza = ""
        cliente = ""
        codice_ordine = ""
        quantita_ordine =""
        prenotato =""
        giacenza_non_riservata =""
        produzione_da_riservare_per_completare_la_produzione=""
        riferimento_ordine=""
        data_inserimento=""
        quantita_saldo=""
        giacenza_non_riservata=""
        produzione_da_riservare_per_completare_la_produzione=""
        ubicazione=""
        return locals()
    return locals()
            
# return_dettagli_articolo_da_riga_ordine

def stampa_cartellini_1():
    articoli_form = SQLFORM.grid(db.anagrafica_articoli,formname='articoli1',maxtextlength=100,create=True,        	deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,user_signature=True)
    return locals()

def aggiorna_giacenze():
     
    articoli_form = SQLFORM.grid(db.anagrafica_articoli,formname='articoli1',maxtextlength=100,create=True,        deletable=True,searchable=True,sortable=True,paginate=5, formstyle = 'table3cols',csv=False,user_signature=True)
    return locals()


@service.jsonrpc
@service.jsonrpc2
def return_description(cod):
	rows = db(db.anagrafica_articoli.codice_articolo==cod).select().first()
	return rows.descrizione
	

@service.jsonrpc
@service.jsonrpc2
def return_price(articolo,numero,listino,cliente):
       
   
    prezzo_corrente = 0
    start = 0
    end = 0
    
    h = HTMLParser()
    cliente = h.unescape(cliente)
    
    rows = db(db.articolo_in_listino.nome_cliente == cliente,db.articolo_in_listino == listino).select()

   
   
    for row in rows:
        if row['listino'] == listino:
            if row['codice_articolo'] == articolo:
                # print "OK"
                end = int(row['numero_pezzi'])
                if (int(numero) > start) and (int(numero) <= end):
                    prezzo_corrente = float(row['prezzo'])
                start = end
                    
    # print prezzo_corrente
    if prezzo_corrente == 0:
        prezzo_corrente=""                
    return prezzo_corrente
    

@service.jsonrpc
@service.jsonrpc2
def return_price_fornitori(articolo,numero,listino,cliente):
       
   
    prezzo_corrente = 0
    start = 0
    end = 0
    
    # print "-----------------------------------"
    h = HTMLParser()
    cliente = h.unescape(cliente)
    rows = db(db.articolo_in_listino_fornitori.nome_fornitore == cliente).select()

   
    
    for row in rows:
        # print "{0} {1} {2} {3}".format(row['nome_fornitore'],len(row['nome_fornitore']),cliente,len(cliente))
        
        if row['listino'] == listino:
            if row['codice_articolo'] == articolo:
                # print "OK"
                end = int(row['numero_pezzi'])
                # print "Numero pezzi : ",end
                if (int(numero) > start) and (int(numero) <= end):
                    # print "prezzo corrente : ",float(row['prezzo'])
                    prezzo_corrente = float(row['prezzo'])
                start = end
                    
    # print prezzo_corrente
    if prezzo_corrente == 0:
        prezzo_corrente=""                
    return prezzo_corrente

@service.jsonrpc
@service.jsonrpc2
def search_piano_dei_conti(args):
    return_data = []
    gruppo = args[:-5]
    conto = args[2:4]
    sottoconto = args[4:]
    
    gruppo_to_search=gruppo + "00000"
    conto_to_search=gruppo+conto+"000"
    sottoconto_to_search = gruppo + conto + sottoconto
   
    descrizione_gruppo = ""
    descrizione_conto = ""
    descrizione_sottoconto = ""
    
    # print gruppo_to_search,conto_to_search,sottoconto_to_search
        
    try:
        descrizione_gruppo = db(db.anagrafica_piano_dei_conti.codice_piano_dei_conti == gruppo_to_search).select().first()["descrizione_codice"]
    except:
       pass
    
    
    if not conto_to_search == gruppo_to_search:
        try:
            descrizione_conto = db(db.anagrafica_piano_dei_conti.codice_piano_dei_conti == conto_to_search).select().first()["descrizione_codice"]
        except:
            pass
        
    if not sottoconto_to_search == gruppo_to_search and not sottoconto_to_search == conto_to_search:
        try:
            descrizione_sottoconto = db(db.anagrafica_piano_dei_conti.codice_piano_dei_conti == sottoconto_to_search).select().first()["descrizione_codice"]
        except:
            pass
    
    if len(descrizione_gruppo)<1:
        gruppo_to_search=""
        
    if len(descrizione_conto)<1:
        conto_to_search=""
    
    if len(descrizione_sottoconto)<1:
        sottoconto_to_search=""
        
    
    return_data.append(gruppo_to_search)
    return_data.append(descrizione_gruppo)
    
    return_data.append(conto_to_search)
    return_data.append(descrizione_conto)
    
    return_data.append(sottoconto_to_search)
    return_data.append(descrizione_sottoconto)
    
    # print return_data
    return return_data

def ritorna_nome_cliente_da_riga_ordine(id_ordine):
	# id_ordine_cliente=db(db.righe_in_ordine_cliente.id==id_riga_ordine).select().first()["id_ordine_cliente"]
	try:
        	nome=db(db.ordine_cliente.id==id_ordine).select().first()["nome_cliente"]
        except:
            nome=""
	return nome

def ritorna_nome_fornitore_da_riga_ordine(id_ordine):
    	# id_ordine_cliente=db(db.righe_in_ordine_cliente.id==id_riga_ordine).select().first()["id_ordine_cliente"]
	try:
        	nome=db(db.ordine_fornitore.id==id_ordine).select().first()["nome_fornitore"]
        except:
            nome=""
	return nome	
	
def ritorna_ddt_da_id(ddt_id):
    try:
        ddt=db(db.saved_ddt.saved_ddt_id==ddt_id).select().first()["numero_ddt"]
    except:
        ddt=""
    
    return ddt

def ritorna_ddt_da_id_fornitori(ddt_id):
    try:
        ddt=db(db.saved_ddt_fornitori.saved_ddt_id==ddt_id).select().first()["numero_ddt"]
    except:
        ddt=""
    
    return ddt


def storico_articoli_prodotti_cron():
    db(db.storico_articoli_prodotti).delete()
    rows=db(db.saved_righe_in_ddt_cliente.codice_articolo !="commento").select()
    for row in rows:
        ddt=ddt=ritorna_ddt_da_id(row.saved_ddt_id)
        if len(ddt)>0:
            db.storico_articoli_prodotti.insert(cliente=ritorna_nome_cliente_da_riga_ordine(row.id_ordine),codice_ordine=row.codice_ordine,n_riga=row.n_riga,codice_articolo=row.codice_articolo,descrizione=row.descrizione,riferimento_ordine=row.riferimento_ordine,quantita=row.quantita,prezzo=row.prezzo,codice_iva=row.codice_iva,evasione=row.evasione,ddt=ddt)
    return locals()


def storico_articoli_prodotti():
    # db.saved_righe_in_ddt_cliente.nome_cliente=Field.Virtual("Cliente", lambda row: ritorna_nome_cliente_da_riga_ordine(row.saved_righe_in_ddt_cliente.id_ordine))
    db.storico_articoli_prodotti.id.readable=False
    articoli=SQLFORM.grid(db.storico_articoli_prodotti,formname='articoli',maxtextlength=100,create=False,        deletable=False,editable=False,searchable=True,sortable=True,paginate=7, formstyle = 'table3cols',csv=False,user_signature=True)
    
    return locals()

def storico_articoli_prodotti_fornitore_cron():
    db(db.storico_articoli_prodotti_fornitore).delete()
    rows=db(db.saved_righe_in_ddt_fornitore).select()
    for row in rows:
        ddt=ddt=ritorna_ddt_da_id_fornitori(row.saved_ddt_id)
        if len(ddt)>0:
            db.storico_articoli_prodotti_fornitore.insert(fornitore=ritorna_nome_fornitore_da_riga_ordine(row.id_ordine),codice_ordine=row.codice_ordine,n_riga=row.n_riga,codice_articolo=row.codice_articolo,descrizione=row.descrizione,riferimento_ordine=row.riferimento_ordine,quantita=row.quantita,prezzo=row.prezzo,codice_iva=row.codice_iva,evasione=row.evasione,ddt=ddt)
    
    return locals()



def storico_articoli_prodotti_fornitore():
    # db.saved_righe_in_ddt_cliente.nome_cliente=Field.Virtual("Cliente", lambda row: ritorna_nome_cliente_da_riga_ordine(row.saved_righe_in_ddt_cliente.id_ordine))
    db.storico_articoli_prodotti_fornitore.id.readable=False
    articoli=SQLFORM.grid(db.storico_articoli_prodotti_fornitore,formname='articoli',maxtextlength=100,create=False,        deletable=False,editable=False,searchable=True,sortable=True,paginate=7, formstyle = 'table3cols',csv=False,user_signature=True)
    
    return locals()


@service.jsonrpc
@service.jsonrpc2
def stampa_etichetta(*args):
    cliente = args[0]
    codice_articolo = args[1]
    descrizione = args[2]
    quantita= args[3]
    lotto = args[4]
    numero_etichette = args[5]
    ordine = args[6]
    contenitore = args[7]

    # print quantita
    # print contenitore
    
    etichette_totali,ultima_capienza_contenitore = divmod(int(quantita),int(contenitore))
    
    
    if ultima_capienza_contenitore == 0:
        ultima_capienza_contenitore = contenitore
        etichette_da_scrivere = etichette_totali
        if etichette_totali == 1:
                # print "qui"
		etichette_totali ==0
    else:
       etichette_da_scrivere = etichette_totali +1
 
    
    

    if True:
        """
        if cliente == "new_global":
    		prn_file = request.folder + 'prn_labels/new_global.prn'
        	codice_articolo = codice_articolo[1:]
                destinazione = args[8]
                ordine +=destinazione
	
	if cliente == "siat":
    		prn_file = request.folder + 'prn_labels/siat.prn'
    		
    	
    	if cliente == "mc":
    		prn_file = request.folder + 'prn_labels/mc.prn'
        	
        

        if cliente == "new_global_romania":
    		prn_file = request.folder + 'prn_labels/new_global_romania.prn'
        	codice_articolo = codice_articolo[1:]
                destinazione = args[8]
                ordine +="  "+destinazione	

        if "cimbali" in cliente:
    		prn_file = request.folder + 'prn_labels/cimbali.prn'
        	
                destinazione = args[8]
                ordine +=destinazione	        

        if "rhea" in cliente:
    		prn_file = request.folder + 'prn_labels/rhea.prn'
                if codice_articolo[len(codice_articolo)-1].isdigit():
			
                	codice_articolo = "Z"+codice_articolo[:-2]
		else:
			codice_articolo = "Z" + codice_articolo[:-4] + codice_articolo[len(codice_articolo)-2:] 

                destinazione = args[8]
                ordine +=destinazione	
	"""
	
	prn_file = request.folder + 'prn_labels/mc.prn'
        for x in range(etichette_totali):
   	    
    	    _content = []
            # print "IN FOR"
    
    	    with open(prn_file, 'r') as content_file:
    		    content = content_file.read()
    	    
    		    content = content.replace("[*1*]", codice_articolo)
    		    content = content.replace("[*2*]", descrizione)
    		    content = content.replace("[*3*]", quantita)
    		    content = content.replace("[*5*]", ordine)
    		    content = content.replace("[*6*]", contenitore)
    		    content = content.replace("[*10*]", str(x + 1))
    		    content = content.replace("[*11*]", str(etichette_da_scrivere))
    		    content = content.replace("[*12*]", cliente)
    		
            with open("/tmp/to#print.prn", 'w') as content_file:
                   content_file.write(content)
    			 
            print_label(numero_etichette)
        
            with open(prn_file, 'r') as content_file:
    
                content = content_file.read()
    	  
        if etichette_totali ==1:
             with open(prn_file, 'r') as content_file:
    		    content = content_file.read()

    	content = content.replace("[*1*]", codice_articolo)
    	content = content.replace("[*2*]", descrizione)
    	content = content.replace("[*3*]", quantita)
    	content = content.replace("[*5*]", ordine)
    	content = content.replace("[*6*]", str(ultima_capienza_contenitore))
    	content = content.replace("[*10*]", str(etichette_da_scrivere))
    	content = content.replace("[*11*]", str(etichette_da_scrivere))
    	content = content.replace("[*12*]", cliente)   
    	    
    	with open("/tmp/to#print.prn", 'w') as content_file:
    		content_file.write(content)
        print etichette_totali,ultima_capienza_contenitore
    	if etichette_totali >0 and not ultima_capienza_contenitore == contenitore:	 
    		print_label(numero_etichette)

def print_label(numero_etichette):
    
        ip="192.168.0.208"
        port = "9100"
        prn_file = "/tmp/to#print.prn"
        
        try:
           numero = int(numero_etichette)
        except:
           numero = 1
        
        for x in range(numero):
        	# command = "ncat --send-only "+ip+" "+port+" < "+prn_file
        	command = "nc "+ip+" "+port+" < "+prn_file
        	# print command
        	p = subprocess.Popen(command, shell=True)
        	p.wait()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@service.jsonrpc
@service.jsonrpc2
def crea_fattura_xml(args):

    data={}
    fattura=None
    fattura=FatturaXml()
    articoli=set([])

    partitaIvaCarpal="01619570193"
    codiceFiscaleCarpal="01619570193"
    denominazioneCarpal="MICROCARP S.R.L."
    indirizzoCarpal="Strada Statale 415"
    capCarpal="26012"
    provinciaCarpal="CR"
    paeseCarpal="Castelleone"

    # Progressivo Invio
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    numeroDocumento=str(numero)

    progressivoInvio=numero_fattura_da_salvare

    

    

    
    """
    Dati cliente
    """
    id_cliente=args['0']
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    iban_cliente = dati_cliente.codice_iban
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    scritta_esenzione_cliente = dati_cliente.descrizione_esenzione_iva
    annotazioni=dati_cliente.annotazioni
    codiceDestinatario=dati_cliente.codiceDestinatario
    pecDestinatario=dati_cliente.pec
    dichiarazione=dati_cliente.descrizione_esenzione_iva
    bollo_interno=dati_cliente.bollo

    esigibilitaIva="I"
    if "leonardo" in nome_cliente.lower():
         esigibilitaIva="S"
         try:
             ddt = db(db.ddt_da_fatturare.user_id == auth.user_id).select().first()
             ddt_id=ddt.ddt_id
             print "Dettaglio ddt",ddt
             numero_ddt=ddt.numero_ddt
             data_emissione_ddt=ddt.data_emissione
             print data_emissione_ddt
             data_emissione_ddt=datetime.datetime.strptime(data_emissione_ddt,"%d/%m/%Y")
             fattura.addSingleDdt(numero_ddt,data_emissione_ddt.strftime("%Y-%m-%d"))


             righe=db(db.saved_righe_in_ddt_cliente.saved_ddt_id==ddt_id).select().first()
             id_ordine=righe.id_ordine
             dati_ordine=db(db.ordine_cliente.id==id_ordine).select().first()
             print dati_ordine
             ente=dati_ordine.ente
             idOrdineAcquisto=dati_ordine.riferimento_ordine_cliente
             cig=dati_ordine.cig
             cup=dati_ordine.cup
             if cig is not None or cup is not None:
                fattura.addOrdineAcquisto(idOrdineAcquisto,cig,cup)

             print "Trovata ente : "+ente
             
             if "ETN" in ente:
                 codiceDestinatario="DL33NSJ"

             if "SAS" in ente:
                 codiceDestinatario="OXPJRM5"
             
             if "SSI" in ente:
                 codiceDestinatario="RUZUQNZ"
             

         except:
             data['msg']="Impossibile recuperare ente per "+str(nome_cliente)
             data['error']=True
             return json.dumps(data)

         

    if bollo_interno:
        fattura.addBollo()

    if dichiarazione is not None:
            if len(dichiarazione)>0:
                    fattura.addDichiarazione(dichiarazione)

    if codiceDestinatario is None and pecDestinatario is None:
        data['msg']="Inserire codice destinatario o pec per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if len(codiceDestinatario)<5 and len(pecDestinatario)<5:
        data['msg']="Inserire codice destinatario o pec per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if pi_cliente is None:
        data['msg']="Inserire la partita iva per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

   
    
    fattura.addDatiTrasmissione("IT",codiceFiscaleCarpal,progressivoInvio,codiceDestinatario,pecDestinatario)
    fattura.addCedentePrestatore("IT",partitaIvaCarpal,denominazioneCarpal)
    fattura.addSedeCedentePrestatore(indirizzoCarpal,capCarpal,paeseCarpal,provinciaCarpal,"IT")

    # Dati cliente
    fattura.addCessionarioCommittente("IT",pi_cliente.replace("IT",""),nome_cliente)
    fattura.addSedeCessionarioCommittente(indirizzo_cliente,cap_cliente,citta_cliente,provincia_cliente,"IT")

    tipoDocumento=ritornaTipoDiPagamento(args['1'])


    # Calcolo data fattura
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    for r in ddts_id:
        data_scelta = r.data_emissione
        
    m = datetime.datetime.strptime(data_scelta,"%d/%m/%Y").date()
        
    day_start,day_end = monthrange(m.year, m.month)
    d = str(day_end)+"/"+str(m.month)+"/"+str(m.year)
    
    start_date = datetime.datetime.strptime(d,"%d/%m/%Y")

    # Creazione descrizione fattura
    descrizione_fattura=""
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    for ddt_id in ddts_id:
        descrizione_fattura += "Rif. DDT : " + ddt_id.numero_ddt + " del " + ddt_id.data_emissione+" "

    fattura.addDatiGeneraliDocumento(tipoDocumento,fixDate(start_date.strftime("%d-%m-%Y")),numeroDocumento,descrizione_fattura)
    
    # Controllare se ci possono essere più rate di pagamento

    """
    if len(righeDataScadenza)>1:
        pagamento="TP01"
    else:
        pagamento="TP02"
    
    """
    # Per ora metto sempre solo 1 rata
    pagamento="TP02"
    fattura.addCondizioniPagamento(pagamento)

    articoli=[]
    for ddt_id in ddts_id:
      rows = db(db.saved_righe_in_ddt_cliente.saved_ddt_id == ddt_id.ddt_id).select()
      for row in rows:
        if not "commento" in row.codice_articolo:
                articolo=[]
                id_ordine = row.id_ordine
                try:
                      
                      try:
                          pagamento = db(db.ordine_cliente.id == id_ordine).select().first()["pagamento"]
                     
                      except:
                          pagamento = None
                                                                
                      if pagamento is None:
                            pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                       
                      if "F.M." in pagamento:
                          fine_mese = True
                      else:
                          fine_mese = False

                      if not fine_mese:
                              
                          try:
                              giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                              
                              if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                          
                              scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                              scadenza_salvata = scadenza
                              scadenza = scadenza.strftime("%d/%m/%Y")
                          except:
                               response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                               return locals()
                              
                      else:
                          
                           if ("M.S." or "ms") in pagamento:
                               
                               giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                               if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                               
                               giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                               scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                               day_start,day_end = monthrange(scadenza.year, scadenza.month)
                               scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                               scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                               scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                               scadenza = scadenza.strftime("%d/%m/%Y") 
                               
                           else:
                               # Fine mese senza M.S.               
                               giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                               if start_date.date().month==12 or start_date.date().month==1 or start_date.date().month==2:
                               	   if int(giorni_da_aggiungere)==60:
                               	   	giorni_da_aggiungere="56"
                               	   if int(giorni_da_aggiungere)==90:
                               	   	giorni_da_aggiungere="86"
                               	   	
                               	   if int(giorni_da_aggiungere)==120:
                               	   	giorni_da_aggiungere="116"
                               
                               
                               scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                               day_start,day_end = monthrange(scadenza.year, scadenza.month)
                               scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)

                      # fattura.dettaglio(str(id_cliente),dettagli_banca.descrizione,str(iban_cliente),pagamento,str(scadenza))
                      codice_articolo=row.codice_articolo
                      descrizione=row.descrizione
                      um=row.u_m
                      qta=row.quantita
                      codice_iva=row.codice_iva
                      riferimento_ordine=row.riferimento_ordine
                      prezzo=row.prezzo
                      n_riga=str(row.n_riga)
                      descrizione+=" Pos. "+n_riga 

                      percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["percentuale_iva"]
                      codice_iva_interno=db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["codice_iva"]
                      bollo = db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["bollo_su_importi_esenti"]

                      # print codice_articolo,descrizione,um,qta,prezzo,riferimento_ordine,pagamento,scadenza
                      articolo.append(codice_articolo)
                      articolo.append(descrizione)
                      articolo.append(codice_iva)
                      articolo.append(percentuale_iva)
                      articolo.append(bollo)
                      articolo.append(um)
                      articolo.append(qta)
                      articolo.append(controllaPrezzo(prezzo))
                      articolo.append(riferimento_ordine)
                      articolo.append(pagamento)
                      articolo.append(scadenza)
                      articolo.append(ritornaCondizioniPagamento(pagamento))
                      articolo.append(codice_iva_interno)

                      add=True
                      for a in articoli:
                          # print a,articolo,a==articolo
                          if a==articolo:
                              add=False
                              break

                      if add:
                          
                          articoli.append(articolo)
                     
                      articolo=[]
                except Exception,e:
                     
                       data['msg']="Controllare tipo pagamento per  cliente "+str(nome_cliente)+str(e)
                       data['error']=True
                       return json.dumps(data)
    


    if bollo_interno:
        articolo=[]
 
        codice_iva_interno="54"
      
        articolo.append("")
        articolo.append("Imposta di bollo assolta in modo virtuale ex DM 17/06/2014")
        articolo.append("Esente Iva")
        articolo.append(0.00)
        articolo.append("")
        articolo.append("Nr")
        articolo.append("1")
        articolo.append("2.00")
        articolo.append("")
        articolo.append(pagamento)
        articolo.append(scadenza)
        articolo.append(ritornaCondizioniPagamento(pagamento))
        articolo.append(codice_iva_interno)
        articoli.append(articolo) 

    def ritornaImponibile(qta,prezzo):
        imponibile= float(qta)*float(prezzo)
        print imponibile,float("%0.2f"%imponibile)
        return float("%0.2f"%imponibile)


    def ritornaTotaleArticoli(articoli):
        totale=0.0
        for articolo in articoli:
            imponibile=ritornaImponibile(articolo[6],articolo[7])
            percentualeIva=articolo[3]
            totaleIvaInclusa=imponibile + (imponibile*percentualeIva)/100
            totale+=totaleIvaInclusa

        return str("{:.2f}".format(totale))
    


    # Dettagilio Pagamento
    articolo=articoli[0]
    dataToFix=articolo[10]
    d=dataToFix.split("/")

    if len(d[1])==1:
        d[1]="0"+d[1]

    if len(d[0])==1:
        d[0]="0"+d[1]
    
    
    d=d[2]+"-"+d[1]+"-"+d[0]
    fattura.addDettaglioPagamento(articolo[11],d,ritornaTotaleArticoli(articoli))
    print "Totale iva inclusa : ",ritornaTotaleArticoli(articoli)


    # TotalerigheCodiciIva

    db(db.anagrafica_codici_iva).select()

    TotaleRigheCodiciIva={}



    for articolo in articoli:
        percentuale_iva=articolo[3]
        codice_iva_interno=articolo[12]
        
        imponibile=ritornaImponibile(articolo[6],articolo[7])
        if not TotaleRigheCodiciIva.has_key(codice_iva_interno):
            TotaleRigheCodiciIva[codice_iva_interno] = imponibile

        else:
            TotaleRigheCodiciIva[codice_iva_interno] = TotaleRigheCodiciIva[codice_iva_interno] + imponibile


           
    print TotaleRigheCodiciIva
    for k in TotaleRigheCodiciIva:
       print "ALIQUOTA IVA : ",k
       aliquota_iva = db(db.anagrafica_codici_iva.codice_iva == k).select().first()["percentuale_iva"]
       imponibile=TotaleRigheCodiciIva[k]
       
       if k=="22":
           aliquota_iva="22.00"
           descrizione_imposta=""
           if esigibilitaIva=="S":
                 descrizione_imposta=scritta_esenzione_cliente
           
           imposta=(imponibile*22.0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),esigibilitaIva,descrizione_imposta,k)

       if k=="10":
           aliquota_iva="10.00"
           descrizione_imposta=""
           imposta=(imponibile*10.0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),esigibilitaIva,descrizione_imposta,k)




       if k=="53":
           aliquota_iva="0.00"
           descrizione_imposta=db(db.anagrafica_codici_iva.codice_iva == k).select().first()["descrizione"]
           imposta=(imponibile*0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),esigibilitaIva,descrizione_imposta,k)
           print "sono qui"

       if k=="54":
           aliquota_iva="0.00"
           descrizione_imposta=db(db.anagrafica_codici_iva.codice_iva == k).select().first()["descrizione"]
           imposta=(imponibile*0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),"I",descrizione_imposta,k)


    numero_linea=1
    for articolo in articoli:
        if "22" in articolo[12]:
            aliquota="22.00"
        elif "10" in articolo[12]:
            aliquota="10.00"
        else:
            aliquota="0.00"
   

        descrizione=articolo[0]+" "+articolo[1]+" Ord. "+articolo[8] #riferimento ordine
        qta=fixPrezzo(articolo[6])+".00"
        prezzo=str(articolo[7])
        codice_iva=str(articolo[12])
        importo=str("{:.2f}".format(ritornaImponibile(qta,prezzo)))

        

        fattura.addLinea(str(numero_linea),descrizione,qta,prezzo,importo,aliquota,codice_iva)
        numero_linea+=1
    

    nome_file=fattura.writeXml()
    # cwd = os.getcwd()+"/applications/gestionale/uploads/fatture/"
    # id_cliente=args['0']
    # tipo_fattura=args['1']

    # data['error']=None
    data['msg']="Tutapost"
    data['filename']=nome_file

    return json.dumps(data)



@service.jsonrpc
@service.jsonrpc2
def crea_fattura_xml_istantanea(args):

    data={}
    fattura=None
    fattura=FatturaXml()
    articoli=set([])

    partitaIvaCarpal="01619570193"
    codiceFiscaleCarpal="01619570193"
    denominazioneCarpal="MICROCARP S.R.L."
    indirizzoCarpal="Strada Statale 415"
    capCarpal="26012"
    provinciaCarpal="CR"
    paeseCarpal="Castelleone"

    # Progressivo Invio
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    numeroDocumento=str(numero)

    progressivoInvio=numero_fattura_da_salvare

    

    

    
    """
    Dati cliente
    """
    id_cliente=args['0']
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    iban_cliente = dati_cliente.codice_iban
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    scritta_esenzione_cliente = dati_cliente.descrizione_esenzione_iva
    annotazioni=dati_cliente.annotazioni
    codiceDestinatario=dati_cliente.codiceDestinatario
    pecDestinatario=dati_cliente.pec
    bollo_interno=dati_cliente.bollo

    dichiarazione=dati_cliente.descrizione_esenzione_iva

    if dichiarazione is not None:
            if len(dichiarazione)>0:
                    fattura.addDichiarazione(dichiarazione)


    if codiceDestinatario is None and pecDestinatario is None:
        data['msg']="Inserire codice destinatario o pec per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if pi_cliente is None:
        data['msg']="Inserire la partita iva per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if len(codiceDestinatario)<5 and len(pecDestinatario)<5:
        data['msg']="Inserire codice destinatario o pec per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if bollo_interno:
        fattura.addBollo()

   
    
    fattura.addDatiTrasmissione("IT",codiceFiscaleCarpal,progressivoInvio,codiceDestinatario,pecDestinatario)
    fattura.addCedentePrestatore("IT",partitaIvaCarpal,denominazioneCarpal)
    fattura.addSedeCedentePrestatore(indirizzoCarpal,capCarpal,paeseCarpal,provinciaCarpal,"IT")

    # Dati cliente
    fattura.addCessionarioCommittente("IT",pi_cliente.replace("IT",""),nome_cliente)
    fattura.addSedeCessionarioCommittente(indirizzo_cliente,cap_cliente,citta_cliente,provincia_cliente,"IT")

    tipoDocumento=ritornaTipoDiPagamento(args['1'])


    # Calcolo data fattura
    """
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    for r in ddts_id:
        data_scelta = r.data_emissione
        
    m = datetime.datetime.strptime(data_scelta,"%d/%m/%Y").date()
        
    day_start,day_end = monthrange(m.year, m.month)
    d = str(day_end)+"/"+str(m.month)+"/"+str(m.year)
    
    start_date = datetime.datetime.strptime(d,"%d/%m/%Y")
    """
    start_date = datetime.datetime.now()

    # Creazione descrizione fattura
    descrizione_fattura="Fattura Immediata"
    fattura.addDatiGeneraliDocumento(tipoDocumento,fixDate(start_date.strftime("%d-%m-%Y")),numeroDocumento,descrizione_fattura)
    
    # Controllare se ci possono essere più rate di pagamento

    """
    if len(righeDataScadenza)>1:
        pagamento="TP01"
    else:
        pagamento="TP02"
    
    """
    # Per ora metto sempre solo 1 rata
    pagamento="TP02"
    fattura.addCondizioniPagamento(pagamento)

    articoli=[]
    articolo=[]

    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []
    if True:
        rows = db(db.righe_in_fattura_istantanea).select()
        for row in rows:
        
            try:
         
                
                  pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                  print "Pagamento :",pagamento
                        
                  if "F.M." in pagamento:
                      fine_mese = True
                  else:
                      fine_mese = False
                      
                   
                  
                    
                  
                  
                  if not fine_mese:
                       try:
                          giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                          scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                          scadenza_salvata = scadenza
                          scadenza = scadenza.strftime("%d/%m/%Y")
                         
                       except:
                           response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                           return locals()
                  else:
                      
                       if ("M.S." or "ms") in pagamento:
                           
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                           scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                           scadenza = scadenza.strftime("%d/%m/%Y") 
                           
                       else:
                           # Fine mese senza M.S.               
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           print "Scadenza : ",scadenza
                       
                  print "qui prima articolo"
                  print row
                  codice_articolo=row.codice_articolo
                  descrizione=row.descrizione
                  um=row.u_m
                  qta=row.qta
                  codice_iva=row.codice_iva
                  print "Codice iva",codice_iva
                  riferimento_ordine=row.riferimento_ordine
                  prezzo=row.prezzo
                  print "qui dopo articolo"
                  
                  percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["percentuale_iva"]
                  codice_iva_interno=db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["codice_iva"]
                  bollo = db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["bollo_su_importi_esenti"]

                  articolo.append(codice_articolo)
                  articolo.append(descrizione)
                  articolo.append(codice_iva)
                  articolo.append(percentuale_iva)
                  articolo.append(bollo)
                  articolo.append(um)
                  articolo.append(qta)
                  articolo.append(controllaPrezzo(prezzo))
                  articolo.append(riferimento_ordine)
                  articolo.append(pagamento)
                  articolo.append(scadenza)
                  articolo.append(ritornaCondizioniPagamento(pagamento))
                  articolo.append(codice_iva_interno)

                  add=True
                  for a in articoli:
                          print a,articolo,a==articolo
                          if a==articolo:
                              add=False
                              break

                  if add:
                      articoli.append(articolo)
                      articolo=[]
            except Exception,e:
                     
                       data['msg']="Controllare tipo pagamento per  cliente "+str(nome_cliente)+str(e)
                       data['error']=True
                       return json.dumps(data) 
                      


    if bollo_interno:
        articolo=[]
 
        codice_iva_interno="54"
      
        articolo.append("")
        articolo.append("Imposta di bollo assolta in modo virtuale ex DM 17/06/2014")
        articolo.append("Esente Iva")
        articolo.append(0.00)
        articolo.append("")
        articolo.append("Nr")
        articolo.append("1")
        articolo.append("2.00")
        articolo.append("")
        articolo.append(pagamento)
        articolo.append(scadenza)
        articolo.append(ritornaCondizioniPagamento(pagamento))
        articolo.append(codice_iva_interno)
        articoli.append(articolo)     


    print articoli
    def ritornaImponibile(qta,prezzo):
        imponibile= float(qta)*float(prezzo)
        return float("%0.2f"%imponibile)


    def ritornaTotaleArticoli(articoli):
        totale=0.0
        for articolo in articoli:
            imponibile=ritornaImponibile(articolo[6],articolo[7])
            percentualeIva=articolo[3]
            totaleIvaInclusa=imponibile + (imponibile*percentualeIva)/100
            totale+=totaleIvaInclusa

        return str("{:.2f}".format(totale))
    


    # Dettagilio Pagamento
    articolo=articoli[0]
    dataToFix=articolo[10]
    d=dataToFix.split("/")

    if len(d[1])==1:
        d[1]="0"+d[1]

    if len(d[0])==1:
        d[0]="0"+d[1]
    
    
    d=d[2]+"-"+d[1]+"-"+d[0]
    fattura.addDettaglioPagamento(articolo[11],d,ritornaTotaleArticoli(articoli))

    print articolo[11],d,ritornaTotaleArticoli(articoli)
    print "Totale iva inclusa : ",ritornaTotaleArticoli(articoli)


    # TotalerigheCodiciIva

    db(db.anagrafica_codici_iva).select()

    TotaleRigheCodiciIva={}



    for articolo in articoli:
        print articolo
        percentuale_iva=articolo[3]
        codice_iva_interno=articolo[12]
        
        imponibile=ritornaImponibile(articolo[6],articolo[7])
        if not TotaleRigheCodiciIva.has_key(codice_iva_interno):
            TotaleRigheCodiciIva[codice_iva_interno] = imponibile

        else:
            TotaleRigheCodiciIva[codice_iva_interno] = TotaleRigheCodiciIva[codice_iva_interno] + imponibile


           

    for k in TotaleRigheCodiciIva:
    
       aliquota_iva = db(db.anagrafica_codici_iva.codice_iva == k).select().first()["percentuale_iva"]
       imponibile=TotaleRigheCodiciIva[k]
       
       if k=="22":
           aliquota_iva="22.00"
           descrizione_imposta=""
           imposta=(imponibile*22.0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),"I",descrizione_imposta,k)

       if k=="10":
           aliquota_iva="10.00"
           descrizione_imposta=""
           imposta=(imponibile*10.0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),"I",descrizione_imposta,k)




       if k=="53":
           aliquota_iva="0.00"
           descrizione_imposta=db(db.anagrafica_codici_iva.codice_iva == k).select().first()["descrizione"]
           imposta=(imponibile*0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),"I",descrizione_imposta,k)

       if k=="54":
           aliquota_iva="0.00"
           descrizione_imposta=db(db.anagrafica_codici_iva.codice_iva == k).select().first()["descrizione"]
           imposta=(imponibile*0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),"I",descrizione_imposta,k)



    numero_linea=1
    for articolo in articoli:
        if "22" in articolo[12]:
            aliquota="22.00"
        elif "10" in articolo[12]:
            aliquota="10.00"
        else:
            aliquota="0.00"
   

        descrizione=articolo[0]+" "+articolo[1]+" "+articolo[8] #riferimento ordine
        qta=fixPrezzo(articolo[6])+".00"
        prezzo=str(articolo[7])
        codice_iva=str(articolo[12])
        importo=str("{:.2f}".format(ritornaImponibile(qta,prezzo)))

        

        fattura.addLinea(str(numero_linea),descrizione,qta,prezzo,importo,aliquota,codice_iva)
        numero_linea+=1
    

    nome_file=fattura.writeXml()
    # cwd = os.getcwd()+"/applications/gestionale/uploads/fatture/"
    # id_cliente=args['0']
    # tipo_fattura=args['1']

    # data['error']=None
    data['msg']="Tutapost"
    data['filename']=nome_file

    return json.dumps(data)


def controllaPrezzo(prezzo):
    p = str(prezzo)
    if "." not in p:
        p+=".00"
    return p

@service.jsonrpc
@service.jsonrpc2
def crea_fattura_xml_accredito(args):

    data={}
    fattura=None
    fattura=FatturaXml()
    articoli=set([])

    partitaIvaCarpal="01619570193"
    codiceFiscaleCarpal="01619570193"
    denominazioneCarpal="MICROCARP S.R.L."
    indirizzoCarpal="Strada Statale 415"
    capCarpal="26012"
    provinciaCarpal="CR"
    paeseCarpal="Castelleone"

    # Progressivo Invio
    numero_corrente_fattura = db(db.fattura).select().first()["numero_fattura"]
    numero = int(numero_corrente_fattura.split("/")[0])
    anno = int(numero_corrente_fattura.split("/")[1])
    numero +=1
    numero_fattura_da_salvare = str(numero)+"/"+str(anno)
    numeroDocumento=str(numero)

    progressivoInvio=numero_fattura_da_salvare

    

    

    
    """
    Dati cliente
    """
    id_cliente=args['0']
    dati_cliente = db(db.clienti.id == id_cliente).select().first()
    nome_cliente=dati_cliente.nome
    citta_cliente = dati_cliente.citta
    indirizzo_cliente = dati_cliente.indirizzo
    cap_cliente = dati_cliente.cap
    provincia_cliente = dati_cliente.provincia
    cf_cliente = dati_cliente.codice_fiscale
    pi_cliente = dati_cliente.partita_iva
    nazione_cliente = dati_cliente.nazione
    codice_banca = dati_cliente.codice_banca
    iban_cliente = dati_cliente.codice_iban
    dettagli_banca = db(db.anagrafica_banche.descrizione == codice_banca).select().first()
    scritta_esenzione_cliente = dati_cliente.descrizione_esenzione_iva
    annotazioni=dati_cliente.annotazioni
    codiceDestinatario=dati_cliente.codiceDestinatario
    pecDestinatario=dati_cliente.pec
    bollo_interno=dati_cliente.bollo

    dichiarazione=dati_cliente.descrizione_esenzione_iva

    if dichiarazione is not None:
            if len(dichiarazione)>0:
                    fattura.addDichiarazione(dichiarazione)
    
    """
    arguments['1']='accredito'
    arguments['2']=ente
    arguments['3'] =causale
    arguments['4'] = riferimento_ordine
    arguments['5'] = cig
    arguments['6'] = cup
    """

    causale=args['3']
    riferimento_ordine=args['4']
    cig=args['5']
    cup=args['6']

    fattura.addOrdineAcquisto(riferimento_ordine,cig,cup)

    esigibilitaIva="I"
    if "leonardo" in nome_cliente.lower():

         esigibilitaIva="S"
         try:
             ente=args['2']
             print "Trovata ente : "+ente
             
             if "ETN" in ente:
                 codiceDestinatario="DL33NSJ"

             if "SAS" in ente:
                 codiceDestinatario="OXPJRM5"
             
             if "SSI" in ente:
                 codiceDestinatario="RUZUQNZ"
             

         except:
             data['msg']="Impossibile recuperare ente per "+str(nome_cliente)
             data['error']=True
             return json.dumps(data)
    

    if codiceDestinatario is None and pecDestinatario is None:
        data['msg']="Inserire codice destinatario o pec per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if pi_cliente is None:
        data['msg']="Inserire la partita iva per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if len(codiceDestinatario)<5 and len(pecDestinatario)<5:
        data['msg']="Inserire codice destinatario o pec per il cliente "+str(nome_cliente)
        data['error']=True
        return json.dumps(data)

    if bollo_interno:
        fattura.addBollo()

    
    
    fattura.addDatiTrasmissione("IT",codiceFiscaleCarpal,progressivoInvio,codiceDestinatario,pecDestinatario)
    fattura.addCedentePrestatore("IT",partitaIvaCarpal,denominazioneCarpal)
    fattura.addSedeCedentePrestatore(indirizzoCarpal,capCarpal,paeseCarpal,provinciaCarpal,"IT")

    # Dati cliente
    fattura.addCessionarioCommittente("IT",pi_cliente.replace("IT",""),nome_cliente)
    fattura.addSedeCessionarioCommittente(indirizzo_cliente,cap_cliente,citta_cliente,provincia_cliente,"IT")

    tipoDocumento=ritornaTipoDiPagamento(args['1'])


    # Calcolo data fattura
    """
    ddts_id = db(db.ddt_da_fatturare.user_id == auth.user_id).select()
    for r in ddts_id:
        data_scelta = r.data_emissione
        
    m = datetime.datetime.strptime(data_scelta,"%d/%m/%Y").date()
        
    day_start,day_end = monthrange(m.year, m.month)
    d = str(day_end)+"/"+str(m.month)+"/"+str(m.year)
    
    start_date = datetime.datetime.strptime(d,"%d/%m/%Y")
    """
    start_date = datetime.datetime.now()

    # Creazione descrizione fattura
    descrizione_fattura=causale
    fattura.addDatiGeneraliDocumento(tipoDocumento,fixDate(start_date.strftime("%d-%m-%Y")),numeroDocumento,descrizione_fattura)
    
    # Controllare se ci possono essere più rate di pagamento

    """
    if len(righeDataScadenza)>1:
        pagamento="TP01"
    else:
        pagamento="TP02"
    
    """
    # Per ora metto sempre solo 1 rata
    pagamento="TP02"
    fattura.addCondizioniPagamento(pagamento)

    articoli=[]
    articolo=[]

    fattura.rows=[]
    lista_codici_iva =  {}
    
    importo_totale = 0
    imposta_totale = 0
    imposta_iva = 0
    lista_ddt = []
    if True:
        rows = db(db.righe_in_fattura_istantanea).select()
        for row in rows:
        
            try:
         
                
                  pagamento = db(db.clienti.id == id_cliente).select().first()["pagamento"]
                  print "Pagamento :",pagamento
                        
                  if "F.M." in pagamento:
                      fine_mese = True
                  else:
                      fine_mese = False
                      
                   
                  
                    
                  
                  
                  if not fine_mese:
                       try:
                          giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                          scadenza = datetime.datetime.now().date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                          scadenza_salvata = scadenza
                          scadenza = scadenza.strftime("%d/%m/%Y")
                         
                       except:
                           response.flash="Tipo di pagamento '{0}' non esistente in anagraficaca pagamenti".format(pagamento)
                           return locals()
                  else:
                      
                       if ("M.S." or "ms") in pagamento:
                           
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           giorni_mese_successivo = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni_mese_successivo"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           scadenza = datetime.datetime.strptime(scadenza,"%d/%m/%Y")
                           scadenza = scadenza.date() + datetime.timedelta(days = int(giorni_mese_successivo))
                           scadenza = scadenza.strftime("%d/%m/%Y") 
                           
                       else:
                           # Fine mese senza M.S.               
                           giorni_da_aggiungere = db(db.codici_pagamenti.descrizione_codice_pagamento == pagamento).select().first()["giorni"]
                           scadenza = start_date.date() + datetime.timedelta(days = int(giorni_da_aggiungere))                           
                           day_start,day_end = monthrange(scadenza.year, scadenza.month)
                           scadenza = str(day_end)+"/"+str(scadenza.month)+"/"+str(scadenza.year)
                           print "Scadenza : ",scadenza
                       
                  print "qui prima articolo"
                  print row
                  codice_articolo=row.codice_articolo
                  descrizione=row.descrizione
                  um=row.u_m
                  qta=row.qta
                  codice_iva=row.codice_iva
                  riferimento_ordine=row.riferimento_ordine
                  prezzo=row.prezzo
                  print "qui dopo articolo"
                  
                  percentuale_iva = db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["percentuale_iva"]
                  codice_iva_interno=db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["codice_iva"]
                  bollo = db(db.anagrafica_codici_iva.descrizione_codice_iva == codice_iva).select().first()["bollo_su_importi_esenti"]

                  articolo.append(codice_articolo)
                  articolo.append(descrizione)
                  articolo.append(codice_iva)
                  articolo.append(percentuale_iva)
                  articolo.append(bollo)
                  articolo.append(um)
                  articolo.append(qta)
                  articolo.append(controllaPrezzo(prezzo))
                  articolo.append(riferimento_ordine)
                  articolo.append(pagamento)
                  articolo.append(scadenza)
                  articolo.append(ritornaCondizioniPagamento(pagamento))
                  articolo.append(codice_iva_interno)

                  add=True
                  for a in articoli:
                          print a,articolo,a==articolo
                          if a==articolo:
                              add=False
                              break

                  if add:
                      if "commento" not in articolo[0]:
                          articoli.append(articolo)
                      articolo=[]
            except Exception,e:
                     
                       data['msg']="Controllare tipo pagamento per  cliente "+str(nome_cliente)+str(e)
                       data['error']=True
                       return json.dumps(data) 


    if bollo_interno:
        articolo=[]
 
        codice_iva_interno="54"
      
        articolo.append("")
        articolo.append("Imposta di bollo assolta in modo virtuale ex DM 17/06/2014")
        articolo.append("Esente Iva")
        articolo.append(0.00)
        articolo.append("")
        articolo.append("Nr")
        articolo.append("1")
        articolo.append("2.00")
        articolo.append("")
        articolo.append(pagamento)
        articolo.append(scadenza)
        articolo.append(ritornaCondizioniPagamento(pagamento))
        articolo.append(codice_iva_interno)
        articoli.append(articolo)           
                        
    def ritornaImponibile(qta,prezzo):
        try:
            imponibile= float(qta)*float(prezzo)
            print imponibile,float("%0.2f"%imponibile)
            return round(imponibile,2)
        except:
            return 0


    def ritornaTotaleArticoli(articoli):
        totale=0.0
        for articolo in articoli:
            try:
                imponibile=ritornaImponibile(articolo[6],articolo[7])
                percentualeIva=articolo[3]
                totaleIvaInclusa=imponibile + (imponibile*percentualeIva)/100
                totale+=totaleIvaInclusa
            except Exception,e:
                print e
                pass

        return str("{:.2f}".format(totale))
    


    # Dettagilio Pagamento
    articolo=articoli[0]
    dataToFix=articolo[10]
    d=dataToFix.split("/")

    if len(d[1])==1:
        d[1]="0"+d[1]

    if len(d[0])==1:
        d[0]="0"+d[1]
    
    
    d=d[2]+"-"+d[1]+"-"+d[0]
    fattura.addDettaglioPagamento(articolo[11],d,ritornaTotaleArticoli(articoli))
    print "Totale iva inclusa : ",ritornaTotaleArticoli(articoli)


    # TotalerigheCodiciIva

    db(db.anagrafica_codici_iva).select()

    TotaleRigheCodiciIva={}



    for articolo in articoli:
        percentuale_iva=articolo[3]
        codice_iva_interno=articolo[12]
        
        imponibile=ritornaImponibile(articolo[6],articolo[7])
        if not TotaleRigheCodiciIva.has_key(codice_iva_interno):
            TotaleRigheCodiciIva[codice_iva_interno] = imponibile

        else:
            TotaleRigheCodiciIva[codice_iva_interno] = TotaleRigheCodiciIva[codice_iva_interno] + imponibile


   


    for k in TotaleRigheCodiciIva:
    
       aliquota_iva = db(db.anagrafica_codici_iva.codice_iva == k).select().first()["percentuale_iva"]
       imponibile=TotaleRigheCodiciIva[k]
       
       if k=="22":
           aliquota_iva="22.00"
           descrizione_imposta=""
           if esigibilitaIva=="S":
                 descrizione_imposta=scritta_esenzione_cliente

           imposta=(imponibile*22.0)/100
           
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)), esigibilitaIva,descrizione_imposta,k)

       if k=="10":
           aliquota_iva="10.00"
           descrizione_imposta=""
           imposta=(imponibile*10.0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),esigibilitaIva,descrizione_imposta,k)




       if k=="53":
           aliquota_iva="0.00"
           descrizione_imposta=db(db.anagrafica_codici_iva.codice_iva == k).select().first()["descrizione"]
           imposta=(imponibile*0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),esigibilitaIva,descrizione_imposta,k)


       if k=="54":
           aliquota_iva="0.00"
           descrizione_imposta=db(db.anagrafica_codici_iva.codice_iva == k).select().first()["descrizione"]
           imposta=(imponibile*0)/100
           fattura.addDatiRiepilogo(aliquota_iva,str("{:.2f}".format(imponibile)),str("{:.2f}".format(imposta)),"I",descrizione_imposta,k)


    numero_linea=1
    for articolo in articoli:
        if "22" in articolo[12]:
            aliquota="22.00"
        elif "10" in articolo[12]:
            aliquota="10.00"
        else:
            aliquota="0.00"
   

        descrizione=articolo[0]+" "+articolo[1]+" "+articolo[8] #riferimento ordine
        qta=fixPrezzo(articolo[6])+".00"
        prezzo=str(articolo[7])
        codice_iva=str(articolo[12])
        importo=str("{:.2f}".format(ritornaImponibile(qta,prezzo)))
       

        

        fattura.addLinea(str(numero_linea),descrizione,qta,prezzo,importo,aliquota,codice_iva)
        numero_linea+=1
    

    nome_file=fattura.writeXml()
    # cwd = os.getcwd()+"/applications/gestionale/uploads/fatture/"
    # id_cliente=args['0']
    # tipo_fattura=args['1']

    # data['error']=None
    data['msg']="Tutapost"
    data['filename']=nome_file

    return json.dumps(data)
