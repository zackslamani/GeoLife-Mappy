import os
from math import cos, asin, sqrt,sin
import datetime as dt


def readTrajectory(file) -> []:
    f = open(file, "r")
    if f.mode == "r":
        allLines = f.readlines()
        contents = allLines[6:]
        placeAndTimes = [line.split(",") for line in contents]
    f.close()
    return placeAndTimes

def distanceLatLon(lat1, lon1, lat2, lon2) -> float:    
    # a = R/cos(sin(lat1) * sin(lat2) + cos(lon1) * cos(lat1) * cos(lon1-lon2))
    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)
    p = 0.017453292519943295     #Pi/180
    a = 0.5-cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p))/2
    return 12742 * asin(sqrt(a)) * 1000

def TimeDifference(date1, date2, time1, time2):
    year1 = int(date1[0:4])
    mount1 = int(date1[5:7])
    day1 = int(date1[8:10])
    hour2 = int(time2[0:2])
    minute2 = int(time2[3:5])
    seconds2 = int(time2[6:8])

    year2 = int(date2[0:4])
    mount2 = int(date2[5:7])
    day2 = int(date2[8:10])
    hour1 = int(time1[0:2])
    minute1 = int(time1[3:5])
    seconds1 = int(time1[6:8])

    a = dt.datetime(year1,mount1,day1,hour1,minute1,seconds1)
    b = dt.datetime(year2,mount2,day2,hour2,minute2,seconds2)
    
    return (b-a).total_seconds()

def altitudeDifference(alt1, alt2):
    alt1 = float(alt1)
    alt2 = float(alt2)
    return alt2 - alt1

def stepTraject(initialPlaceAndTime, endPlaceAndTime):
    initialDateAndTime = initialPlaceAndTime[5] + " " + initialPlaceAndTime[6][:len(initialPlaceAndTime[6]) - 1]
    endDateAndTime = endPlaceAndTime[5] + " " + endPlaceAndTime[6][:len(endPlaceAndTime[6]) - 1]
    deltaDistance = distanceLatLon(initialPlaceAndTime[0], initialPlaceAndTime[1], endPlaceAndTime[0], endPlaceAndTime[1])
    deltaTime = TimeDifference(initialPlaceAndTime[5], endPlaceAndTime[5],initialPlaceAndTime[6], endPlaceAndTime[6])
    deltaAltitude = float(altitudeDifference(initialPlaceAndTime[3], endPlaceAndTime[3]))
    speed = deltaDistance / deltaTime

    # return [initial time, end time, deltaTime, deltaDistance, deltaAltitude, speed]
    return [initialDateAndTime, endDateAndTime, deltaTime, deltaDistance, deltaAltitude, speed]

def createListOfStepTraject(placeAndTimes):
    result = []
    for i in range(len(placeAndTimes) - 1):
        result.append(stepTraject(placeAndTimes[i], placeAndTimes[i + 1]))
    return result

    
def main():
    #cwd = os.getcwd()
    #print(cwd)
    datas = readTrajectory("c:/ETNA/Geolife Trajectories 1.3/mappy/Data/000/Trajectory/20081023025304.plt")
    print(createListOfStepTraject(datas))
   
if __name__ == "__main__":
    main()
