# preprocess.py
import cv2
import numpy as np

def preprocess_image(path):
    img = cv2.imread(path)

    if img is None:
        raise Exception("Image cannot be read.")

    # Resize sesuai model kamu
    img = cv2.resize(img, (48, 48))

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img / 255.0
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)

    return img
