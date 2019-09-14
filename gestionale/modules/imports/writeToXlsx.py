import openpyxl
import os

class WriteToXlsx():
    
    def __init__(self,master_path,save_path):
        self.master_path=master_path
        self.save_path=save_path
        self.wb=openpyxl.load_workbook(self.master_path)
        self.ws = self.wb.worksheets[0]
    

    def write(self,row,column,value):
        self.ws.cell(row, column).value = value
        #self.ws.range('E10').value="ciao"

    def save(self):
        try:
           os.remove(self.save_path)
        except:
           pass
        self.wb.save(self.save_path)