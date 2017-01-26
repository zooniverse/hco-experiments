import optparse, time
import numpy as np
import scipy.io as sio

np.seterr(all="ignore")

def signPreserveNorm(patch):

        Vec = np.nan_to_num(patch)
        std = np.std(Vec)
        normVec = ((Vec)/ np.abs(Vec))*(np.log1p(np.abs(Vec)/std))
        return np.nan_to_num(normVec)

def build_patches(X, patchSize, numPatches):
    m, n = np.shape(X)
    extent = int(np.floor(np.sqrt(n)) / 2.0)
    print extent
    patches = np.ones((m*numPatches, patchSize*patchSize))
    print "[+] building %d patches." % (m*numPatches)
    for i in range(m):
        vector = X[i,:]
        image = np.reshape(vector, (2*extent, 2*extent), order="F")
        for j in range(numPatches):
            top_left = (np.random.randint((2*extent)-patchSize), \
                        np.random.randint((2*extent)-patchSize))
            #print top_left
            #top_left = (0,0)
            #patch = signPreserveNorm(image[top_left[0]:top_left[0]+patchSize, top_left[1]:top_left[1]+patchSize])
            patch = image[top_left[0]:top_left[0]+patchSize, top_left[1]:top_left[1]+patchSize]
            patches[(i*numPatches)+j,:] = patches[(i*numPatches)+j,:] * np.ravel(patch, order="F")
    return patches


def main():
    startTime = time.time()
    parser = optparse.OptionParser("[!] usage: python build_patches.py\n"+\
                                   " -i <.mat file with image vectors>\n"+\
                                   " -o <output file [optional]>\n"+\
                                   " -p <patch size [default=8]>\n"+\
                                   " -n <number of patches per image [default=1]>")

    parser.add_option("-i", dest="inFile", type="string", \
                      help="specify file containing image vectors from which to extract patches")
    parser.add_option("-o", dest="outFile", type="string", \
                      help="specify output file name [optional]")
    parser.add_option("-p", dest="patchSize", type="int", \
                      help="specify size of patches to extract [default=8]")
    parser.add_option("-n", dest="numPatches", type="int", \
                      help="specify number of patches to extract from each image [default=1]")
                      
    (options, args) = parser.parse_args()
    
    inFile = options.inFile
    outFile = options.outFile
    patchSize = options.patchSize
    numPatches = options.numPatches
    
    if inFile == None:
        print parser.usage
        exit(0)
        
    if patchSize == None:
        patchSize = 8
        
    if numPatches == None:
        numPatches = 1
        
    if outFile == None:
        outFile = "patches_"+inFile.split("/")[-1].split(".")[0] +\
                  "_"+str(patchSize)+"x"+str(patchSize)+"_"+\
                  str(numPatches)+".mat"
                  
    data = sio.loadmat(inFile)


    #X = data["X"]
    X = data["patches"]
    #try:
    #    X = np.concatenate((X, data["validX"]))
    #except KeyError:
    #    X = np.concatenate((X, data["testX"]))
    
    patches = build_patches(X, patchSize, numPatches)   
                  
    print "[+] Saving patches."
    sio.savemat(outFile, {"patches":patches})
    print "[+] Processing complete."
    print "[*] Run time: %d minutes." % ((time.time() - startTime) / 60)

if __name__ == "__main__":
    main()
