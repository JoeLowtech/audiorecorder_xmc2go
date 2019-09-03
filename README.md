# XMC2Go Audioaufzeichnung mit Python
Der XMC2Go hat selbst sehr wenig Speicherplatz. Um Audiodaten aufzunehmen, müssen die Samples an einen PC übertragen und abgespeichert werden.
Hier soll gezeigt werden, wie mit einem XMC2Go, der mit einem Mikrofon (IM69D310) ausgestattet ist, Audiodaten aufgenommen und an einen PC geschickt werden können.
## Übertragungsgeschwindigkeit für Audiodaten
Bei der Übertragung von Audiodaten können eine Menge Daten anfallen. Je höher die Frequenzauflösung, desto höher ist die zu übertragende Datenmenge. Die Samplerate gibt Auskunft darüber wieviel Werte pro Sekunde übertragen werden. Bei 22 kHz sind das 22000 Samples pro Sekunde.
Die Bitrate gibt an wie groß ein einzelnes Sample ist. Zum Beispiel 16 Bit. Das sind 22000 1/s*16 bit = **352 kbit/s** = **44000 byte/s**. Zusätzlich kommt noch der Overhead für das Übertragungsprotokoll dazu. Bei SLIP sind das im günstigsten Fall 44000 byte/s /8 = **5500 byte/s**.
Die Übertragungsgeschwindigkeit muss also mindestens 44000 + 5500 = **49500 byte/s** bzw **396 kbit/s** betragen.

## XMC2Go sendet Audio
Das Mikrofon ist über die I2S-Schnittstelle verbunden. Es nimmt mit einer Sample-Rate von 11 kHz und 16-Bit auf. Zum Senden wird das SLIP-Protokol verwendet.
Ein Datenpaket besteht aus 8 Bytes plus Overhead. Das heißt es werden immer 4 Samples pro Datenpaket verschickt.
```
Datenpaket:
[        8 Bytes Daten         ]
[2 Byte][2 Byte][2 Byte][2 Byte]
[sample][sample][sample][sample][END]
```
```c++
#include <Arduino.h>
#include <I2S.h>
#include <PacketSerial.h>

SLIPPacketSerial myPacketSerial;
int16_t buffer[16]= {};

void onPacketReceived(const uint8_t* buffer, size_t size)
{
    // Process your decoded incoming packet here.
}

void setup()
{
    myPacketSerial.begin(1000000);
    myPacketSerial.setPacketHandler(&onPacketReceived);

    Serial.println("Begin of I2S microphone");
    // Disable all microphones
    I2S.disableMicrophones();
    // Enable the microphone when word select is low - only one microphone is used
    I2S.enableMicrophoneLow();
    // Start I2S with I2S_PHILIPS_MODE, 11 kHz sampling rate and 16 bits per sample
    // Returns 0 if everything okay, otherwise value > 0
    if( I2S.begin(I2S_PHILIPS_MODE,11000, 16) > 0 ){
        Serial.println("i2s failed!");
    }else {Serial.println("I2S gestarted");}

}

void loop() {
    //checks if samples are available
    while (I2S.available() > 3)
    {   
        //read samples and put them into an array
        for( int i = 0; i <= 3; i++ ){
            buffer[i] = I2S.read();
        }
        //send the array to the pc
         myPacketSerial.send((uint8_t*)buffer,8);
         
    
        if(I2S.getOverflow() == true){
            I2S.flush();
        }  
    }
}
```
<span style="color: #ff0000;">
Anmerkung: Mit dem XMC2Go gab es Schwierigkeiten die UART-Schnittstelle mit 1 MBaud zu konfigurieren. Der XMC2Go versendete keine Daten!
Als Workaround hat es geholfen den XMC2Go im Debug-Modus zu starten.
</span>

## PC empfängt Audio 
Zum Empfangen und dekodieren der Daten wird das Python-Beispiel aus **Simples Datenprotokoll für UART-Schnittstelle** verwendet. Die empfangen Bytes werden in einzelne 8-Byte Pakete aufgeteilt und so konvertiert, das sie in eine Wave-Datei abgelegt werden können.

```python
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
            samples = bytes_to_samples(byte_package)
            if samples:
                wave_write(wave_file, samples)
    else : continue

```
Mit```get_audio_packages()``` werden die Audiopakete eingesammelt und anschließend mit der Funktion ```bytes_to_samples()``` wieder in einzelne Samples geschnitten und so bearbeitet, dass sie in einer Wave-Datei mit```wave_write()``` abgelegt werden können.
