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

 


class CONTROLLO_PRODUZIONE():
    
     
     pdf = None
     html = ""
     rows = []
     
     
     def __init__(self,nome_intestazione,tipo_intestazione):
         self.pdf = MyFPDF("P", "mm", "A4")
         
         self.nome_intestazione = nome_intestazione
         self.tipo_intestazione=tipo_intestazione
         self.pdf.set_auto_page_break(False)
         self.rows_per_page = 16
         self.rows=[]
         
     def add_row(self,lavorazione,descrizione):
         record = []
         record.append(lavorazione)
         record.append(descrizione)
         self.rows.append(record)
          
         
     def print_footer(self):
         
          self.pdf.set_xy(2,252)
          self.pdf.set_font_size(8)
          f=False
          #self.pdf.cell(34, 0, self.br,0,0,"",f)
          self.pdf.image(self.br, x=170, y=260, w=34)
          
          
          
          self.pdf.set_font('Times','', 12)
          self.pdf.rect(2,260,160,5)
          self.pdf.set_xy(5, 262)
          self.pdf.set_font('', 'B')
          self.pdf.set_font_size(8)
          self.pdf.write(1, "Benestare alla spedizione    | SI       | NO       | Sigla                                  | Data")
          
          self.pdf.rect(2,268,160,20)
          
          self.pdf.set_xy(5, 270)
          if self.ente=="Nessuno":
             self.pdf.write(1,"Note")
          else:
             self.pdf.write(1,"Ente di destinazione")
             self.pdf.set_font('', '')
             self.pdf.set_font_size(12)
             self.pdf.set_xy(5, 276)
             self.pdf.write(1,self.ente)
          
          pass

          self.pdf.set_xy(5,282)
          self.pdf.set_font_size(10)
          strOk="Giac. "+self.giacenza+"      Ubic. "+self.ubicazione+"      Cart. "+self.cartella+ "      Peso. "+self.peso
          self.pdf.write(1,strOk)
      
         
          
     def insert_rows(self):
         self.pdf.set_font('Times','', 12)
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
                         #print "fINITO INTERNO"
                         pass
                         
                 else:
                     """
                     Print footer data
                     """
                     #print "SONO QUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
                     self.pdf.set_font('', '')
                     self.print_footer()
                     print "FINITOOOOOOOOOOO"
                     pass
                 try:
                     self.pdf.set_xy(2,40)
                     self.pdf.set_font_size(6)
                     y2=6
                     y3=13
                     for line_number in range(row_index,row_index + self.rows_per_page):
                         if line_number % 2 == 1:
                             self.pdf.line(1, self.pdf.get_y()-y2-1, 200, self.pdf.get_y()-y2-1)
                             self.pdf.line(1, self.pdf.get_y()+y2+2, 200, self.pdf.get_y()+y2+2)
                             self.pdf.rect(1.5, self.pdf.get_y()-y2, 5, y3, style = 'F')
                             self.pdf.rect(7.5, self.pdf.get_y()-y2, 32, y3, style = 'F')
                             self.pdf.rect(40.5, self.pdf.get_y()-y2, 29, y3, style = 'F')
                             self.pdf.rect(70.5, self.pdf.get_y()-y2, 9, y3, style = 'F')
                             self.pdf.rect(80.5, self.pdf.get_y()-y2, 19, y3, style = 'F')
                             self.pdf.rect(100.5, self.pdf.get_y()-y2, 19, y3, style = 'F')
                             self.pdf.rect(120.5, self.pdf.get_y()-y2, 17, y3, style = 'F')
                             self.pdf.rect(138.5, self.pdf.get_y()-y2, 25, y3, style = 'F')
                             self.pdf.rect(164.5, self.pdf.get_y()-y2, 36, y3, style = 'F')

                             
                             #print "rect"
                         else:
                             f = False
                             
                         self.pdf.set_font('Times','', 10)
                         #print "LINE NuMBER :",line_number
                         self.pdf.set_x(2)
                         #print self.rows[line_number]
                         self.pdf.cell(1, 0, str(line_number+1),0,0,"",f)
                         #self.pdf.cell(21, 0, self.rows[line_number][0],0,0,"",f)
                         self.pdf.set_font('Times','', 12)
                         self.multi_line(7,self.rows[line_number][0],f,11)
                         self.pdf.set_x(40)
                         #self.pdf.cell(80, 0, self.rows[line_number][1],fill=f)
                         self.multi_line(40,self.rows[line_number][1],f,12)
                         self.pdf.set_y(self.pdf.get_y()+14)
                         row_index+=1
                 except Exception,e:
                     print e
                     pass
         
         pass
      
     def multi_line(self,x_pos,line,f,car):
         
         print "in multi line"
         numero_caratteri = car
         lines = int(len(line) // numero_caratteri)
         x=0
         y=0
         for y in range(-lines,lines,3):
             self.pdf.set_x(x_pos)
             self.pdf.cell(x_pos, y*2.5, line[x:x+numero_caratteri].lstrip(),0,0,"",f)
             
             x+=numero_caratteri
         
         reminder = len(line) % numero_caratteri
         if reminder >0:
             self.pdf.set_x(x_pos)
             self.pdf.cell(x_pos, y*3+7, line[x:].lstrip(),0,0,"",f)
             
                 
         
     def add_header(self):
         self.pdf.add_page()
         
	 
	 """
	 Primo rettangolo in alto
         """
	 self.pdf.set_font('Times','', 12)
         self.pdf.rect(1,2,208,5)
         self.pdf.set_xy(10, 4)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, self.nome_intestazione)
         
         self.pdf.set_x(80)
         self.pdf.write(1, self.tipo_intestazione)
         
         self.pdf.set_x(180)
         self.pdf.write(1, "Pag:     {0}".format(self.pdf.page_no()))
         
         
         """
	 Secondo rettangolo in alto
         """
	 self.pdf.set_font('Times','', 12)
         self.pdf.rect(1,8,208,12)
         self.pdf.set_xy(2, 10)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Cliente : ")
         self.pdf.set_font('', '')
         self.pdf.write(1, self.cliente)
         
         
         
         self.pdf.set_xy(110, 10)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Codice articolo : ")
         self.pdf.set_font_size(12)
         self.pdf.set_font('', '')
         self.pdf.write(1, self.codice_articolo)
         
         
         self.pdf.set_xy(166, 10)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Revisione : ")
         self.pdf.set_font_size(12)
         self.pdf.set_font('', '')
         self.pdf.write(1, self.revisione)
         
         
         self.pdf.set_xy(166, 16)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Numero pezzi : ")
         self.pdf.set_font_size(12)
         self.pdf.set_font('', '')
         self.pdf.write(1, self.numero_pezzi)
         
         
         self.pdf.set_font('Times','', 12)
        
         self.pdf.set_xy(2, 16)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Nr. Ordine : ")
         self.pdf.set_font_size(12)
         
         self.pdf.set_font('', '')
         self.pdf.write(1, self.rif_ordine)
         
         
         
         self.pdf.set_xy(110, 16)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(8)
         self.pdf.write(1, "Data consegna : ")
         self.pdf.set_font('', '')
         self.pdf.set_font_size(12)
         self.pdf.write(1, self.scadenza)
         
         self.pdf.set_font('', '')
         
         
                
         
         
         y = 30
         y4 = 256
         self.pdf.line(2, y+5, 200, y+5)
         
         self.pdf.set_xy(2,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "N")
         self.pdf.line(7, y, 7, y4)
         
         
         self.pdf.set_xy(8,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Operazione")
        
         x=40
         self.pdf.line(x, y, x, y4)
         self.pdf.set_xy(x,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.write(1, "Controlli")
         
         
         self.pdf.line(70, y, 70, y4) 
         self.pdf.set_xy(70,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Pezzi")
         self.pdf.set_xy(70,y+3)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Prodotti")
         
         
         
         self.pdf.line(80, y, 80, y4)
         self.pdf.set_xy(80,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Pezzi")
         self.pdf.set_xy(80,y+3)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Controllati")
         
         
         
         self.pdf.line(100, y, 100, y4)
         self.pdf.set_xy(100,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Tempo attr.")
         self.pdf.set_xy(100,y+3)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Ore / Min")
         
         
         
         self.pdf.line(120, y, 120, y4)
         self.pdf.set_xy(120,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Tempo produz.")
         self.pdf.set_xy(120,y+3)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(6)
         self.pdf.cell(10,0, "Ore / Min")
         
         
         
        
         self.pdf.line(138, y, 138, y4)
         self.pdf.set_xy(138,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Operatore")
         
         
         self.pdf.line(164, y, 164, y4)
         self.pdf.set_xy(164,y)
         self.pdf.set_font('', 'B')
         self.pdf.set_font_size(10)
         self.pdf.cell(10,0, "Note")
        
         
         
         
         
         
         
        
         
         
         
         
         
     def intestazione(self,cliente,rif_ordine,codice_articolo,scadenza,revisione,numero_pezzi,giacenza,ubicazione,cartella,peso):    
         self.cliente = cliente
         self.rif_ordine = rif_ordine
         self.codice_articolo = codice_articolo
         self.scadenza = scadenza
         self.revisione = revisione
         self.numero_pezzi = numero_pezzi
         self.giacenza=giacenza
         self.ubicazione=ubicazione
         self.cartella=cartella
         self.peso=peso
         
         
     def genera_bardcode(self,br):
         options = {}
         options["write_text"] = False
         options["text"] = 'asd'
         generated = barcode.codex.Code39(br, writer=ImageWriter(), add_checksum=False)
         generated.render(options)
         print options
	 filename = generated.save(str(br))
	 return filename
	 
         
     def footer(self,n_riga,ente):
         self.n_riga=n_riga
         self.br = self.genera_bardcode(n_riga)
         self.ente=ente
              
        
         
         
        
     def add_note(self,ubicazione,giacenza,cartella):
         pass
         
         
     def create_pdf(self):
        
         
         
         #self.pdf.write_html(self.html)
         
         self.pdf.output('./applications/gestionale/static/rcp.pdf','F')
	     #self.pdf.output('controllo.pdf','F')
         


if __name__ == '__main__':
    p = CONTROLLO_PRODUZIONE("Microcarp S.r.l.","Registro dei Controlli in Produzione")
    p.intestazione("Brema Spa 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890","A17 002852 - POS. 1", "ABC123","07/05/2017","A", "10")
       
    p.footer("1452")
   
    
    for x in range(30):
        p.add_row("111111111122222222223asdasdas33333"+str(x),"Dimensionale e Forma "+str(x))
    
    p.insert_rows()
    p.create_pdf()
    

