# coding=latin-1
from fpdf import FPDF, HTMLMixin
from dns.resolver import NoMetaqueries
#from twisted.words.protocols.oscar import CAP_CHAT
import os

class MyFPDF(FPDF, HTMLMixin):
            pass

 


class DDT():
    
     
     pdf = None
     html = ""
     rows = []
     
     
     def __init__(self,date,numero_interno_ddt,tipo,anteprima=False):
         self.pdf = MyFPDF("P", "mm", "A4")
         self.date=date
         self.numero_interno_ddt = numero_interno_ddt
         self.ddt1="Documento di trasporto (D.d.T)"
         self.ddt2="D.P.R. 472 del 14 agosto 1996"
         self.ddt3="Numero interno {0}".format(numero_interno_ddt)
         self.ddt4="del {0}".format(date)
         self.pdf.set_auto_page_break(False)
         self.rows_per_page = 26
         self.tipo = tipo
         self.anteprima = anteprima
      
     def add_row(self,codice,descrizione,riferimento_ordine,um,quantita):
         record = []
         
         if len(codice)>1:
             record.append(codice)
             record.append(descrizione)
             record.append(riferimento_ordine)
             record.append(um)
             record.append(quantita)
         else:
             record.append(codice)
             record.append(descrizione)
             record.append("")
             record.append("")
             record.append("")
             
         self.rows.append(record)
          
         
         
      
     def insert_rows(self):
         page_number = (len(self.rows) / self.rows_per_page) +1
         row_index = 0
         f = False
         self.pdf.set_fill_color(220, 220, 220)
         for page in range(0,page_number):
             if row_index  < len(self.rows):
                 print row_index,len(self.rows)-1
                 self.add_header()
                 print "Add header"
                 self.pdf.set_xy(2,132)
                 try:
                     for line_number in range(row_index,row_index + self.rows_per_page):
                         if line_number % 2 == 1:
                             self.pdf.rect(2, self.pdf.get_y()-2, 24, 4, style = 'F')
                             self.pdf.rect(28, self.pdf.get_y()-2, 98, 4, style = 'F')
                             self.pdf.rect(128, self.pdf.get_y()-2, 48, 4, style = 'F')
                             self.pdf.rect(178, self.pdf.get_y()-2, 8, 4, style = 'F')
                             self.pdf.rect(188, self.pdf.get_y()-2, 20, 4, style = 'F')
                             
                             #print "rect"
                         else:
                             f = False
                             
                         print "LINE NuMBER :",line_number
                         self.pdf.set_x(2)
                         
                         self.pdf.cell(26, 0, self.rows[line_number][0],0,0,"",f)
                         self.pdf.cell(100, 0, self.rows[line_number][1],fill=f)
                         self.pdf.cell(50, 0, self.rows[line_number][2],fill=f)
                         self.pdf.cell(18, 0, self.rows[line_number][3],fill=f)
                         self.pdf.cell(0, 0, self.rows[line_number][4],fill=f)
                         self.pdf.set_y(self.pdf.get_y()+5)
                         row_index+=1
                 except Exception,e:
                     print e
                     pass
         
         pass
         
     def add_header(self):
         self.pdf.add_page()
         img_name = "logo.png"
         #print os.getcwd()
         if not self.anteprima:
             all_link = os.getcwd()+"/applications/gestionale/static/images/logo.png"
         else:
             all_link = os.getcwd()+"/applications/gestionale/static/images/anteprima.png"
             
         
         self.pdf.image(all_link, x=1, y=5, w=209)
         self.pdf.set_font('Times','', 12)
         #self.pdf.cell(0,40,ln=1)
         #
         
         self.pdf.rect(1,50.5,208,5)
         self.pdf.set_xy(10, 52.5)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, self.ddt1)
         
         self.pdf.set_font('', '')
         self.pdf.set_x(self.pdf.get_string_width(self.ddt1)+25)
         self.pdf.write(1, self.ddt2)
         
         self.pdf.set_x(115)
         self.pdf.set_font('', 'B')
         self.pdf.write(1, self.ddt3)
         
         self.pdf.set_font('', '')
         self.pdf.set_x(150)
         self.pdf.write(1, self.ddt4)
         
         self.pdf.set_x(180)
         self.pdf.write(1, "Pag:     {0}".format(self.pdf.page_no()))
         
         """
         Intestazione
         """
         
         
         self.pdf.rect(1,58,102,30) #Cliente
         self.pdf.rect(105,58,104,30) # Lugo di consegna
         self.pdf.rect(1,90,208,30) #infos
         self.pdf.rect(1,90,208,15) #infos
         self.pdf.line(52, 90, 52, 120)
         self.pdf.line(104.5, 90, 104.5, 120)
         self.pdf.line(156, 90, 156, 120)
         
         
         
         
         """
         Righe
         """
         
         self.pdf.rect(1, 121, 208, 141)
         self.pdf.rect(1, 121, 208.1, 141)
         self.pdf.rect(1, 121, 26, 141) #larghezza codice
         self.pdf.rect(27, 121, 100, 141) #larghezza descrizione
         
         self.pdf.rect(127, 121, 50, 141) #riferimeto ordine
         self.pdf.rect(177, 121, 10, 141) #riferimeto ordine
         #self.pdf.rect(147, 121, 30, 141) #riferimeto ordine
         #self.pdf.rect(177, 121, 10.1, 141) #riferimeto ordine
         
         self.pdf.rect(1, 121, 208, 6)
         self.pdf.rect(1, 121, 208, 6)
         
         
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
         
         
         
         
         self.pdf.set_xy(8,124)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Codice")
         
         self.pdf.set_xy(70,124)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Descrizione")
         
         self.pdf.set_xy(130,124)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Rif. ordine")
         
         self.pdf.set_xy(178,124)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(0, "U.M")
         
         self.pdf.set_xy(190,124)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Quantita'")
         
         
         
         
         """
         Footter
         """
         self.pdf.rect(1, 264, 208, 30)
         self.pdf.line(1, 279, 209, 279)
         self.pdf.line(1 +69, 264, 1+69, 294)
         self.pdf.line(1 +69*2, 264, 1+69*2, 294)
          
         
         self.pdf.set_xy(10,267)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Aspetto esteriore dei beni")
         
         self.pdf.set_xy(10 + 80,267)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Numero colli")
         
         self.pdf.set_xy(16 + 75*2,267)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, "Porto")
         
         
         
         
         
         
         self.pdf.set_xy(43,60)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(12)
         self.pdf.write(1, self.tipo)
         
         self.pdf.set_xy(139,60)
         self.pdf.write(1, "Luogo di consegna")
         
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
         self.pdf.cell(50,5,self.c_nome,0,2)
         self.pdf.cell(50,5,self.c_indirizzo,0,2)
         self.pdf.cell(50,5,self.c_cap + "  "+self.c_citta + "                     "+self.c_provincia,0,2)
         #self.pdf.cell(50,5,"Partita IVA :    "+self.pi,0,2)
         
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
         
         
         
         
         
     def intestazione(self,nome,citta,indirizzo,cap,provincia,pi,nazione="",cf=""):    
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
           
     def info_trasporto(self,trasporto,vettore,causale,inizio_trasporto,residenza,data_ritiro):
         self.trasporto = trasporto
         self.vettore = vettore
         self.causale = causale
         self.residenza = residenza
         self.data_ritiro = data_ritiro
         self.inizio_trasporto = inizio_trasporto
         
        
     def footer(self,aspetto_esteriore,numero_colli,porto,annotazioni,peso):
         self.aspetto_esteriore = aspetto_esteriore
         self.numero_colli = numero_colli
         self.porto=porto
         self.annotazioni= annotazioni
         self.peso = peso
         
     
         
         
     def create_pdf(self):
        
         
         
         #self.pdf.write_html(self.html)
         
         self.pdf.output('./applications/gestionale/static/html.pdf','F')
         
	   

"""
pdf=MyFPDF()
#First page
pdf.add_page()
pdf.write_html(html)
pdf.output('html.pdf','F
"""
"""
if __name__ == '__main__':
    p = DDT("28/11/2017","1")
    p.intestazione("LEONARDO SPA", "ROMA","PIAZZA MONTE GRAPPA 4", "00195", "RM", "IT", "123456", "00881841001")
    p.consegna("LEONARDO SPA", "CAMPI BISENZIO", "VIA ALBERT EINSTEIN 35", "50013", "FI")
    p.info_trasporto("Vettore", "TNT GLOBAL EXPRESS SPA", "VENDITA","29/11/16", "LODI", "28/11/16")
    p.footer("scatola su bancale","100","ASSEGNATO","NOTE","123")
    for x in range(130):
        p.add_row("AAAAAA"+str(x),"BBBBBB"+str(x),"CCCCCCC"+str(x),"NR",str(x))
    
    p.insert_rows()
    
        
    p.create_pdf()
    
"""
