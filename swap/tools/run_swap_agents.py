#!/usr/bin/env python

from swap import Control
import time

# if __name__ == "__main__":
#     from swap import Control
#     import time

#     def test_swap():
#         start = time.time()
#         control = Control(.5, .5)
#         max_batch_size = 1e5

#         # get classifications
#         classifications = control.getClassifications()

#         n_classifications = 1e6

#         # determine and set max batch size
#         classifications.batch_size(int(min(max_batch_size, n_classifications)))

#         swap = SWAP_AGENTS()

#         # loop over classification curser to process
#         # classifications one at a time
#         print("Start: SWAP Processing %d classifications" % n_classifications)
#         for i in range(0, int(n_classifications)):
#             # read next classification
#             current_classification = classifications.next()
#             # process classification in swap
#             swap.processOneClassification(current_classification)
#             if i % 100e3 == 0:
#                 print("   " + str(i) + "/" + str(n_classifications))
#         print("Finished: SWAP Processing %d/%d classifications" %
#               (i, n_classifications))

#         control.process()
#         print("--- %s seconds ---" % (time.time() - start))
#         swappy = control.getSWAP()
#         ud = swappy.getUserData()
#         sd = swappy.getSubjectData()

#     test_swap()

def main():
    start = time.time()
    server = Control(.5,.5)
    server.process()
    print("--- %s seconds ---" % (time.time() - start))
    swappy = server.getSWAP()
    ud = swappy.getUserData()
    sd = swappy.getSubjectData()

if __name__ == "__main__":
    main()