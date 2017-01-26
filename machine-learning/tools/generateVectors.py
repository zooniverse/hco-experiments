import sys, os
import numpy as np
import scipy.io as sio
from TargetImage import *

#np.seterr(all="raise")
def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) != 4:
        sys.exit("Usage: python generateVectors.py " +\
                 "<absolute path to image list> " +\
                 "<extent> " +\
                 "<output file>")

    imageFile = argv[1]
    path, file = os.path.split(imageFile)
    print path 
    extent = int(argv[2])
    outputFile = argv[3]


    counter = 0
    imageList = []
    for line in open(imageFile,"r").readlines():
        imageList.append(line.rstrip())
        counter += 1

    X = np.ones((counter, 4*extent*extent))
    y = np.ones((counter,))
    for i,image in enumerate(imageList):
        vector = np.nan_to_num(TargetImage(path+"/"+image, extent).signPreserveNorm())
        X[i,:] = X[i,:] * vector

    """
    counter = 0
    objects = []
    for line in open(imageFile,"r").readlines():
        objects.append(line.rstrip().split("_")[0])
        counter += 1
    objects = set(objects)

    first_detections = []
    for object in objects:
        first_detection = 99999.0
        for line in open(imageFile,"r").readlines():
            if object in line:
                #print object
                if float(line.rstrip().split("_")[1]) <= first_detection:
                    first_detection = float(line.rstrip().split("_")[1])
                    #print first_detection
        if first_detection != None:
            first_detections.append(object+"_"+str(first_detection))
        else:
            print "No First detection found"
    print first_detections

    #X = np.ones((counter, 4*extent*extent))
    
    X = np.ones((len(first_detections)+5, 4*extent*extent))


    imageList = []
    first_detection_counter = 0
    for i,line in enumerate(open(imageFile,"r").readlines()):
        for detection in first_detections:
            if detection in line:
                imageList.append(line)
                print path+"/"+line.rstrip()
                vector = TargetImage(path+"/"+line.rstrip(), extent).signPreserveNorm()
                print first_detection_counter
                X[first_detection_counter,:] = X[first_detection_counter,:] * vector
                first_detection_counter += 1
    """
    """
        if "1160335221545252700" in line:
            print "skipping: " + line
            continue

        for detection in first_detections:
            if detection in line:
                print "skipping: " + line + "-first detection"
                first_detection_counter +=1
                continue
        print line
        imageList.append(line)
        try:
            vector = TargetImage(path+"/"+line.rstrip(), extent).signPreserveNorm()
            X[i,:] = X[i,:] * vector
        except:
            continue
    """

    print X
    #print first_detection_counter
    print np.shape(X)
    print np.shape(imageList)
    sio.savemat(outputFile, {"X": X, "y":y, "images": imageList})

if __name__ == "__main__":
    main()
