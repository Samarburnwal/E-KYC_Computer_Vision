import cv2
import numpy as np
#import matplotlib.pyplot as plt

image_path = "E-KYC_Computer_Vision\\aadharImages\\aadhar1.png"

img = cv2.imread(image_path)
print(img)