from swap import SWAP
            
# read classifications
def test_swap():
    n_classifications=1000
    max_batch_size = 1000
    server = Server(.5,.5)
    # initialize curser with limit and max batch size
    classification_cursor = server.classifications.find().limit(n_classifications).batch_size(min(max_batch_size,n_classifications))
    swappy = SWAP()
    # loop over cursor to retrieve classifications
    for i in range(0,n_classifications):
        current_classification = classification_cursor.next()
        swappy.processOneClassification(current_classification)
    ud = swappy.getUserData()
    sd = swappy.getSubjectData()
    
    
    
if __name__ == "__main__":
    test_swap()
