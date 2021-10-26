import json

class Reader:

  @staticmethod
  def readJson(jsonFile):
    file = open(jsonFile)
    data = json.load(file)
    file.close()

    return data
