import wave
import struct
import packetserial_slip

get_audio_packages = packetserial_slip.get_packages

"""
# .wav params
nchannels = 1
sample_width = 2
nframes = 0
sampleRate = 11000
comptype = "NONE"
compname = "not compressed"
# Open a wav file
wavFile=wave.open("output.wav", "w")
# Set the parameters of the wave file
wavFile.setparams((nchannels, sample_width, sampleRate, nframes, comptype, compname))
"""
# creates a wavefile
# create_wavefile(tuple)
# Parameter file_specs: (name, (nchannels, sample_width, sampleRate, nframes, comptype, compname))
                        # defaults
                        # name = "output.wav"
                        # nchannels = 1
                        # sample_width = 2
                        # nframes = 0
                        # sampleRate = 11000
                        # comptype = "NONE"
                        # compname = "not compressed"  
# returns the object wave_file
def create_wavefile(file_specs = ("output.wav", (1, 2, 11000, 0, "NONE", "not compressed"))):
    name , parameter = file_specs
    wave_file = wave.open(name ,"w")
    wave_file.setparams(parameter)
    return wave_file

# converts byte packages to tupel filled with integers
# bytes_to_samples(bytes,int,str)
# Parameter : byte_data = data which is converted
#             sample_width = width of Integer in bytes
#             fmt = format - indication for the struct : h for 16-bit sample width; i for 32-bit sample width
# returns samples as tupel filled with integers
def bytes_to_samples(byte_data, sample_width = 2, fmt = 'h'):
    if len(byte_data) % sample_width == 0 :
        samples_length = str(len(byte_data)//sample_width)
        return struct.unpack('<'+ samples_length + fmt,byte_data)
    else :
        return False

# write tupel/list to wave-file
# wave_write(wave-object,tuple/list,str)
# Parameter: wave_file = wave-object
#            samples = data to write into wave_file
#            fmt = fmt = format - indication for the struct : h for 16-bit sample width; i for 32-bit sample width
def wave_write (wave_file, samples, fmt = 'h'): 
    wave_file.writeframes(struct.pack(str(len(samples)) + fmt, *samples))

wave_file = create_wavefile()

while True:
    audio_packages = get_audio_packages()
    if audio_packages:
        for byte_package in audio_packages:
            print(byte_package)
            samples = bytes_to_samples(byte_package)
            if samples:
                wave_write(wave_file, samples)
    else : continue
