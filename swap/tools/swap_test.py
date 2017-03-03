from swap import Control
import time          

def test_swap():
    start = time.time()
    server = Control(.5,.5)
    server.process()
    print("--- %s seconds ---" % (time.time() - start))
    swappy = server.getSWAP()
    ud = swappy.getUserData()
    sd = swappy.getSubjectData()
    
if __name__ == "__main__":
    test_swap()


#
## read classifications
#def test_swap():
#
#    start = time.time()
#    server = Server(.5,.5)
#    n_classifications = server.classifications.count()
#    #n_classifications=1000
#    max_batch_size = 100000
#    # initialize curser with limit and max batch size
#    classification_cursor = server.classifications.find().limit(n_classifications).batch_size(min(max_batch_size,n_classifications))
#
#    swappy = SWAP()
#    # loop over cursor to retrieve classifications
#    for i in range(0,n_classifications):
#        current_classification = classification_cursor.next()
#        swappy.processOneClassification(current_classification)
#        if i % 100e3 ==0:
#            print(str(i) + "/" + str(n_classifications))
#    ud = swappy.getUserData()
#    sd = swappy.getSubjectData()
#    print("--- %s seconds ---" % (time.time() - start))
#    