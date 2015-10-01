# OS
from subprocess import call
import os
import sys

# Djano
from django.core.files import File as FileDj
from django.http import HttpResponse
from django import forms
from django.core.files.temp import NamedTemporaryFile

# Signal processing
import numpy as np
import wave
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib import cm

# Create your models here.
class UploadFileForm(forms.Form):
    musicFile = forms.FileField()

class sound3dGenerator():
    def __init__(self):
        self.status = 0

        # Hard-coded configurations
        self.num_audio_sections = 10
        self.num_downsample = 10

    # This function returns the HTTP response with the STL file
    def generate(self, musicFile):
        tmpScad = NamedTemporaryFile(suffix='.scad')
        tmpDat = NamedTemporaryFile(suffix='.dat')

        #points = self.generatePoints(musicFile)
        #print points
        #if points.shape[0] == 0:
        #    return np.array([])

        # Print to dat file
        tmpDat.write('10 2 3 4 5\n')
        tmpDat.write('2 3 5 6 7\n')

        # Generate Scad file
        tmpScad.write('surface(file = "' + tmpDat.name + '", center = true, convexity = 5);')
        
        # Generate STL file
        tmpScad.seek(0)        
        #for line in tmpScad:
        #    print line
        tmpStl = NamedTemporaryFile(suffix='.stl')
        cmd = 'openscad -o ' +  tmpStl.name + ' ' + tmpScad.name
        ret = call(cmd, shell=True)
        tmpScad.close()

        # Copy STL file to HttpResponse
        response = HttpResponse(content_type='application/txt')
        response['Content-Disposition'] = 'attachment; filename="%s.stl"' % inputString
        f = FileDj(response)

        # Copy file over to the download file
        tmpStl.seek(0)
        for line in tmpStl:
            f.write(line)
        tmpStl.close()
        return response

    # Opens the wave file and produces the points for spectrum
    def generatePoints(self, musicFile):
        waveFile = wave.open(musicFile.name, 'r')

        inputSignal = waveFile.readframes(-1)
        inputSignal = np.fromstring(inputSignal, 'Int16')
        fs = waveFile.getframerate()

        # If Stereo
        if waveFile.getnchannels() == 2:
            return np.array([])

        # Pad zeros to fit in everything
        num_pad_zeros = self.num_audio_sections - inputSignal.shape[0] % self.num_audio_sections
        inputSignal = np.pad(inputSignal, (0,num_pad_zeros), 'constant', constant_values=(0,0))

        # Reshape
        reshapedSignal = inputSignal.reshape(self.num_audio_sections, -1)
        spectrumPoints = np.zeros([self.num_audio_sections, self.num_downsample])

        # For loop to get all spectrum points
        num_pad_zeros = self.num_downsample- reshapedSignal.shape[1] % self.num_downsample
        for idx in range(self.num_audio_sections):
            # Downsample
            tmpSignal = np.pad(reshapedSignal[idx], (0, num_pad_zeros), 'constant', constant_values=(0,0))
            tmpSignal = tmpSignal.reshape(self.num_downsample, -1)
            tmpSignal = tmpSignal.mean(axis=1)

            # FFT
            #timeInfo =np.linspace(0, len(tmpSignal)/fs, num=len(tmpSignal))
            #freqInfo = np.fft.fftfreq(timeInfo.shape[-1])
            spectrumPoints[idx] = np.fft.fft(tmpSignal)
            spectrumPoints[idx] = np.absolute(spectrumPoints[idx])

        waveFile.close()
        print spectrumPoints
        return spectrumPoints

if __name__ == "__main__":
    mGenerator = sound3dGenerator()
    f = FileDj(open('static/test.wav'))
    z = mGenerator.generatePoints(f)
    f.close()

    x = np.arange(z.shape[0])
    y = np.arange(z.shape[1])
    x, y = np.meshgrid(x, y)
    """
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)

    plt.show()
    """
    
    
