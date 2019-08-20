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
    
    while (I2S.available() > 3)
    {   
        //get samples into an array
        for( int i = 0; i <= 3; i++ ){
            buffer[i] = I2S.read();
        }
        //send array to pc
         myPacketSerial.send((uint8_t*)buffer,8);
         
    
        if(I2S.getOverflow() == true){
            I2S.flush();
        }  
    
    }
    
}