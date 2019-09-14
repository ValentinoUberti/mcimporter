# coding=latin-1
from fpdf import FPDF, HTMLMixin
from dns.resolver import NoMetaqueries
#from twisted.words.protocols.oscar import CAP_CHAT
import os
import datetime
from money import *
from datetime import timedelta
from calendar import monthrange
class MyFPDF(FPDF, HTMLMixin):
            pass

 


class FATTURA():
    
     
     pdf = None
     html = ""
     rows = []
     
     
     def __init__(self,tipo_fattura,date,numero_interno_fattura,anteprima=False):
         self.pdf = MyFPDF("P", "mm", "A4")
         self.date=date
         self.numero_interno_ddt = numero_interno_fattura
         self.tipo_fattura=tipo_fattura
         self.valuta="Valuta : EURO"
         self.numero_fattura="Numero fattura {0}".format(numero_interno_fattura)
         self.data_fattura="del {0}".format(date)
         self.pdf.set_auto_page_break(False)
         self.rows_per_page = 26
         self.rows=[]
         self.f2_list=[]
         self.anteprima = anteprima
      
     def add_row(self,codice,descrizione,riferimento_ordine,um,quantita,prezzo,sconti,importo,ci):
         record = []
         record.append(codice)
         record.append(descrizione)
         record.append(riferimento_ordine)
         record.append(um)
         record.append(quantita)
         record.append(prezzo)
         record.append(sconti)
         record.append(str(importo))
         record.append(ci)
         
         self.rows.append(record)
          
         
     def print_footer(self):
         
          self.pdf.set_xy(2,242)
          self.pdf.set_font_size(8)
          f=False
          self.pdf.cell(34, 0, self.totale_merce,0,0,"",f)
          self.pdf.cell(30, 0, self.sconto,0,0,"",f)
          self.pdf.cell(30, 0, self.netto_merce,0,0,"",f)
          self.pdf.cell(24, 0, self.spese_varie,0,0,"",f)
          self.pdf.cell(30, 0, self.spese_trasporto,0,0,"",f)
          self.pdf.cell(30, 0, self.totale_imponibile,0,0,"",f)
          self.pdf.cell(26, 0, self.totale_imposta,0,0,"",f)
          
          print "SCRITTO1"
          pass
      
     def print_total(self):
          self.pdf.set_font_size(12)
          self.pdf.set_xy(180,260)
          
          self.pdf.cell(34, 0, self.totale_documento,0,0,"")
          print "SCRITTO2"
         
     def print_footer_2(self):
         
          
          self.pdf.set_font_size(8)
          y = 250
          for row in self.f2_list:
                self.pdf.set_xy(2,y+5)
                self.pdf.set_font_size(8)
                print row
                f=False
                self.pdf.cell(34, 0, row[0],0,0,"",f)
                self.pdf.cell(30, 0, row[1],0,0,"",f)
                self.pdf.cell(24, 0, row[2],0,0,"",f)
                self.pdf.cell(30, 0, row[3],0,0,"",f)
                self.pdf.cell(30, 0, row[4],0,0,"",f)
                self.pdf.cell(30, 0, row[5],0,0,"",f)
                y +=5
          
          
          
          if not "/" in self.pagamento:
              self.pdf.set_xy(90,283)
              self.pdf.set_font_size(10)
              self.pdf.cell(30, 0, self.scadenza + "   " + self.totale_documento,0,0,"")
              print "SCRITTO3"
          else:
              self.pdf.set_xy(60,283)
              
              self.pdf.set_font_size(10)
              s=self.pagamento
              
              res = self.totale_documento.split(',')
              print res
              full_price = float('.'.join([res[0].replace('.', ''), res[1]]))
              
              first_half = round(full_price / 2,2)
              second_half= full_price - first_half
              
              print first_half,second_half
              
              importo1 = Money(str(first_half),"EUR")
              importo1 = importo1.format("it_IT").encode('ascii', 'ignore').decode('ascii')


              importo2 = Money(str(second_half),"EUR")
              importo2 = importo2.format("it_IT").encode('ascii', 'ignore').decode('ascii')
                            
              
              
              st = int(s[s.index("/")+1:s.index("/")+4]) - int(s[s.index("/")-3:s.index("/")])
              
              second_date = datetime.datetime.strptime(self.scadenza,"%d/%m/%Y").date()
              first_date = second_date - datetime.timedelta(days = int(st) +1)
              
              first_date = first_date.strftime("%d/%m/%Y")
                  
              second_date = second_date.strftime("%d/%m/%Y")
              
              self.pdf.cell(50, 0, first_date + "   " + importo1,0,0,"")
              self.pdf.cell(30, 0, second_date + "   " + importo2,0,0,"")
              
              
              
              
              
          
     def insert_rows(self):
         page_number = (len(self.rows) / self.rows_per_page) +1
         row_index = 0
         f = False
         self.pdf.set_fill_color(220, 220, 220)
         for page in range(0,page_number):
             
                 
             if row_index  < len(self.rows):
                 #print row_index,len(self.rows)-1
                 self.add_header()
                 print "Add header"
                 print "righe totali {0} riga corrente {1}".format(len(self.rows),row_index)
                 if (page < (page_number -1)):
                     print "MINORE : current page {0} page number {1}".format(page,page_number -1)
                     print "riga corrente {0} righe massime {1}",format(row_index,str(self.rows_per_page))
                     
                     if not row_index + self.rows_per_page == len(self.rows):
                         self.pdf.set_xy(164, 281)
                         self.pdf.set_font('', '')
                         self.pdf.set_font_size(18)
                         self.pdf.write(1, "SEGUE >>>")
                         self.pdf.set_xy(2,100)
                     else:
                         """
                         Print footer data
                         """
                         print "oCIO : current page {0} page number {1}".format(page,page_number)
                         #print "SONO QUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
                         self.pdf.set_font('', '')
                         self.print_footer()
                         self.print_footer_2()
                         self.print_total()
                         print "fINITO INTERNO"
                         pass
                         
                 else:
                     """
                     Print footer data
                     """
                     #print "SONO QUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
                     self.pdf.set_font('', '')
                     self.print_footer()
                     self.print_footer_2()
                     self.print_total()
                     print "FINITOOOOOOOOOOO"
                     pass
                 try:
                     self.pdf.set_xy(2,100)
                     self.pdf.set_font_size(8)
                     for line_number in range(row_index,row_index + self.rows_per_page):
                         if line_number % 2 == 1:
                             self.pdf.rect(2, self.pdf.get_y()-2, 24, 4, style = 'F')
                             self.pdf.rect(28, self.pdf.get_y()-2, 74, 4, style = 'F')
                             self.pdf.rect(106, self.pdf.get_y()-2, 20, 4, style = 'F')
                             self.pdf.rect(130, self.pdf.get_y()-2, 6, 4, style = 'F')
                             self.pdf.rect(140, self.pdf.get_y()-2, 8, 4, style = 'F')
                             self.pdf.rect(151, self.pdf.get_y()-2, 15, 4, style = 'F')
                             self.pdf.rect(168, self.pdf.get_y()-2, 10, 4, style = 'F')
                             self.pdf.rect(181, self.pdf.get_y()-2, 16, 4, style = 'F')
                             self.pdf.rect(201, self.pdf.get_y()-2, 7, 4, style = 'F')                             
                             #print "rect"
                         else:
                             f = False
                             
                         #print "LINE NuMBER :",line_number
                         self.pdf.set_x(2)
                         #print self.rows[line_number]
                         self.pdf.cell(26, 0, self.rows[line_number][0],0,0,"",f)
                         self.pdf.cell(80, 0, self.rows[line_number][1],fill=f)
                         self.pdf.cell(22, 0, self.rows[line_number][2],fill=f)
                         self.pdf.cell(12, 0, self.rows[line_number][3],fill=f)
                         self.pdf.cell(8, 0, self.rows[line_number][4],fill=f)
                         self.pdf.cell(14, 0, self.rows[line_number][5],align='R',fill=f)
                         self.pdf.cell(14, 0, self.rows[line_number][6],fill=f)
                         self.pdf.cell(20, 0, self.rows[line_number][7],align='R',fill=f)
                         self.pdf.cell(10, 0, self.rows[line_number][8],align='R',fill=f)
                         self.pdf.set_y(self.pdf.get_y()+5)
                         row_index+=1
                 except Exception,e:
                     print e
                     pass
         
         pass
         
     def add_header(self):
         self.pdf.add_page()
         #img_name = "logo.png"
         #print os.getcwd()
         
         if not self.anteprima:
             all_link = os.getcwd()+"/applications/gestionale/static/images/logo.png"
         else:
             all_link = os.getcwd()+"/applications/gestionale/static/images/anteprima.png"
             
         #all_link = "logo.png"
         self.pdf.image(all_link, x=1, y=2, w=209)
         #self.pdf.image(img_name, x=1, y=2, w=209)

	 self.pdf.set_font('Times','', 12)
         #self.pdf.cell(0,40,ln=1)
         #
         
         self.pdf.rect(1,50.5,208,5)
         self.pdf.set_xy(10, 52.5)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, self.tipo_fattura)
         
         self.pdf.set_font('', '')
         self.pdf.set_x(self.pdf.get_string_width(self.tipo_fattura)+25)
         self.pdf.write(1, self.valuta)
         
         self.pdf.set_x(115)
         self.pdf.set_font('', 'B')
         self.pdf.write(1, self.numero_fattura)
         
         self.pdf.set_font('', '')
         self.pdf.set_x(150)
         self.pdf.write(1, self.data_fattura)
         
         self.pdf.set_x(180)
         self.pdf.write(1, "Pag:     {0}".format(self.pdf.page_no()))
         
         """
         Intestazione
         """
         
         
         self.pdf.rect(1,58,102,30) #Cliente
         self.pdf.rect(105,58,104,30) # Lugo di consegna
                 
         
         
         
         """
         Righe
         """
         
         #self.pdf.rect(1, 121, 208, 141)
         self.pdf.rect(1, 90, 208.1, 141) #Angolo destro righe quantità
         #self.pdf.rect(1, 90, 26, 141) #larghezza codice
         #self.pdf.rect(27, 90, 100, 141) #larghezza descrizione
         
         #self.pdf.rect(127, 90, 50, 141) #riferimeto ordine
         #self.pdf.rect(177, 90, 10, 141) #riferimeto ordine
         #self.pdf.rect(147, 121, 30, 141) #riferimeto ordine
         #self.pdf.rect(177, 121, 10.1, 141) #riferimeto ordine
         
         
         self.pdf.rect(1, 90, 208, 6)
         self.pdf.rect(1, 90, 208, 6)
         
         """
         
         self.pdf.set_xy(8,92)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Trasporto a mezzo")
         
         
         
         self.pdf.set_xy(57,92)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Causale del trasporto")
         
         self.pdf.set_xy(106,92)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Inizio trasporto (data/ora)")
         
         self.pdf.set_xy(158.5,92)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Firma del conducente")
         
         self.pdf.set_xy(8,107)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Vettore")
         
         self.pdf.set_xy(57,107)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Residenza o domicilio")
         
         self.pdf.set_xy(106,107)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Data e ora del ritiro")
         
         self.pdf.set_xy(158.5,107)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Firma del conducente")
         
         
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         
         
         self.pdf.set_xy(8,99)
         self.pdf.write(1, self.trasporto)
         
         self.pdf.set_xy(57,99)
         self.pdf.write(1, self.causale)
         
         self.pdf.set_xy(106,99)
         self.pdf.write(1, self.inizio_trasporto)
         
         self.pdf.set_xy(8,114)
         self.pdf.write(1, self.vettore)
         
         self.pdf.set_xy(57,114)
         self.pdf.write(1, self.residenza)
         
         self.pdf.set_xy(106,114)
         self.pdf.write(1, self.data_ritiro)
         
         """
         
         
         self.pdf.set_xy(8,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Codice")
         self.pdf.line(27, 90, 27, 231)
         
         self.pdf.set_xy(50,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Descrizione")
         self.pdf.line(103, 90, 103, 231)
         
         self.pdf.set_xy(104,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Rif Vs. ordine")
         self.pdf.line(128, 90, 128, 231)
    
         self.pdf.set_xy(129,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(0, "U.M")
         self.pdf.line(138, 90, 138, 231)
         
         self.pdf.set_xy(140,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Q.ta")
         self.pdf.line(150, 90, 150, 231)
         
         self.pdf.set_xy(154,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Prezzo")
         self.pdf.line(167, 90, 167, 231)
         
         self.pdf.set_xy(168,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Sconti")
         self.pdf.line(180, 90, 180, 231)
         
         self.pdf.set_xy(184,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Importo")
         self.pdf.line(200, 90, 200, 231)
         
         self.pdf.set_xy(201,93)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "C.I.")
         
         
         
         
         
         """
         Footter
         """
         self.pdf.rect(1, 234, 208, 52)
         #self.pdf.line(1, 279, 209, 279)
         #self.pdf.line(1 +69, 264, 1+69, 294)
         #self.pdf.line(1 +69*2, 264, 1+69*2, 294)
         self.pdf.rect(1, 286, 208, 4)
          
         
         self.pdf.set_xy(2,237)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(7)
         self.pdf.write(1, "Totale merce")
         
         self.pdf.set_xy(36,237)
         self.pdf.write(1, "Sconto %")
         
         self.pdf.set_xy(66,237)
         self.pdf.write(1, "Netto merce")
         
         self.pdf.set_xy(96,237)
         self.pdf.write(1, "Spese varie")
         
         self.pdf.set_xy(120,237)
         self.pdf.write(1, "Spese trasporto")
         
         self.pdf.set_xy(150,237)
         self.pdf.write(1, "Totale imponibile")
         
         self.pdf.set_xy(180,237)
         self.pdf.write(1, "Totale imposta")
        
         self.pdf.line(1, 246, 209, 246)
         self.pdf.line(1, 270, 209, 270)
         self.pdf.line(1, 276, 209, 276)
         
         self.pdf.set_xy(30,273)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "CONTRIBUTO AMBIENTALE CONAI ASSOLTO")
         
         self.pdf.set_xy(160,273)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "MADE IN ITALY")
         
         
         self.pdf.set_xy(90,277)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(6)
         self.pdf.write(1, "Scadenza rate e relativo importo")
         
         
         self.pdf.set_xy(2,250)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(7)
         self.pdf.write(1, "Codice Iva")
         self.pdf.line(18, 246, 18, 270)
         
         self.pdf.set_xy(36,250)
         self.pdf.write(1, "Spese accessorie")
         self.pdf.line(60, 246, 60, 270)
        
         self.pdf.set_xy(66,250)
         self.pdf.write(1, "Imponibile")
         self.pdf.line(86, 246, 86, 270)
         
         self.pdf.set_xy(96,250)
         self.pdf.write(1, "Iva")
         self.pdf.line(110, 246, 110, 270)
         
         self.pdf.set_xy(120,250)
         self.pdf.write(1, "Imposta")
         self.pdf.line(140, 246, 140, 270)
         
         self.pdf.set_xy(150,250)
         self.pdf.write(1, "Note")
         self.pdf.line(170, 246, 170, 270)
         
         self.pdf.set_xy(180,250)
         self.pdf.write(1, "Tot. documento")
         
         dicitura = """CONDIZIONI DI VENDITA : la merca viaggia ad esclusivo rischio e pericolo del compratore, anche se venduta porto franco. \nNon si accettano reclami trascorsi 8 giorni dal ricevimento della merce."""
         dicitura2 = """Per qualsiasi controversia e' competente il Foro di emissione. In caso di ritardato pagamento decorrono gli interessi commerciali d'uso. Le eventuali spese di bolli per l'emmisioni di R.B. sono a carico del compratore."""
               
         self.pdf.set_xy(1,292)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(6)
         self.pdf.cell(0,0, dicitura,0,0)
         self.pdf.set_xy(1,293)
         self.pdf.cell(0,3, dicitura2)
         
         
         
         self.pdf.set_xy(43,60)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Cliente")
         
         self.pdf.set_xy(139,60)
         self.pdf.write(1, "Dettaglio")
         
         """
         Cliente
         """
         
         self.pdf.set_xy(2,65)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         
         
         
         self.pdf.cell(50,5,self.nome,0,2)
         self.pdf.cell(50,5,self.indirizzo,0,2)
         self.pdf.cell(50,5,self.cap + "  "+self.citta + "        "+self.provincia,0,2)
         self.pdf.cell(50,5,"Partita IVA :    "+self.pi,0,2)
         
         self.pdf.set_xy(106,65)
         self.pdf.cell(50,4,"Codice cliente : " + self.codice_cliente,0,2)
         self.pdf.cell(50,4,"Banca : " +self.banca,0,2)
         self.pdf.cell(50,4,"Iban : "+self.iban,0,2)
         self.pdf.cell(50,4,"Pagamento :    "+self.pagamento,0,2)
         #self.pdf.cell(50,4,self.da_ddt,0,2)
         print "SELF IBAN : ",self.iban
         
         """
         self.pdf.set_xy(22,267+15)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.cell(0,0, "Annotazioni")
         
         self.pdf.set_xy(26+69,267+15)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.cell(0,0, "Peso Kg")
         
         self.pdf.set_xy(18+69*2,267+15)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.cell(0,0, "Firma destinatario")
         
         
         self.pdf.set_xy(2,267+8)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         self.pdf.write(0, self.aspetto_esteriore)
         
         self.pdf.set_xy(2,267+20)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         self.pdf.write(0, self.annotazioni)
         
         self.pdf.set_xy(2+69+30,267+8)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         self.pdf.write(0, self.numero_colli)
         
         self.pdf.set_xy(2+69*2+23,267+8)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         self.pdf.write(0, self.porto)
                        
                        
         self.pdf.set_xy(2+69+30,267+20)
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         self.pdf.write(0, self.peso)
         
         """
         
         
         
     def intestazione(self,nome,citta,indirizzo,cap,provincia,nazione="",cf="",pi=""):    
         self.nome = nome
         self.citta = citta
         self.indirizzo = indirizzo
         self.cap = cap
         self.provincia = provincia
         self.nazione = nazione
         self.cf = cf
         self.pi = pi
         
         
     
     def consegna(self,c_nome,c_indirizzo,c_cap,c_citta,c_provincia):
         self.c_nome = c_nome.lstrip()
         self.c_citta = c_citta.lstrip()
         self.c_indirizzo = c_indirizzo.lstrip()
         self.c_cap = c_cap.lstrip()
         self.c_provincia = c_provincia.lstrip()
     
     def dettaglio(self,codice_cliente,banca,iban,pagamento,scadenza):
         print "IBAN RICEVUTO IN DETTAGLIO : ",iban
    	 self.codice_cliente = codice_cliente.lstrip()
    	 self.banca = banca.lstrip()
    	 self.iban = iban
         print "IBAN IN DETTAGLIO : ",self.iban
    	 self.pagamento = pagamento.lstrip()
         #self.da_ddt = da_ddt
         self.scadenza = scadenza    

     def info_trasporto(self,trasporto,vettore,causale,inizio_trasporto,residenza,data_ritiro):
         self.trasporto = trasporto
         self.vettore = vettore
         self.causale = causale
         self.residenza = residenza
         self.data_ritiro = data_ritiro
         self.inizio_trasporto = inizio_trasporto
         
        
     def footer(self,totale_merce,sconto,netto_merce,spese_varie,spese_trasporto,totale_imponibile,totale_imposta):
         self.totale_merce = totale_merce
         self.sconto = sconto
         self.netto_merce=netto_merce
         self.spese_varie= spese_varie
         self.spese_trasporto = spese_trasporto
         self.totale_imponibile = totale_imponibile
         self.totale_imposta = totale_imposta
         
     def footer_2(self,codice_iva,spese_accessorie,imponibile,iva,imposta,bolli):
         record = []
         
         record.append(codice_iva)
         record.append(spese_accessorie)
         record.append(imponibile)
         record.append(iva)
         record.append(imposta)
         record.append("")
         
         self.f2_list.append(record)
         
        
     def totale(self,totale):
         self.totale_documento = totale
     
         
         
     def create_pdf(self):
        
         
         
         #self.pdf.write_html(self.html)
         
         self.pdf.output('./applications/gestionale/static/fattura.pdf','F')
	     #self.pdf.output('html.pdf','F')
         
	   

"""
pdf=MyFPDF()
#First page
pdf.add_page()
pdf.write_html(html)
pdf.output('html.pdf','F
"""

if __name__ == '__main__':
    p = FATTURA("FATTURA DIFFERITA","28/11/2017","1/2017")
    p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    #p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    p.dettaglio("0000122","Banca sella","Iban","RIBA 90 GG D.F. F.M.","11/11/2017")
    #def dettaglio(self,codice_cliente,banca,iban,pagamento,da_ddt):
    #p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    p.footer("Totale merce","Sconto","Netto merce","spese varie","spese_trasporto","totale_imponibile","Totale imposta")
    p.footer_2("CodIva","Spese accessorie","Imponibile","Iva","Imposta","Bolli")
    p.footer_2("CodIva2","Spese accessorie2","Imponibile2","Iva2","Imposta2","Bolli2")
    p.totale("145,676.45")
    
    
    
    
    for x in range(51):
        p.add_row("AAAAAA"+str(x),"BBBBBBdsfdsfdsfdsfsdfsdfsdfsdfsdffgdf"+str(x),"CCCCCCC"+str(x),"NR",str(x),"DDDDDDD"+str(x),"EEEE"+str(x),"FFFFFF"+str(x),"G"+str(x))
    
    p.insert_rows()
    
        
    p.create_pdf()
    

