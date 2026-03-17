import os

class Solution: 
    def __init__(self, status, obj_value, dualBound, runtime, sol):
        self._obj_value = obj_value
        self._runtime = runtime
        self._status = status
        self._dualBound = dualBound
        self._solP1 = sol[0]
        self._solP2 = sol[1]
        self._soly = sol[2]
        self._solr = sol[3]
        self._sols = sol[4]

    def value(self):
        return self._obj_value
    


def saveDataToFile(solution, dataFileName):
    import csv
    print("Saving to file ", dataFileName)

    outfile = open(dataFileName, 'w')
    writer = csv.writer(outfile, delimiter=";")
    writer.writerow([solution._status])
    writer.writerow([solution._obj_values])
    writer.writerow([solution._dualBound])
    writer.writerow([solution._runtime])
    writer.writerow(solution._solP1)
    writer.writerow(solution._solP2)
    writer.writerow(solution._soly)
    writer.writerow(solution._solr)
    writer.writerow(solution._sols)
    outfile.close()