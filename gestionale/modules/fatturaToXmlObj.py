# -*- coding: utf-8 -*-
import datetime
import string
import pymysql
import random
import os
"""
connection = pymysql.connect(host='localhost',
                                    user='root',
                                    password='toor',                             
                                    db='carpal',
                                    charset='utf8',
                                    cursorclass=pymysql.cursors.DictCursor)
"""
def ritornaHash(progressivo):

        connection = pymysql.connect(host='localhost',
                                    user='root',
                                    password='toor',                             
                                    db='carpal',
                                    charset='utf8',
                                    cursorclass=pymysql.cursors.DictCursor)
        
        with connection.cursor() as cursor:

                sql = 'SELECT * FROM nome_file_univoco WHERE (numero_fattura="'+progressivo+'")'
                cursor.execute(sql)
                oneRow = cursor.fetchone()
                if not oneRow:
                   r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                   sql = 'INSERT INTO nome_file_univoco (numero_fattura,random) VALUES ("'+str(progressivo)+'","'+str(r)+'")'
                   cursor.execute(sql)
                   connection.commit()
                   return r
                else:
                   return oneRow['random']

def removeFuckingSpaces(my_str):
    
    final_str = ''
    for char in my_str:
        if char in string.printable:
            final_str += char
        else:
            final_str +=" "
    return final_str


class myDDT():
    numero_ddt=""
    data_ddt=""
    riferimento_linee=[]

    def __init__(self,numero_ddt,data_ddt,riferimento_linee):
        self.numero_ddt=numero_ddt
        self.data_ddt=data_ddt
        self.riferimento_linee=riferimento_linee
  

class DettaglioPagamento():
    def __init__(self):
        self.modalitaPagamento=""
        self.dataScadenzaPagamento=""
        self.importoPagamento=""

class DatiRiepilogo():

    def __init__(self):
        self.aliquotaIva=""
        self.imponibileImporto=""
        self.imposta=""
        self.esigibilitaIva=""
        self.riferimentoNormativo=""

class Linea():

    def __init__(self):
        self.numeroLinea=""
        self.descrizione=""
        self.qta=""
        self.prezzoUnitario=""
        self.prezzoTotale=""
        self.aliquotaIva=""
        self.codice_articolo=""


class FatturaXml():

    header = '<?xml version="1.0" encoding="UTF-8"?>\n<p:FatturaElettronica versione="FPR12" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2 http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd">'
    headerClose = '</p:FatturaElettronica>'
    feHeader="<FatturaElettronicaHeader>"

    xml=[]

    linee=[]
    datiRiepilogo = []
    dettaglioPagamento= []
    bollo=False
    ddt=[]

    def addDDT(self,numero_ddt,data_ddt,riferimento_linee):
        obj=myDDT(numero_ddt,data_ddt,riferimento_linee)
        self.ddt.append(obj)
        


        
    def ritornaCodiceNaturaIva(self,codiceCarpal):

        natura=""

        if "54" in codiceCarpal:
            natura="N1"

        if "53" in codiceCarpal:
                natura="N3"
        
        if "14" in codiceCarpal:
                natura="N6" #Reverse charghe


        if "86" in codiceCarpal:
                natura="N6" #Art.74 DPR 633/72


        return natura


    def addBollo(self):
        self.bollo=True

    def addCondizioniPagamento(self,condizioniPagamento):
        self.condizioniPagamento=condizioniPagamento

    def addDettaglioPagamento(self,modalitaPagamento,dataScadenzaPagamento,importoPagamento):
        dettaglio=DettaglioPagamento()
        dettaglio.modalitaPagamento=modalitaPagamento
        dettaglio.dataScadenzaPagamento=dataScadenzaPagamento
        dettaglio.importoPagamento=importoPagamento

        self.dettaglioPagamento.append(dettaglio)

    def addDatiRiepilogo(self,aliquotaIva,imponibileImporto,imposta,esigibilitaIva,riferimentoNormativo,codice_iva_interno):

        riepilogo=DatiRiepilogo()

        riepilogo.aliquotaIva=aliquotaIva
        riepilogo.imponibileImporto=imponibileImporto
        riepilogo.imposta=imposta
        riepilogo.esigibilitaIva=esigibilitaIva
        riepilogo.riferimentoNormativo=riferimentoNormativo
        riepilogo.natura=self.ritornaCodiceNaturaIva(codice_iva_interno)
        self.datiRiepilogo.append(riepilogo)

    def addDatiTrasmissione(self,idPaese,idCodice,progressivoInvio,codiceDestinatario,pecDestinatario):
        self.idPaese=idPaese
        self.idCodice=idCodice
        self.progressivoInvio=progressivoInvio
        self.codiceDestinatario=codiceDestinatario
        self.pecDestinatario=pecDestinatario
        self.formatoTrasmissione="FPR12"
       
        if codiceDestinatario is None:
            self.codiceDestinatario=""

        if pecDestinatario is None:
            self.pecDestinatario=""


    def addLinea(self,numero,descrizione,qta,prezzoUnitario,prezzoTotale,aliquotaIva,codice_iva_interno=""):
        
        linea=Linea()

        linea.numeroLinea=numero
        linea.descrizione=descrizione.replace("&","&amp;")
        linea.qta=qta
        linea.prezzoUnitario=prezzoUnitario
        linea.prezzoTotale=prezzoTotale
        linea.aliquotaIva=aliquotaIva
        linea.natura=self.ritornaCodiceNaturaIva(codice_iva_interno)
        self.linee.append(linea)
        #print codice_iva_interno,linea.natura


        pass

    def addCedentePrestatore(self,idPaese,idCodice,denominazione):
        self.idPaeseCedente = idPaese
        self.idCodiceCedente = idCodice
        self.denominazioneCedente = denominazione

    def addSedeCedentePrestatore(self,indirizzo,cap,comune,provincia,nazione):
        self.indirizzoCedente=indirizzo
        self.capCedente=cap
        self.comuneCedente=comune
        self.provinciaCedente = provincia
        self.nazioneCedente = nazione



    def addCessionarioCommittente(self,idPaese,idCodice,denominazione):
        self.idPaeseCessionario = idPaese
        self.idCodiceCessionario = idCodice
        self.denominazioneCessionario = denominazione.replace("&","&amp;")

    def addSedeCessionarioCommittente(self,indirizzo,cap,comune,provincia,nazione):
        self.indirizzoCessionario=indirizzo
        self.capCessionario=cap
        self.comuneCessionario=comune
        self.provinciaCessionario = provincia
        self.nazioneCessionario = nazione

    

    def addOpen(self,t):
        space=self.space_index
        s = "<"+t+">"
        s = s.rjust(len(s) + space)
        self.xml.append(s)
        self.space_index +=2

    def addClose(self,t):
        
        space=self.space_index -2
        s = "</"+str(t)+">"
        s = s.rjust(len(s) + space)
        self.xml.append(s)
        self.space_index -=2

    def addValue(self,t,v):
         
         space=self.space_index
         if len(v)>0:
            s = "<"+str(t)+">"+str(v)+"</"+t+">"
         else:
             s = "<"+t+"/>"
            
         s = s.rjust(len(s) + space)
         self.xml.append(s)

    
    
    def addDichiarazione(self,dichiarazione):
            self.dichiarazione=dichiarazione

    def __init__(self):

        self.xml=[]

        self.linee=[]
        self.datiRiepilogo = []
        self.dettaglioPagamento= []
        self.bollo=False
        
        self.xml.append(self.header)
        self.space_index=2
        self.regimeFiscaleCedente="RF01"
        self.divisa="EUR"
        self.ddt=[]
        self.dichiarazione=None
        self.identificativoOrdineAcquisto=None
        self.cig=None
        self.cup=None
        self.single_ddt=None
        self.single_data_ddt=None

    def addSingleDdt(self,ddt,data):
        self.single_ddt=ddt
        self.single_data_ddt=data

        

        
    def addDatiGeneraliDocumento(self,tipoDocumento,data,numero,causale):
        self.tipoDocumento=tipoDocumento
        self.dataDocumento=data
        self.numeroDocumento=numero
        if not len(causale)>0:
            causale="Vendita"
        self.causaleDocumento=causale
   
    
    def addDatiOrdineAcquisto(self,riferimentoNumeroLinea,idDocumento,numItem):
        self.riferimentoNumeroLinea=riferimentoNumeroLinea
        self.idDocumento=idDocumento
        self.numItem=numItem
       

    def addOrdineAcquisto(self,ordine,cig,cup):
        self.identificativoOrdineAcquisto=ordine
        if cig is not None:
            if len(str(cig))>2:
                self.cig=cig
        
        if cup is not None:
            if len(str(cup))>2:
                self.cup=cup
               


    def writeXml(self):

        connection = pymysql.connect(host='localhost',
                                    user='root',
                                    password='toor',                             
                                    db='carpal',
                                    charset='utf8',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.addOpen("FatturaElettronicaHeader")
        self.addOpen("DatiTrasmissione")
        self.addOpen("IdTrasmittente")
        self.addValue("IdPaese",self.idPaese)
        self.addValue("IdCodice",self.idCodice)
        self.addClose("IdTrasmittente")

        self.addValue("ProgressivoInvio",self.progressivoInvio)
        self.addValue("FormatoTrasmissione",self.formatoTrasmissione)
        if len(self.pecDestinatario)>0:
             self.addValue("CodiceDestinatario","0000000")
             self.addValue("PECDestinatario",self.pecDestinatario)
        else:            
             self.addValue("CodiceDestinatario",self.codiceDestinatario)

        #self.addValue("ContattiTrasmittente","")
        self.addClose("DatiTrasmissione")

        ##### Cedente prestatore #####
        self.addOpen("CedentePrestatore")
        self.addOpen("DatiAnagrafici")
        self.addOpen("IdFiscaleIVA")
        self.addValue("IdPaese",self.idPaeseCedente)
        self.addValue("IdCodice",self.idCodiceCedente)
        self.addClose("IdFiscaleIVA")
        self.addOpen("Anagrafica")
        self.addValue("Denominazione",self.denominazioneCedente)
        self.addClose("Anagrafica")
        self.addValue("RegimeFiscale",self.regimeFiscaleCedente)
        self.addClose("DatiAnagrafici")
        self.addOpen("Sede")
        self.addValue("Indirizzo",self.indirizzoCedente)
        self.addValue("CAP",self.capCedente)
        self.addValue("Comune",self.comuneCedente)
        self.addValue("Provincia",self.provinciaCedente)
        self.addValue("Nazione",self.nazioneCedente)
        self.addClose("Sede")
        
        self.addOpen("Contatti")
        self.addValue("Telefono","037456603")
        self.addValue("Fax","037458562")
        self.addValue("Email","amministrazione@microcarp.com")
        self.addClose("Contatti")
        
        self.addClose("CedentePrestatore")

        #Cessionario Committente

        self.addOpen("CessionarioCommittente")
        self.addOpen("DatiAnagrafici")
        self.addOpen("IdFiscaleIVA")
        self.addValue("IdPaese",self.idPaeseCessionario)
        self.addValue("IdCodice",self.idCodiceCessionario)
        self.addClose("IdFiscaleIVA")
         
        if "leonardo" in self.denominazioneCessionario.lower():
            self.addValue("CodiceFiscale","00401990585")
       
        self.addOpen("Anagrafica")
        self.addValue("Denominazione",self.denominazioneCessionario)
        self.addClose("Anagrafica")
        
        self.addClose("DatiAnagrafici")
        self.addOpen("Sede")
        self.addValue("Indirizzo",self.indirizzoCessionario)
        self.addValue("CAP",self.capCessionario)
        self.addValue("Comune",self.comuneCessionario)
        self.addValue("Provincia",self.provinciaCessionario)
        self.addValue("Nazione",self.nazioneCessionario)
        self.addClose("Sede")
        self.addClose("CessionarioCommittente")

        self.addClose("FatturaElettronicaHeader")

      
        #### Fattura Elettronica Body ####
        self.addOpen("FatturaElettronicaBody")
        self.addOpen("DatiGenerali")
        
        self.addOpen("DatiGeneraliDocumento")
        
        self.addValue("TipoDocumento",self.tipoDocumento)
        self.addValue("Divisa",self.divisa)
        self.addValue("Data",self.dataDocumento)
        self.addValue("Numero",self.numeroDocumento)
        totale=0
        for dettaglio in self.dettaglioPagamento:
            totale+=float(dettaglio.importoPagamento)

        if self.bollo:
            self.addOpen("DatiBollo")
            self.addValue("BolloVirtuale","SI")
            self.addValue("ImportoBollo","2.00")
            self.addClose("DatiBollo")

        totale='%.2f' % totale
        self.addValue("ImportoTotaleDocumento",str(totale))
        

            

        
        if ("leonardo" not in self.denominazioneCessionario.lower()) or "TD04" in self.tipoDocumento:
            if len(self.causaleDocumento)<200:
                self.addValue("Causale",self.causaleDocumento)
            else:
                self.addValue("Causale",self.causaleDocumento[:199])
                self.addValue("Causale",self.causaleDocumento[199:])

            if ("leonardo" not in self.denominazioneCessionario.lower()):
                if self.dichiarazione is not None:
                    self.addValue("Causale",self.dichiarazione)
       
        self.addClose("DatiGeneraliDocumento")

        #DATI ORDINE ACQUISTO ##
        if self.identificativoOrdineAcquisto is not None:
            self.addOpen("DatiOrdineAcquisto")
            self.addValue("IdDocumento",str(self.identificativoOrdineAcquisto))
            
            if self.cup is not None:
                self.addValue("CodiceCUP",str(self.cup))
            
            if self.cig is not None:
                self.addValue("CodiceCIG",str(self.cig))
            
            self.addClose("DatiOrdineAcquisto")
    
        if self.single_ddt is not None:
            self.addOpen("DatiDDT")
            self.addValue("NumeroDDT",str(self.single_ddt))
            self.addValue("DataDDT",str(self.single_data_ddt))

            self.addClose("DatiDDT")

        self.addClose("DatiGenerali")

        
        #self.addOpen("DatiOrdineAcquisto")

        #self.addValue("RiferimentoNumeroLinea",self.riferimentoNumeroLinea)
        #self.addValue("IdDocumento",self.idDocumento)
        #self.addValue("NumItem",self.numItem)

        #self.addClose("DatiOrdineAcquisto")

        self.addOpen("DatiBeniServizi")
       

        for linea in self.linee:
             self.addOpen("DettaglioLinee")

             self.addValue("NumeroLinea",linea.numeroLinea)
             self.addValue("Descrizione",linea.descrizione)
             self.addValue("Quantita",linea.qta)
             self.addValue("UnitaMisura","NR")
             self.addValue("PrezzoUnitario",linea.prezzoUnitario)
             self.addValue("PrezzoTotale",linea.prezzoTotale)
             self.addValue("AliquotaIVA",linea.aliquotaIva)
             if len(linea.natura)>0:
                    self.addValue("Natura",linea.natura)

             self.addClose("DettaglioLinee")
    
        

        
        esigibilitaIva=""
        for riepilogo in self.datiRiepilogo:
            self.addOpen("DatiRiepilogo")

            self.addValue("AliquotaIVA",riepilogo.aliquotaIva)
            if len(riepilogo.natura)>0:
                self.addValue("Natura",riepilogo.natura)
            self.addValue("ImponibileImporto",riepilogo.imponibileImporto)
            self.addValue("Imposta",riepilogo.imposta)
            if not len(riepilogo.natura)>0:
                self.addValue("EsigibilitaIVA",riepilogo.esigibilitaIva)
            esigibilitaIva=riepilogo.esigibilitaIva
            if riepilogo.riferimentoNormativo is not None:
              if len(riepilogo.riferimentoNormativo)>0:
                self.addValue("RiferimentoNormativo",riepilogo.riferimentoNormativo)
            #if len(riepilogo.natura)>0:
            #      self.addValue("Natura",riepilogo.natura)



            self.addClose("DatiRiepilogo")


        self.addClose("DatiBeniServizi")


        self.addOpen("DatiPagamento")

        self.addValue("CondizioniPagamento",self.condizioniPagamento)

        for dettaglio in self.dettaglioPagamento:
            self.addOpen("DettaglioPagamento")
            self.addValue("ModalitaPagamento",dettaglio.modalitaPagamento)
            self.addValue("DataScadenzaPagamento",dettaglio.dataScadenzaPagamento)
            if "S" in esigibilitaIva:
                self.addValue("ImportoPagamento",riepilogo.imponibileImporto)
            else:
                self.addValue("ImportoPagamento",dettaglio.importoPagamento)

            
            if "leonardo" in self.denominazioneCessionario.lower():
                 self.addValue("IstitutoFinanziario","Banca Cremasca Cred.Coop.- Fil. di Madignano")
                 self.addValue("IBAN","IT98K0707657330000000607807")


            self.addClose("DettaglioPagamento")


        self.addClose("DatiPagamento")


        self.addClose("FatturaElettronicaBody")

        self.addClose("p:FatturaElettronica")

       


        nome_hash=ritornaHash(self.progressivoInvio)        
        #nome_hash=str(hash(self.progressivoInvio))[:5].replace("-","")
        cwd = os.getcwd()+"/applications/gestionale/static/uploads/fatture/"
        nome_file_reale=self.idPaese+self.idCodice+"_"+nome_hash+".xml"
        nome_file=cwd+"xml/"+self.idPaese+self.idCodice+"_"+nome_hash+".xml"
        nome_file_sql=nome_file[2:]

        if os.path.exists(nome_file):
            os.remove(nome_file)
        else:
            print("The file does not exist")

        with open(nome_file,"w") as file:
            for line in self.xml:
                file.write(line+"\n")
        

        with connection.cursor() as cursor:
             sql = 'INSERT INTO  file_xml_da_scaricare (nome_file) VALUES ("'+nome_file_sql+'")'
             cursor.execute(sql)
             connection.commit()

        return nome_file_reale

def clearStrOle(my_str):
    words=[]
    final_str = ''
    for char in my_str:
        if char in string.printable:
            final_str += char
    return final_str

def ritornaTipoDiPagamento(str):
    
    str=str.lower()

    if "fattura" in str:
        return "TD01"

    if "accredito" in str:
        return "TD04"

    if "debito" in str:
        return "TD05"

def fixDate(str):

    str=clearStrOle(str)
    try:
        return datetime.datetime.strptime(str, '%d-%m-%Y').strftime('%Y-%m-%d')
    except:
        return ""
    
def fixPrezzo(str):
    str=clearStrOle(str)
    str=str.replace(".","")
    str=str.replace(",",".")
    return str




def ritornaCondizioniPagamento(str):

    str=clearStrOle(str)
    str=str.lower()

    if "r.b." in str:
        return "MP12"

    if "rb" in str:
        return "MP12"

    if "bonif" in str:
        return "MP05"

    if "b.b." or "bb" in str:
         return "MP05"

    if "rimessa" in str:
         return "MP09"

    if "assegno" in str:
         return "MP02"

    
    

    pass

"""
fattura=FatturaXml()
fattura.addDatiTrasmissione("IT","01234567890","00001","01234567890")
fattura.addCedentePrestatore("IT","01568510190","CARPAL SRL")
fattura.addSedeCedentePrestatore("Viale gerundo","26020","Madignano","CR","IT")
fattura.addCessionarioCommittente("IT","01568510190","MICROSOFT")
fattura.addSedeCessionarioCommittente("Viale Lago gerundo","26020","Madignano","CR","IT")

fattura.addDatiGeneraliDocumento("TD01","2014-12-18","123","Riferimento fattura")
fattura.addDatiOrdineAcquisto("1","66685","1")
fattura.addCondizioniPagamento("TP01")
fattura.addDettaglioPagamento("MP01","2015-01-30","6.10")


for i in range(1,2):
    fattura.addLinea(str(i),"Descrizione 1","50.00","10.00","500.00","22.00")
    fattura.addDatiRiepilogo("22.00","100.00","22.00","I","")

fattura.writeXml()
"""

"""
Tabella campo “Natura” 

Tipologia di operazione	Causale campo natura 
Escluse	N1 – escluse (es. ex artt. 2, 3, 5, 13,15, del DPR n. 633/72)
Non soggette 	N2 – non soggette (es. ex art.7-bis, 7-ter, 7-quater, 7- quinquies, ecc. del DPR n. 633/72)
Non imponibili 	N3 – non imponibile (es. ex artt.8, 8-bis, 9, 71, 72, del DPR n. 633/72 e artt.41 e 58 del D.L. n. 331/793)
Esenti  	N4– esente (ex art.10 del DPR n.633/72)
Soggette al regime del margine	N5 – regime del margine per i beni usati /editoria/ agenzie di viaggio e turismo
Soggette a inversione contabile/reverse charge	N6 – inversione contabile (“reverse charge”) (es. ex art.74 commi 7 e 8, art.17, commi 2 e 6 del DPR n. 633/72, artt.38 e 40 del D.L. n. 331/93) 
Soggette a modalità speciali di
determinazione/assolvimento dell’Iva	N7 – IVA assolta in altro Stato UE (vendite a distanza sopra la soglia, commercio elettronico diretto verso privati)
"""
