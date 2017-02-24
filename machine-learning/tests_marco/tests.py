import scipy.io as sio


file_path = "D://Studium_GD//Zooniverse//Data//sn_hunters_image_classification//"
file_name = "3pi_20x20_skew2_signPreserveNorm.mat"

image_data = sio.loadmat(file_path + file_name)




dataFile = "D://Studium_GD//Zooniverse//Data//sn_hunters_image_classification//3pi_20x20_skew2_signPreserveNorm.mat"
patchesFile = "sparse_output_test.mat"

image_test = sio.loadmat(dataFile)

image_X = image_test['testX']

image_test = sio.loadmat(patchesFile)
