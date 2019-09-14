import yaml


class Worker():
    
    def __init__(self, name, startingRow):
        self.name = name
        self.startingRow = startingRow

  


class YamlImporter():

    def __init__(self, filename):
        self.filename = filename
        self.workers=[]

    def importYaml(self):
        with open(self.filename) as f:
            self.yamlData = yaml.load(f, Loader=yaml.BaseLoader)["workers"]

        for d in self.yamlData:
            w = Worker(d["paName"],d["startingRow"])
            self.workers.append(w)

        return self.workers

    def returnStartingRow(self,worker):
        for row in self.workers:
            if row.name==worker:
                return row.startingRow
        return None
