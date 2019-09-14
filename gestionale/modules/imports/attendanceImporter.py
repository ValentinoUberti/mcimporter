import openpyxl
from datetime import datetime
from calendar import monthrange
class Actions():
    def __init__(self,name,action,actionTime):
        self.name=name
        self.action=action
        self.actionTime=datetime.strptime(actionTime,"%d/%m/%Y %H:%M:%S")

    def __repr__(self):
        return self.name + " " + self.action +" " + str(self.actionTime)
 

class FinalOrderedActions():
    
    def __init__(self):
        self.days=dict()
        for i in range(1,32):
            self.days[i]=dict()

class OrderedActions():

    def __init__(self):
        self.days=dict()
        for i in range(1,32):
            self.days[i]=dict()

    def printDays(self):
        for d in self.days:
            print d

class AttendanceImporter():
    



    def __init__(self,filename):
        self.wb=openpyxl.load_workbook(filename)
        self.ws = self.wb.worksheets[0]
        self.actions=[]
        self.finalOrderedActions=FinalOrderedActions()

    

    def addFinalOrderedActions(self,worker,day,hours):
        self.finalOrderedActions.days[day][worker]=hours

    def trasformHumanTimeToFull(self,t):
        t=str(t)
        s=0
        if len(t)>2:
           #print(type(t),len(t))
           #return 0
           t1=t.split(":")
           h=int(t1[0])
           m=int(t1[1])
           m=int((m*100/60))
           s="{0}.{1}".format(h,m)

        print (float(s))   
        return float(s)   



    def loadData(self):
        row_count=1
        fullName=""
        takeTheTime=False
        for row in self.ws.iter_rows():
            if row_count==1:
                #Take the month number from the first row
                fullDateString=row[0].value.upper().strip()
                dateString=fullDateString[8:19].strip()
               
                year=datetime.strptime(dateString,"%d-%m-%Y").year
                monthNumber=datetime.strptime(dateString,"%d-%m-%Y").month
                num_days = monthrange(year, monthNumber)[1]
                self.year=year
                self.monthNumber=monthNumber
                self.num_days=num_days
               
                
                pass

            if (row_count >= 5) and (row_count % 2 ==1):
                 fullName= row[0].value.upper().strip()
                 fullName=fullName[:fullName.index("(")].strip()
                 takeTheTime=True

                 

                 
            elif (row_count >= 5) and (row_count % 2 ==0):
                 for d in range(1,self.num_days+1):
                     worked_hours=row[d+2].value
                     if worked_hours is not None:
                        worked_hours= self.trasformHumanTimeToFull(worked_hours)
                     else:
                        worked_hours=0
                     self.addFinalOrderedActions(fullName,d,worked_hours)


                 pass
            
            row_count+=1
            if row_count>32:
                break

            
          
        self.finalOrderedActions.days[32]=int(self.monthNumber)
        return self.actions

    
    
            

                
            
        


