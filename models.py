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

# Create your models here.
class UploadFileForm(forms.Form):
    musicFile = forms.FileField()

class sound3dGenerator():
    def __init__(self):
        """
        Constructor
        """
        self.status = 0

        # Hard-coded configurations
        self.num_audio_sections = 10
        self.num_downsample = 20

        # Input members

        # Output members
        self.points = None


    def gen_online(self, inputMusicFile):
        """
        This function returns the HTTP response with the STL file
        """
        # Start generation
        self.gen_offline(inputMusicFile)
        if self.points.shape[0] == 0:
            return None

        # Print to dat file
        tmpScad = NamedTemporaryFile(suffix='.scad')
        tmpDat = NamedTemporaryFile(suffix='.dat')
        tmpScad.seek(0)
        tmpDat.seek(0)
        self.write_points_to_file(tmpDat)

        # Generate STL file
        currentDir = os.getcwd()
        os.chdir(os.path.dirname(tmpDat.name))
        tmpScad.write('surface(file = "' + os.path.basename(tmpDat.name) + '", center = true, convexity = 5);')  

        tmpDat.seek(0)
        tmpScad.seek(0)
        tmpStl = NamedTemporaryFile(suffix='.stl')
        cmd = 'openscad -o ' + os.path.basename(tmpStl.name) + ' ' + os.path.basename(tmpScad.name)
        ret = call(cmd, shell=True)
        os.chdir(currentDir)

        # Copy STL file to HttpResponse
        response = HttpResponse(content_type='application/txt')
        response['Content-Disposition'] = 'attachment; filename="%s.stl"' \
            % os.path.splitext(os.path.basename(inputMusicFile.name))[0]

        # Copy file over to the download file
        tmpStl.seek(0)
        f = FileDj(response)
        for line in tmpStl:
            f.write(line)

        # Close all temp files
        tmpDat.close()
        tmpScad.close()
        tmpStl.close()
        
        return response

    def _convert_to_wav(self, inputMusicFile, outputWaveFile):
        """
        Converts an input music file into a wave file with only one channel output only
        """
        cmd = 'ffmpeg -i ' + inputMusicFile.name + ' -y -acodec pcm_s16le -ac 1 ' + outputWaveFile.name
        
        outputWaveFile.seek(0)
        inputMusicFile.seek(0)
        ret = call(cmd, shell=True)
        return ret

    def write_points_to_file(self, fileObj):
        """
        Writes points to file
        """
        for rowIdx in range(self.points.shape[0]):
            rowPointStr = ' '.join(map(str, self.points[rowIdx]))
            fileObj.write(rowPointStr + '\n')

    def gen_offline(self, inputMusicFile):
        """
        Opens the wave file and produces the points for the desired art shape
        Currently, it only generates the spectrum
        """
        file_extension = os.path.splitext(inputMusicFile.name)[1]
        tmpInputMusicFile = NamedTemporaryFile(suffix=file_extension)
        tmpWaveFile = NamedTemporaryFile(suffix='.wav')
        for chunk in inputMusicFile.chunks():
            tmpInputMusicFile.write(chunk)

        ret = self._convert_to_wav(tmpInputMusicFile, tmpWaveFile)
        if ret:
            return np.array([])

        # Start using the wave file
        tmpWaveFile.seek(0)
        waveFile = wave.open(tmpWaveFile.name, 'r')

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
            spectrumPoints[idx] = np.absolute(np.fft.fft(tmpSignal))
            spectrumPoints[idx] = np.round(spectrumPoints[idx] / 1000.0, 2)

        waveFile.close()
        self.points = spectrumPoints

# If run as main, plot will be made for quick verification adn visualization
if __name__ == "__main__":
    mGenerator = sound3dGenerator()
    f = FileDj(open('scad/Track1.wav'))
    mGenerator.gen_offline(f)
    f.close()

    f = open('scad/test.dat', 'w')
    mGenerator.write_points_to_file(f)
    f.close()

    
    
