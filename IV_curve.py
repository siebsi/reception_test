import visa
from time import sleep
rm = visa.ResourceManager()
rm = visa.ResourceManager("/Library/Frameworks/VISA.framework/VISA")
#print(rm.list_resources())#possible connections
from pymeasure.instruments.keithley import Keithley2400
import matplotlib.pyplot as plt
import csv
import time, datetime
def IVcurve(gpib_adr, vMax, compCurr, stepSize, mydelay): #silicon: IVcuvre(vMax=0, compCurr=0.0001, stepSize=10, delay=1)
    keith_str="GPIB::"+str(gpib_adr)
    #print('IV-CURVE DONE')
    length=int(vMax*1.0/stepSize)
    vArray=[None for i in range(length)]
    iArray=[None for i in range(length)]
    keith = Keithley2400(keith_str)
    keith.reset()
    keith.apply_voltage(None,compCurr)
    keith.enable_source()
    keith.measure_current(1,compCurr,True)
    for i in range(length):
      vArray[i]=stepSize*(i+1)
      keith.ramp_to_voltage(vArray[i])
      sleep(mydelay)
      iArray[i]=keith.current*1000
    print('Voltages:'+str(vArray))
    print('milli-Amps:'+str(iArray))
    keith.shutdown()
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (mA)')
    plt.plot(vArray,iArray)
    plt.show()
    the_time=datetime.datetime.now()
    name='Module TEST -'+str(the_time.day)+"-"+str(the_time.month)+"-"+str(the_time.year)+'.csv'#"_"+str(the_time.hour)+"-"+str(the_time.minute)+str(the_time.second)+'.csv'
    with open('IV_LOG/'+name, 'w') as csvfile:
      spamwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
      spamwriter.writerow(vArray)
      spamwriter.writerow(i Array)
    return(vArray,iArray)

#(v,i)=IVcurve(4, 5, 0.01, 0.4, 0.2)
