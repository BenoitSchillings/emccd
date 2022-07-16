import numpy as np

from scipy.optimize import leastsq

def fit_gauss_circular(data):
	"""
	---------------------
	Purpose
	Fitting a star with a 2D circular gaussian PSF.
	---------------------
	Inputs

	* data (2D Numpy array) = small subimage
	---------------------
	Output (list) = list with 6 elements, in the form [maxi, floor, height, mean_x, mean_y, fwhm]. The list elements are respectively:
	- maxi is the value of the star maximum signal,
	- floor is the level of the sky background (fit result),
	- height is the PSF amplitude (fit result),
	- mean_x and mean_y are the star centroid x and y positions, on the full image (fit results), 
	- fwhm is the gaussian PSF full width half maximum (fit result) in pixels
	---------------------
	"""
	
	#find starting values
	maxi = data.max()
	floor = np.ma.median(data.flatten())
	height = maxi - floor
	if height==0.0:				#if star is saturated it could be that median value is 32767 or 65535 --> height=0
		floor = np.mean(data.flatten())
		height = maxi - floor

	mean_x = (np.shape(data)[0]-1)/2
	mean_y = (np.shape(data)[1]-1)/2

	fwhm = np.sqrt(np.sum((data>floor+height/2.).flatten()))
	
	#---------------------------------------------------------------------------------
	sig = fwhm / (2.*np.sqrt(2.*np.log(2.)))
	width = 0.5/np.square(sig)
	
	p0 = floor, height, mean_x, mean_y, width

	#---------------------------------------------------------------------------------
	#fitting gaussian
	def gauss(floor, height, mean_x, mean_y, width):		
		return lambda x,y: floor + height*np.exp(-np.abs(width)*((x-mean_x)**2+(y-mean_y)**2))

	def err(p,data):
		return np.ravel(gauss(*p)(*np.indices(data.shape))-data)
	
	p = leastsq(err, p0, args=(data), maxfev=300)
	p = p[0]
	
	#---------------------------------------------------------------------------------
	#formatting results
	floor = p[0]
	height = p[1]
	mean_x = p[2]
	mean_y = p[3]

	sig = np.sqrt(0.5/np.abs(p[4]))
	fwhm = sig * (2.*np.sqrt(2.*np.log(2.)))	
	
	output = [maxi, floor, height, mean_x, mean_y, fwhm]
	return fwhm

