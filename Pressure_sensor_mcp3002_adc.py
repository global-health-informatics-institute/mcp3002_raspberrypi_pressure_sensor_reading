import time
import spidev

spi_ch = 0

pressure_zero = 153
pref = float(60)
vref = float(3.3)
pressureValue = float(0.00)
pressureMax = 871


#Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

def read_adc(adc_ch, ref):
    
    #make sure adc channel is 0 or 1
    if adc_ch != 0:
        adc_ch = 1
        #construct spi message
        #first bit (start): Logic high (1)
        #second bit (SGL/DIFF):1 to select single mode
        #Third bit (ODD/SIGN): Select channel (0 or 1)
        #Fourth bit (MSFB): 0 for LSB first
        #Next 12 bits: 0 (don't care)
            
        msg = 0b11
        msg = ((msg << 1) + adc_ch) << 5
        msg = [msg, 0b00000000]
        reply = spi.xfer2(msg)
        
        # construct single integer out of the reply (2 bytes)
        adc = 0
        for n in reply:
            adc = (adc << 8) + n
        
        # Last bit (0) is not part of ADC value, shift to remove it
        adc = adc >> 1
        
        #calculate voltage from ADC value
        voltage = (ref * adc) / 1024
        print(adc)
        return voltage
    
    #calculate the pressure from ADC value
    msg = 0b11
    msg = ((msg << 1) + adc_ch) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)
    
    # construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n
    
    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1
    
    adc = adc - pressure_zero
    
    #calculate voltage from ADC value
    pressure = (ref * adc) / pressureMax
    print(adc)
    return pressure

# report channel 0 and channel 1 voltages to the terminal
try:
    while True:
        adc_0 = read_adc(0, pref)
        adc_1 = read_adc(1, vref)
        pressureValue = adc_0
       
        if pressureValue < 0:
            pressureValue = 0;
        
        print("Pressure (psi):", round(pressureValue, 2), "Potentiometer (v):", round(adc_1, 2))
        time.sleep(0.2)

finally:
    GPIO.cleanup()
