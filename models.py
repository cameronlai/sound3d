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
    def __init__(self, input_music_file):
        """
        Constructor
        """
        # Hard-coded configurations
        self.num_audio_sections = 10
        self.num_downsample = 20

        # File members
        self.scad_file = NamedTemporaryFile(suffix='.scad')
        self.data_file = NamedTemporaryFile(suffix='.dat')
        self.wave_file = NamedTemporaryFile(suffix='.wav')
        self.stl_file = NamedTemporaryFile(suffix='.stl')
        self.music_file = None
        self.output_file_name = None
        self.set_music_file(input_music_file) # self.music_file

        # Output members
        self.points = np.zeros([self.num_audio_sections, self.num_downsample])

    def __del__(self):
        self.scad_file.close()
        self.data_file.close()
        self.wave_file.close()
        self.stl_file.close()
        self.music_file.close()

    def gen_online(self):
        """
        This function returns the HTTP response with the STL file
        """
        self.gen_offline()
        if self.points.shape[0] == 0:
            return None

        # Print to dat file
        self._seek_all()
        self.write_points_to_file(self.data_file)

        # Generate STL file        
        current_dir = os.getcwd()
        os.chdir(os.path.dirname(self.data_file.name))
        self.scad_file.write('surface(file = "' + os.path.basename(self.data_file.name) + '", center = true, convexity = 5);')  
        cmd = 'openscad -o ' + os.path.basename(self.stl_file.name) + ' ' + os.path.basename(self.scad_file.name)
        self._seek_all()
        ret = call(cmd, shell=True)
        os.chdir(current_dir)

        # Copy STL file to HttpResponse
        response = HttpResponse(content_type='application/txt')
        response['Content-Disposition'] = 'attachment; filename="%s.stl"' \
            % os.path.splitext(os.path.basename(self.output_file_name))[0]

        # Copy file over to the download file
        self._seek_all()
        f = FileDj(response)
        for line in self.stl_file:
            f.write(line)

        return response

    def gen_offline(self):
        """
        Opens the wave file and produces the points for the desired art shape
        Currently, it only generates the spectrum
        """
        ret = self._convert_to_wav()
        if ret:
            return np.array([])

        # Start using the wave file
        self._seek_all()
        waveFile = wave.open(self.wave_file.name, 'r')
        inputSignal = np.fromstring(waveFile.readframes(-1), 'Int16')
        fs = waveFile.getframerate()
        
        # If Stereo
        if waveFile.getnchannels() == 2:
            return np.array([])

        # Pad zeros to fit in everything
        sample_per_section = self.num_audio_sections * self.num_downsample
        pad_zero_remainder = inputSignal.shape[0] % sample_per_section
        if pad_zero_remainder:
            inputSignal = np.pad(inputSignal, (0, sample_per_section - pad_zero_remainder), 'constant', constant_values=(0,0))

        # Reshape
        reshapedSignal = inputSignal.reshape(self.num_audio_sections, -1)

        # For loop to get all spectrum points
        for idx in range(self.num_audio_sections):
            tmpSignal = reshapedSignal[idx]
            tmpSignal = tmpSignal.reshape(self.num_downsample, -1)
            tmpSignal = tmpSignal.mean(axis=1)

            # FFT
            #timeInfo =np.linspace(0, len(tmpSignal)/fs, num=len(tmpSignal))
            #freqInfo = np.fft.fftfreq(timeInfo.shape[-1])
            self.points[idx] = np.absolute(np.fft.fft(tmpSignal))
            self.points[idx] = np.round(self.points[idx] / 1000.0, 2)

        waveFile.close()

    def set_music_file(self, input_music_file):
        file_extension = os.path.splitext(input_music_file.name)[1]
        self.music_file = NamedTemporaryFile(suffix=file_extension)
        for chunk in input_music_file.chunks():
            self.music_file.write(chunk)
        self.output_file_name = os.path.splitext(os.path.basename(input_music_file.name))[0]

    def _seek_all(self):
        self.scad_file.seek(0)
        self.data_file.seek(0)
        self.wave_file.seek(0)
        self.stl_file.seek(0)
        self.music_file.seek(0)

    def _convert_to_wav(self):
        """
        Converts an input music file into a wave file with only one channel output only
        """
        cmd = ' '.join(['ffmpeg -i', self.music_file.name, 
                        '-y -acodec pcm_s16le -ac 1 -ar 44100', self.wave_file.name])
        self._seek_all()
        ret = call(cmd, shell=True)
        return ret
    
    def write_points_to_file(self, fileObj):
        """
        Writes points to file
        """
        if self.points is not None:
            for rowIdx in range(self.points.shape[0]):
                rowPointStr = ' '.join(map(str, self.points[rowIdx]))
                fileObj.write(rowPointStr + '\n')

if __name__ == "__main__":
    f = FileDj(open('scad/Track1.wav'))
    mGenerator = sound3dGenerator(f)
    mGenerator.gen_offline()
    f.close()

    f = open('scad/test.dat', 'w')
    mGenerator.write_points_to_file(f)
    f.close()
