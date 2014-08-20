# Cross spectral match
# 14/08/2014 
# llpassarelli@gmail.com

import numpy as np
import wave 
import matplotlib.pyplot as plt
from matplotlib.mlab import find
from pylab import specgram, savefig
import sys

file0 = 'mono0.wav'
file1 = 'mono1.wav'
# threshold mask
th_min=20
th_max=100
# th_result aprova | reprova
th_result=50
nfft = 128
fig, (ax1,ax2,ax3,ax4,ax5) = plt.subplots(5)

if len(sys.argv) == 3:
	file0=sys.argv[1]
	file1=sys.argv[2]

print('wav_files:', file0, file1)	
spf0 = wave.open(file0,'r')
spf1 = wave.open(file1,'r')

#If Stereo
if (spf0.getnchannels() == 2 or spf1.getnchannels() == 2):
    print 'Just mono files'
    sys.exit(0)
	
# Extract Raw Audio from Wav File 0
S0 = spf0.readframes(-1)
S0 = np.fromstring(S0, 'Int16')
fs0 = spf0.getframerate()
S1 = spf1.readframes(-1)
S1 = np.fromstring(S1, 'Int16')
fs1 = spf1.getframerate()

# Extract sample Times
t1=8000 * 2.8
t2=8000 * 32.8
s0=S0[t1:t2]
s1=S1[t1:t2]

# Find peaks
peak = 150
a = find((s0[1:] >= peak) & (s0[:-1] < peak))
b = find((s1[1:] >= peak) & (s1[:-1] < peak))

# Diff of first peaks
diff = a[0] - b[0]

# Remove delay  
s0 = S0[t1+diff:t2+diff]
print('Async [0:10]')
print('A:',a[0:10])
print('B:',b[0:10])
print('diff: A-B:',diff)

# Find peaks
a = find((s0[1:] >= peak) & (s0[:-1] < peak))
b = find((s1[1:] >= peak) & (s1[:-1] < peak))

# Show first sync
print('Sync [0:10]')
print('A:', a[0:10])
print('B:', b[0:10])   

# Test len( A | B ) and scale 
if(len(s0) > len(s1)):
	diff = np.zeros(len(s0) - len(s1))
	s1 = np.append(s1,diff)
	print('len(A), len(B), diff(A-B)', len(s0), len(s1))			
if(len(s0) < len(s1)):
	diff = np.zeros(len(s1) - len(s0))
	s0 = np.append(s0,diff)
	print('len(A), len(B), diff(A-B)', len(s0), len(s1))	

#Spectro A	
Px0, freqs0, bins0, im0 = ax1.specgram(s0, NFFT=nfft,Fs=fs0, noverlap=0)
ax1.set_title('File A: '+file0, loc='left')
#Spectro B
Px1, freqs1, bins1, im1 = ax2.specgram(s1, NFFT=nfft,Fs=fs1, noverlap=0)
ax2.set_title('File B: '+file1, loc='left')
ax2.axes.get_xaxis().set_visible(False)
ax2.axes.get_yaxis().set_visible(False)
# Scale
arr2D1 = 10 * np.log10(Px0)
arr2D1[arr2D1 == -np.inf] = 0 # replace infs with zeros
arr2D2 = 10 * np.log10(Px1)
arr2D2[arr2D2 == -np.inf] = 0 # replace infs with zeros
# mask
th1=((th_min < arr2D1) & (arr2D1<th_max))# mask A
th2=((th_min-2 < arr2D2) & (arr2D2<th_max))# mask B
# mask error
error = (th1 & th2) 
# error %
a=np.count_nonzero(th1)
b=np.count_nonzero(error)
c=a-b
d=(((c*100))/a)

# mask A
ax3.imshow(th1, interpolation='nearest', aspect='auto', cmap='Blues')
ax3.invert_yaxis()
ax3.axes.get_xaxis().set_visible(False)
ax3.axes.get_yaxis().set_visible(False)
ax3.set_title('Mask A: ', loc='left')

# mask B
ax4.imshow(th2, interpolation='nearest', aspect='auto', cmap='Reds')
ax4.invert_yaxis()
ax4.axes.get_xaxis().set_visible(False)
ax4.axes.get_yaxis().set_visible(False)
ax4.set_title('Mask B: ', loc='left')

# mask error
ax5.imshow(error, interpolation='nearest', aspect='auto', cmap='Greys')
ax5.invert_yaxis()
ax5.axes.get_xaxis().set_visible(False)
ax5.axes.get_yaxis().set_visible(False)
d = "%0.2f" % (100-d)

if(float(d)>th_result):
	result='OK'
else:
	result='ERRO'
	
title = 'Cross A x B = '+str(d)+'% | '+result
fig.suptitle(title, fontsize=14, fontweight='bold')	
ax5.set_title(title, loc='left')
fig = plt.gcf()
fig.canvas.set_window_title(title)
plt.show()
 
