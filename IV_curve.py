import visa
import numpy as np
from time import sleep
rm = visa.ResourceManager()
rm = visa.ResourceManager("/Library/Frameworks/VISA.framework/VISA")
#print(rm.list_resources())#possible connections
from pymeasure.instruments.keithley import Keithley2400
def IVcurve(gpib_adr, vMax, compCurr, stepSize, mydelay): #silicon: IVcuvre(vMax=0, compCurr=0.0001, stepSize=10, delay=1)
    keith_str="GPIB::"+str(gpib_adr)
    #print('IV-CURVE DONE')
    length=int(vMax*1.0/stepSize)
    vArray=[None for i in range(length)]
    iArray=[[None for j in range(5)] for i in range(length)]
    iArray_median=[None for i in range(length)]
    keith = Keithley2400(keith_str)
    keith.reset()
    keith.apply_voltage(None,compCurr)
    keith.enable_source()
    keith.measure_current(1,compCurr,True)
    for i in range(length):
        vArray[i]=stepSize*(i+1)
        keith.ramp_to_voltage(vArray[i],2,0.02)
        sleep(mydelay)
        for j in range(5):
            #vArray[i]=300-stepSize*(i)
            iArray[i][j]=keith.current*1000
            sleep(0.5)
        print(iArray[i])
        iArray_median[i]=np.median(np.array(iArray[i]))
    print('Voltages:'+str(vArray))
    print('milli-Amps:'+str(iArray_median))
    keith.shutdown()
    return(vArray,iArray_median)

#(v,i)=IVcurve(4, 300, 0.001, 10 , 5) #gpib_adr, vMax, complianceCurrent, stepSize, delay_between_steps
