# coding=latin-1
from fpdf import FPDF, HTMLMixin
from dns.resolver import NoMetaqueries
#from twisted.words.protocols.oscar import CAP_CHAT
import os
from barcode.writer import ImageWriter
import base64
from barcode import generate
import barcode

class MyFPDF(FPDF, HTMLMixin):
            pass

 


class CICLO_LAVORAZIONE():
    
     
     pdf = None
     html = ""
     rows = []
     
     
     def __init__(self,nome_cliente,codice_ordine_interno,riferimento_ordine_cliente,data_consegna,codice_articolo,descrizione_articolo,revisione,numero_pezzi):
         self.pdf = MyFPDF("P", "mm", "A4")
         self.nome_cliente = nome_cliente
         self.codice_ordine_interno = codice_ordine_interno
         self.riferimento_ordine_cliente = riferimento_ordine_cliente
         self.data_consegna = data_consegna
         self.codice_articolo = codice_articolo
         self.descrizione_articolo = descrizione_articolo
         self.numero_pezzi = numero_pezzi
         self.revisione = revisione
         self.rows_per_page = 11
      
     def add_row(self,nome_macchina,nome_operazione,controlli,tempo_attrezzaggio,tempo_produzione,pezzi_prodotti,note,barcode):
         record = []
         record.append(nome_macchina)
         record.append(nome_operazione)
         record.append(controlli)
         record.append(tempo_attrezzaggio)
         record.append(tempo_produzione)
         record.append(pezzi_prodotti)
         record.append(note)
         record.append(barcode)
         self.rows.append(record)
          
         
         
         
     def genera_bardcode(self,br):
         options = {}
         options["write_text"] = False
         options["text"] = 'asd'
         generated = barcode.codex.Code39(br, writer=ImageWriter(), add_checksum=False)
         generated.render(options)
         print options
	 filename = generated.save(str(br))
	 return filename
      
     def insert_rows(self):
         page_number = (len(self.rows) / self.rows_per_page) +1
         
         row_index = 0
         f = False
         self.pdf.set_fill_color(220, 220, 220)
         for page in range(0,page_number):
             if row_index  < len(self.rows):
                 print row_index,len(self.rows)-1
                 self.add_header()
                 self.add_columns()
                 print "Add header"
                 self.pdf.set_xy(1,60)
                 try:
                     for line_number in range(row_index,row_index + self.rows_per_page):
                         print row_index,self.rows_per_page
                         if line_number % 2 == 1:
                             pass
                             """
                             self.pdf.rect(2, self.pdf.get_y()-2, 24, 4, style = 'F')
                             self.pdf.rect(28, self.pdf.get_y()-2, 98, 4, style = 'F')
                             self.pdf.rect(128, self.pdf.get_y()-2, 48, 4, style = 'F')
                             self.pdf.rect(178, self.pdf.get_y()-2, 8, 4, style = 'F')
                             self.pdf.rect(188, self.pdf.get_y()-2, 20, 4, style = 'F')
                             """
                             #print "rect"
                         else:
                             f = False
                             
                         print "LINE NuMBER :",line_number
                         self.pdf.set_x(1)
                         
                         if self.rows[line_number] is not None:
                             self.pdf.set_font('', '')
                             self.pdf.set_font_size(8)
                             self.pdf.cell(8, 0, str(line_number),8,0,"",f)
                             self.pdf.cell(42, 0, self.rows[line_number][0],"",f)
                             self.pdf.cell(40, 0, self.rows[line_number][1],fill=f)
                             self.pdf.cell(19, 0, self.rows[line_number][2],fill=f)
                             self.pdf.cell(20, 0, self.rows[line_number][3],fill=f)
                             self.pdf.cell(20, 0, self.rows[line_number][4],fill=f)
                             self.pdf.cell(30, 0, self.rows[line_number][5],fill=f)
                             #self.pdf.cell(10, 0, self.rows[line_number][6],fill=f)
                             #self.pdf.image(self.genera_bardcode(self.rows[line_number][6]), x=170, self.pdf.get_y(), w=40,h=20)
                             y = self.pdf.get_y() - 3
                             self.pdf.image(self.genera_bardcode(self.rows[line_number][6]), x=176, y=y, w=34,h=18)
                             
                             self.pdf.line(1, self.pdf.get_y()+15, 178, self.pdf.get_y() + 15)
                             
                             self.pdf.set_y(self.pdf.get_y()+20)
                             row_index+=1
                         else:
                             print "QUIIIIIIIIIIII"
                             pass
                             
                 except Exception,e:
                     print e
                     pass
         
         pass
         
     def add_header(self):
         self.pdf.add_page()
         
         
         self.pdf.rect(1,2,208,7) # First Rect
         
         
         self.pdf.set_xy(3, 5)
         
         self.pdf.set_font('Times','', 10)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         descrizione = self.descrizione_articolo[:40]+".." if len(self.descrizione_articolo) > 40 else self.descrizione_articolo
         msg = " {0}     '{1}'".format(self.codice_articolo,descrizione)
         self.pdf.write(1, "Cicli di lavorazione per articolo : ")
         
         self.pdf.set_font('', '')
         self.pdf.write(1, msg)

         self.pdf.set_x(150)   
         self.pdf.set_font('', 'B')
         self.pdf.write(1, "Rev : ")
         self.pdf.set_font('', '')
         self.pdf.write(1, str(self.revisione))
      
         self.pdf.set_x(170)   
         self.pdf.set_font('', 'B')
         self.pdf.write(1, "Qta : ")
         
         self.pdf.set_font('', '')
         self.pdf.write(1, str(self.numero_pezzi))
         
         
                  
         

        
         
         self.pdf.set_font('Times','', 12)
         #self.pdf.cell(0,40,ln=1)
         #
         
         self.pdf.rect(1,10.5,208,5)
         self.pdf.set_xy(3, 12.5)
         
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Cliente : ")
         self.pdf.set_font('', '')
         self.pdf.set_font_size(8)
         self.pdf.write(1, self.nome_cliente)
         
         self.pdf.set_font('', '')
         self.pdf.set_x(self.pdf.get_string_width(self.nome_cliente)+25)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Ordine interno : ")
         self.pdf.set_font('', '')
         self.pdf.write(1, self.codice_ordine_interno)
         
         
        
         self.pdf.set_x(100)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Rif.Ord. Cliente : ")
         self.pdf.set_font('', '')
         self.pdf.write(1, self.riferimento_ordine_cliente)
         
         
         self.pdf.set_x(145)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Data consegna : ")
         self.pdf.set_font('', '')
         self.pdf.write(1, self.data_consegna)
         
        
       
         self.pdf.set_x(184)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Pag : ")
         self.pdf.set_font('', '')
         self.pdf.write(1, str(self.pdf.page_no()))
         
         
         """
         Intestazione
         """
         
         
         """
         Comandi (Start/ Sospensione / Stop)
         """
         
        
         self.pdf.image(self.genera_bardcode("INIZIO"), x=1, y=20, w=40,h=20)
         self.pdf.image(self.genera_bardcode("SOSPENSIONE"), x=90, y=20, w=40,h=20)
         self.pdf.image(self.genera_bardcode("FINE"), x=170, y=20, w=40,h=20)
         
         
         
         
         """
         Righe
         """
         
         """
         self.pdf.rect(1, 121, 208, 141)
         self.pdf.rect(1, 121, 208.1, 141)
         self.pdf.rect(1, 121, 26, 141) #larghezza codice
         self.pdf.rect(27, 121, 100, 141) #larghezza descrizione
         
         self.pdf.rect(127, 121, 50, 141) #riferimeto ordine
         self.pdf.rect(177, 121, 10, 141) #riferimeto ordine
         #self.pdf.rect(147, 121, 30, 141) #riferimeto ordine
         #self.pdf.rect(177, 121, 10.1, 141) #riferimeto ordine
         
         """
             
        
         
         #Righe intestazione righe           
         
     def add_columns(self):
         y = 50
         
         self.pdf.rect(1, 18, 208, 24)
         
         self.pdf.rect(1, y-4, 208, 250)
         self.pdf.line(1, y+4, 209, y+4)              
         
         
         self.pdf.set_xy(1,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Nr")
         
         self.pdf.line(8, y-4, 8, 275)
         self.pdf.set_xy(8,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Lavorazione")
         
         
         
         self.pdf.line(50, y-4, 50, 275)
         self.pdf.set_xy(50,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Controlli")
         
         self.pdf.line(90, y-4, 90, 275)
         self.pdf.set_xy(90,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "T. Attr.")
         
         
         self.pdf.line(110, y-4, 110, 275)
         self.pdf.set_xy(110,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(0, "T.Prod.")
         
         self.pdf.line(130, y-4, 130, 275)
         self.pdf.set_xy(130,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "P.P.")
         
         self.pdf.line(150, y-4, 150, 275)
         self.pdf.set_xy(150,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Note")
         
         self.pdf.line(178, y-4, 178, 275)
         self.pdf.set_xy(180,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Bardcode")
             
         
         self.pdf.line(1, 275, 178, 275) #Riga di chiusura
         
         
     def create_pdf(self,filename):
        
         
         
         #self.pdf.write_html(self.html)
         
         self.pdf.output('./applications/gestionale/static/lavorazioni/'+filename,'F')
         
	   




if __name__ == '__main__':
    # def __init__(self,nome_cliente,codice_ordine_interno,riferimento_ordine_cliente,data_consegna,codice_articolo,numero_pezzi)
    p = CICLO_LAVORAZIONE("Nome cliente","Codice_ordine_interno","Rif ordine","data_consegna","Codice articolo","Descrizione articolo ---------------------------------asdassssasdasdasdasdasdasdasdasdasdasdasdasdasdas-","01","numero pezzi")
   
    for x in range(9):
        p.add_row("AAAAAA"+str(x),"BBBBBB"+str(x),"HHHH"+str(x),"CCCC"+str(x),"DD"+str(x),"EE"+str(x),"FF56"+str(x),"GG"+str(x))
    
    p.insert_rows()
    p.add_columns()
      
    p.pdf.output('html.pdf','F')
    

