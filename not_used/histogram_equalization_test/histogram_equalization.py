import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('img.jpg', 0)

img = cv2.equalizeHist(img)

hist,bins = np.histogram(img.flatten(),256,[0,256])

cdf = hist.cumsum()
cdf_normalized = cdf * hist.max()/ cdf.max()


plt.plot(cdf_normalized, color = 'b')
plt.hist(img.flatten(),256,[0,256], color = 'r')
plt.xlim([0,256])
# plt.legend(('cdf','histogram'), loc = 'upper left')
cv2.imshow('Histogram equalization', img)
cv2.waitKey(1)
plt.show()