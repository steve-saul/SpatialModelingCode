import numpy as np
import matplotlib.pyplot as plt
import math
import random
import scipy.stats as ss

def vnorm(v):
	return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def vnormalize(v):
	vmag = vnorm(v)
	return np.array([v[i]/vmag  for i in range(len(v))])

def delta(direction,position,center,radius):
	D = (direction.dot(position-center))**(2) - (position-center).dot(position-center) + radius**2
	return D

def t_norm_c(mu,sig,r1,r2,inner):
	pa = ss.norm.cdf(float(r1-mu)/sig)
	pb = ss.norm.cdf(float(r2-mu)/sig)
	if inner:
		out = mu + sig*ss.norm.ppf((pb-pa)*random.uniform(0,1)+pa)
	else:
		if random.uniform(0,1)<pa/(pa+1-pb):
			out = mu + sig*ss.norm.ppf(pa*random.uniform(0,1))
		else:
			out = mu + sig*ss.norm.ppf((1-pb)*random.uniform(0,1)+pb)
	return out

def inv_cdf(y):
    if 0<=y<0.015:
        return (((math.pi*y)/(0.015*8))-math.pi)
    elif 0.015<=y<0.035:
        return ((y-0.05)*math.pi/0.04)
    elif 0.035<=y<0.045:
        return (((math.pi*(y-0.035))/0.08)-(3.0/8.0)*math.pi)
    elif 0.045<=y<0.06:
        return (((math.pi*(y-0.045))/(0.015*8.0))-(2.0/8.0)*math.pi)
    elif 0.06<=y<0.5:
        h = 6.92/math.pi
        Q = 0.12/math.pi
        wd = (2*(0.44-Q*math.pi/16.0))/(h-Q)
        m = h/wd
        a = m/2.0
        b = h
        c = h*math.pi/8.0 - m*math.pow(math.pi, 2)/128.0 + 0.06 - y
        dt = math.pow(b, 2) - 4.0*a*c
        return ((-b+math.pow(dt,0.5))/(2*a))
    elif 0.5<=y<0.94:
        h = 6.92/math.pi
        Q = 0.12/math.pi
        wd = (2*(0.44-Q*math.pi/16.0))/(h-Q)
        m = -h/wd
        a = m/2.0
        b = h
        c = 0.5-y
        dt = math.pow(b, 2) - 4.0*a*c
        return ((-b+math.pow(dt,0.5))/(2*a))
    elif 0.94<=y<0.955:
        return (((math.pi*(y-0.94))/(0.015*8.0))+(1.0/8.0)*math.pi)
    elif 0.955<=y<0.965:
        return (((math.pi*(y-0.955))/0.08)+(2.0/8.0)*math.pi)
    elif 0.965<=y<0.985:
        return (((math.pi*(y-0.965))/0.04)+(3.0/8.0)*math.pi)
    elif 0.985<=y<=1:
        return (((math.pi*(y-0.985))/(0.015*8.0))+(7.0/8.0)*math.pi)

def binorm_hitrun_circle(Mu,Sig,pos,pre_angle,center,r,inner=1):
	# (1) Generate a 2 dim random (uniform) vector, and normalize it to get the random direction
	#d = np.array([random.gauss(0,1),random.gauss(0,1)])
	#d = vnormalize(d)
	delta_angle = inv_cdf(random.random())
	angle = math.fmod((pre_angle+delta_angle), math.pi)
	d = np.array([math.cos(angle),math.sin(angle)])

	# (2) Cholesky decomposition for std.err
	B = np.linalg.cholesky(Sig)

	# (3) Expression of Delta
	D = delta(d,pos,center,r)

	# (4) Matrix left division
	z1 = np.linalg.inv(B).dot(d)
	z2 = np.linalg.inv(B).dot(pos-Mu)

	# (5) Mean and variance of lambda
	sig = float(1)/vnorm(z1)
	mu = -z1.dot(z2)*(sig**2)

	# (6) Draw lambda according Delta
	if inner:
		# Roots
		r1 = -math.sqrt(D) - d.dot(pos-center)
		r2 = math.sqrt(D) - d.dot(pos-center)
		lam = t_norm_c(mu,sig,r1,r2,inner)
	else:
		if D<0:
			lam = mu + sig*random.gauss(0,1)
		else:
			# Roots
			r1 = -math.sqrt(D) - d.dot(pos-center)
			r2 = math.sqrt(D) - d.dot(pos-center)
			lam = t_norm_c(mu,sig,r1,r2,inner)

	# (7) Calculate the next point
	pos = pos + lam*d
	return pos,angle