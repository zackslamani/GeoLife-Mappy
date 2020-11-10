import os
import datetime as dt
from math import cos, asin, sqrt,sin

def PreprocessingAllPersonData(folderName):
    """entry-> folder name of the Data
       output->file with all the data necessary to train and test the model"""

    resultLabeled = []
    resultNOTLabeled = []

    #get the list of folders in Data
    personData = os.listdir(folderName)

    #iterate over each folder and look for the persons with data labeled
    for fileName in personData:
        fullFileName = "c:/ETNA/Geolife Trajectories 1.3/mappy/Data/" + fileName
        if os.listdir(fullFileName).__contains__("labels.txt"):
            print("Analysing " + fileName + " as Labeled DATA")
            l = PreprocessingOnePersonData(fullFileName)
            if l != []:
                resultLabeled.append(l)
        else:
            print("Analysing " + fileName + " as NOT Labeled DATA")
            wideSpectrum = [[dt.datetime(1990, 1, 1,00,00,00),dt.datetime(2990, 1, 1,00,00,00), "?"]]
            notL = LoadData(fullFileName, wideSpectrum)
            if notL != []:
                resultNOTLabeled.append(notL)


    writeData(resultLabeled, "c:/ETNA/Geolife Trajectories 1.3/mappy/resultLabeled.csv")
    writeData(resultNOTLabeled, "c:/ETNA/Geolife Trajectories 1.3/mappy/resultNOTLabeled.csv")


def PreprocessingOnePersonData(fullPath):
    listOfLabeledData = LoadLabeledData(fullPath)
    listOfNotLabeledData = LoadData(fullPath, listOfLabeledData)
    return listOfNotLabeledData


def LoadLabeledData(fullPath):
    """Take the fileName called "Label.txt" who has the data already labeled and return a list of all this info"""
    """list returned: [[initialTime as datetime, endtime as datetime, mode of transportation],...]"""

    fullPath = fullPath + "/labels.txt"

    f = open(fullPath, "r")
    if f.mode == "r":
        allLines = f.readlines()
        allLines = allLines[1:]
        data = [line.split('\t') for line in allLines]
    f.close()

    for d in data:
        #convertin in datatime the initial time
        year = int(d[0][0:4])
        mount = int(d[0][5:7])        
        day = int(d[0][8:10])        
        hour = int(d[0][11:13])
        minute = int(d[0][14:16])
        seconds = int(d[0][17:19])
        d[0] = dt.datetime(year,mount,day,hour,minute,seconds)        

        #convertin in datatime the end time
        year = int(d[1][0:4])
        mount = int(d[1][5:7])
        day = int(d[1][8:10])
        hour = int(d[1][11:13])
        minute = int(d[1][14:16])
        seconds = int(d[1][17:19])
        d[1] = dt.datetime(year,mount,day,hour,minute,seconds)

        #removing the return of line character
        d[2] = d[2][:len(d[2]) - 1] 
        
    return data

def LoadData(fullPath, listOfLabeledData):
    """Take the folder passed in "fullPath" who has the data not labeled of the trajectories and return a list of all this info"""
    """list returned: [[initialTime as datetime, endtime as datetime, mode of transportation],...]"""
    result = []
    
    #get the list of files in Trajectory folder
    fullPath = fullPath + "/Trajectory"
    listOfTrajectories = os.listdir(fullPath)

    #for each file .plt transform the raw data in the data that is going to go to the learning
    for trajectory in listOfTrajectories:
        plt = fullPath + "/" + trajectory
        listAux = GetDataFromPLTFile(plt, listOfLabeledData)
        for l in listAux:
            if l != []:
                result.append(l)

    return result
    


def GetDataFromPLTFile(plt, listOfLabeledData):
    listOfStepTrajectRaw = readTrajectory(plt)
    listOfStepTraject = createListOfStepTraject(listOfStepTrajectRaw, listOfLabeledData)

    return listOfStepTraject


def readTrajectory(fileName) -> []:
    f = open(fileName, "r")
    if f.mode == "r":
        allLines = f.readlines()
        contents = allLines[6:]
        placeAndTimes = [line.split(",") for line in contents]
    f.close()
    return placeAndTimes


def createListOfStepTraject(listOfStepTraject, listOfLabeledData):
    result = []
    for i in range(len(listOfStepTraject) - 1):
        l = stepTraject(listOfStepTraject[i], listOfStepTraject[i + 1], listOfLabeledData)
        if l != []:
            result.append(l)
    return result


def stepTraject(initialPlaceAndTime, endPlaceAndTime, listOfLabeledData):
    year = int(initialPlaceAndTime[5][0:4])
    mount = int(initialPlaceAndTime[5][5:7])
    day = int(initialPlaceAndTime[5][8:10])
    hour = int(initialPlaceAndTime[6][0:2])
    minute = int(initialPlaceAndTime[6][3:5])
    seconds = int(initialPlaceAndTime[6][6:8])
    initialTime = dt.datetime(year,mount,day,hour,minute,seconds)
    
    year = int(endPlaceAndTime[5][0:4])
    mount = int(endPlaceAndTime[5][5:7])
    day = int(endPlaceAndTime[5][8:10])
    hour = int(endPlaceAndTime[6][0:2])
    minute = int(endPlaceAndTime[6][3:5])
    seconds = int(endPlaceAndTime[6][6:8])
    endTime = dt.datetime(year,mount,day,hour,minute,seconds)

    deltaDistance = distanceLatLon(initialPlaceAndTime[0], initialPlaceAndTime[1], endPlaceAndTime[0], endPlaceAndTime[1])
    deltaTime = (endTime - initialTime).total_seconds()
    deltaAltitude = float(endPlaceAndTime[3]) - float(initialPlaceAndTime[3])
    speed = 0
    if deltaTime != 0:
        speed = deltaDistance / deltaTime

    mode = IsInAnyInterval(initialTime, endTime, listOfLabeledData)
    if mode == "":
        return []
    else:
        # return [initial time as datetime, end time as datetime, deltaTime in seconds, deltaDistance in meters, deltaAltitude in feets, speed in meters/seconds]
        return [initialTime, endTime, deltaTime, deltaDistance, deltaAltitude, speed, mode]


def distanceLatLon(lat1, lon1, lat2, lon2) -> float:
    """take 2 points defined by longitud and latitude and calculate the distance between they"""
    """return the distance in meters"""
    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a)) * 1000


def IsInAnyInterval(initialTime, endTime, listOfLabeledData):
    for elem in listOfLabeledData:
        if initialTime >= elem[0] and endTime <= elem[1]:
            return elem[2]
    return ""



def writeData(data, fileName):
    f = open(fileName, "w")
    head = "\"Initial Time\", \"End Time\", \"Delta Time\", \"Delta Distance\", \"Delta Altitude\", \"Speed\", \"Transportation Mode\""
    f.write(head)
    for i in data:
        for j in i:
            initialTime = str(j[0])
            endTime = str(j[1])
            deltaTime = str(j[2])
            deltaDistance = str(j[3])
            deltaAltitude = str(j[4])
            speed = str(j[5])

            f.write(str("\n" + initialTime + "," + endTime + "," + deltaTime + "," + deltaDistance + "," + deltaAltitude + "," + speed + "," + j[6]))
    
    f.close()





def main():
    PreprocessingAllPersonData("c:/ETNA/Geolife Trajectories 1.3/mappy/Data/")


if __name__ == "__main__":
    main()