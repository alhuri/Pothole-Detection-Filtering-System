import matplotlib.pyplot as plt
from keras.models import load_model
import numpy as np
import os, cv2, base64
print("libraries loaded")

model = load_model(os.path.join(os.path.dirname(__file__), "model.h5"))
print("model loaded")

def predict(pth):

    # npimg = np.fromfile(filestr, np.uint8)
    # img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    X = cv2.imread(pth,cv2.IMREAD_COLOR)
    print(X.shape)

    X = cv2.resize(X,(256,256))  
    print(X.shape)

    #plt.figure() # this can not be run in serverr env.
    #plt.imshow(X[:,:,::-1])
    #plt.show()

    X = np.array(X)
    X = np.expand_dims(X, axis=0)

    print("predicting image")
    y_pred = np.round(model.predict(X))
    if y_pred[0][0] == 1:
        return "Plain Road"
    else:
        return "Pothole Road"

