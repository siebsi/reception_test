# coding=utf-8
import zmq,yaml
import os,time,datetime
import bitarray,struct
from unpacker import unpacker
from rpi_data_tests import checker #for data tests
from optparse import OptionParser
import skiroc2cms_bit_string as sk2conf
import client_GUI
import common_variables
import math
import IV_curve
from pprint import pprint
import matplotlib.pyplot as plt
import csv
import visa
from pymeasure.instruments.keithley import Keithley2400
from time import sleep

class yaml_config:
    default_options=yaml.YAMLObject() #vermutlich darf ich options nicht aendern - wegen config Line 95
    sca_variables=yaml.YAMLObject()
    toa_tot_variables=yaml.YAMLObject()
    iv_variables=yaml.YAMLObject()

    def __init__(self,filename):
        self.default_options=yaml.safe_load(open(filename))['default_options']
        self.sca_variables=yaml.safe_load(open(filename))['sca_variables']
        self.toa_tot_variables=yaml.safe_load(open(filename))['toa_tot_variables']
        self.iv_variables=yaml.safe_load(open(filename))['iv_variables']

    def dump(self):
        #print('Conf-string:')
        #print(yaml.dump(self.default_options))
        return yaml.dump(self.default_options)

    def dumpToYaml(self,fname):
        with open(fname,'w') as fout:
            yaml.dump({'default_options': self.default_options},fout)
            print('HERE')
            print(self.sca_variables)
            print('DONE')
            yaml.dump({'sca_variables': self.sca_variables},fout)
            yaml.dump({'toa_tot_variables': self.toa_tot_variables},fout)
            yaml.dump({'iv_variables': self.iv_variables},fout)

def get_comma_separated_args(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

'''-----------Define Configuration---------'''

filename='teststand_1_config.yaml' #changeable by parser (later)

parser = OptionParser()
parser.add_option('-e','--dataNotSaved',dest="dataNotSaved",action="store_true",default=False,
                  help="set to true if you don't want to save the data (and the yaml file)")
'''parser.add_option('-g','--noGui',dest="guiOFF",action="store_true",default=False,
                  help="set to true if you don't want to use the gui")
parser.add_option("-a", "--externalChargeInjection", dest="externalChargeInjection",action="store_true",
                  help="set to use external injection",default=False)
choices_m=["standard","sweep","fixed","const_inj","instrumental_trigger","external_trigger"]
parser.add_option("-b", "--acquisitionType", dest="acquisitionType",choices=choices_m,
                  help="acquisition method, valid choices are:\t%s"%(choices_m), default="standard")
parser.add_option('-c', '--channelIds', dest="channelIds",action="callback",type=str,
                  help="channel Ids for charge injection", callback=get_comma_separated_args, default=[])
parser.add_option('-d','--injectionDAC',dest="injectionDAC",type="int",action="store",default=1000,
                  help="DAC setting for injection when acquisitionType is const_inj")
parser.add_option("-f", "--pulseDelay", dest="pulseDelay",type="int",action="store",
                  help="pulse delay (arbitrary unit) w.r.t. the trigger",default=72)'''
(options, args) = parser.parse_args()
print('parser_stuff:',options)

'''-----------Setup Communication to the Pi-----------'''
#'''
#in Python3, all strings are represeted in unicode -> socket.send works just for bytes.
#Use socket.send_string instead! (http://pyzmq.readthedocs.io/en/latest/unicode.html#unicode)
#'''

config=yaml_config(filename)####hier file input einfügen, parser options!
daq_options=config.default_options['daq_options']
glb_options=config.default_options['glb_options']
testswitches=config.default_options['testswitches']
iv_stuff=config.iv_variables

"""print('BEFORE:')
pprint(glb_options)
pprint(daq_options)"""
'''daq_options['acquisitionType']=options.acquisitionType
daq_options['externalChargeInjection']=options.externalChargeInjection
daq_options['injectionDAC']=options.injectionDAC
daq_options['pulseDelay']=options.pulseDelay
daq_options['channelIds'].append(options.channelIds)'''

datadir = "/Users/patricksieberer/Documents/reception_test/pchgcal_data/2018/tests_20_09/"

def run_test():
    os.system("rm yamlConfigOutput data IV_LOG")
    os.system("mkdir -p " + datadir + "raw/module"+str(glb_options['moduleNumber']))
    os.system("mkdir -p " + datadir + "yaml/module"+str(glb_options['moduleNumber']))
    os.system("mkdir -p " + datadir + "iv/module"+str(glb_options['moduleNumber']))
    os.system("ln -s -F " + datadir + "raw/module"+str(glb_options['moduleNumber'])+" data")
    os.system("ln -s -F " + datadir + "yaml/module"+str(glb_options['moduleNumber'])+" yamlConfigOutput")
    os.system("ln -s -F " + datadir + "iv/module"+str(glb_options['moduleNumber'])+" IV_LOG")
    """print('AFTER:')
    pprint("Global options = "+yaml.dump(glb_options))
    pprint("DAQ options = "+yaml.dump(daq_options))"""
    #pprint("testswitches = "+yaml.dump(testswitches))
    the_time=datetime.datetime.now()
    if testswitches['IV_curve']==True:
        (voltArray,currArray)=IV_curve.IVcurve(iv_stuff['gpib_adr'], iv_stuff['vMax'], iv_stuff['compCurr'],iv_stuff['stepSize'], iv_stuff['delay']) #gpib_adr, vMax, complianceCurrent, stepSize, delay_between_steps
        plt.figure(1)
        plt.xlabel('Voltage (V)')
        plt.ylabel('Current (mA)')
        plt.title('Module '+str(glb_options['moduleNumber']))
        plt.plot(voltArray,currArray)
        #plt.plot(voltArray,currArray[0],'r',voltArray,currArray[1],'b',voltArray,currArray[2],'g',voltArray,currArray[3],'k',voltArray,currArray[4],'y')
        ivName=glb_options['outputIVPath']+"/Module"+str(glb_options['moduleNumber'])+"_"
        ivName=ivName+str(the_time.day)+"-"+str(the_time.month)+"-"+str(the_time.year)+"_"+str(the_time.hour)+"-"+str(the_time.minute)+"-"+str(the_time.second)
        if (int(daq_options['hv'])==0):
            ivName+='_HV_OFF'
        ivName=ivName+".pdf"
        plt.savefig(ivName)
        #plt.show()
        plt.close(1)
        ivName=glb_options['outputIVPath']+"/Module"+str(glb_options['moduleNumber'])+"_"
        ivName=ivName+str(the_time.day)+"-"+str(the_time.month)+"-"+str(the_time.year)+"_"+str(the_time.hour)+"-"+str(the_time.minute)+"-"+str(the_time.second)
        if (int(daq_options['hv'])==0):
            ivName+='_HV_OFF'
        ivName=ivName+".csv"
        csvfile = open(ivName, "w")
        firstrow='Date:'+str(the_time.day)+"-"+str(the_time.month)+"-"+str(the_time.year)+"_Time:"+str(the_time.hour)+"-"+str(the_time.minute)+"-"+str(the_time.second)
        secondrow='Module_Number:'+str(glb_options['moduleNumber'])
        thirdrow='vMAX='+str(iv_stuff['vMax'])+'-'+'compcurrent='+str(iv_stuff['compCurr'])+'-'+'stepsize='+str(iv_stuff['stepSize'])+'-'+'delay='+str(iv_stuff['delay'])
        fourthrow='temp:'+iv_stuff['temperature']+'_humidity:'+iv_stuff['humidity']
        csvfile.writelines([str(firstrow)+'\n',str(secondrow)+'\n',str(thirdrow)+'\n',str(fourthrow)+'\n'])
        for i in range(len(voltArray)):
            csvfile.write(str(voltArray[i])+' '+str(currArray[i])+'\n')
            #csvfile.write(str(voltArray[i])+' '+str(currArray[0][i])+' '+str(currArray[1][i])+' '+str(currArray[2][i])+' '+str(currArray[3][i])+' '+str(currArray[4][i])+'\n')
        csvfile.close()
    #Set HV
    keith_str="GPIB::"+str(iv_stuff['gpib_adr'])
    keith = Keithley2400(keith_str)
    keith.reset()
    keith.apply_voltage(None,iv_stuff['compCurr'])
    keith.enable_source()
    keith.ramp_to_voltage(int(daq_options['hv']))
    keith.measure_current(1,iv_stuff['compCurr'],True)
    sleep(5)
    if glb_options['startServerManually']==False:
        os.system("ssh -T pi@"+glb_options['serverIpAdress']+" \"nohup python "+glb_options['serverCodePath']+"/daq-zmq-server.py > log.log 2>&1& \"")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    print("Send request to server")
    socket.connect("tcp://"+glb_options['serverIpAdress']+":5555")
    cmd="DAQ_CONFIG"
    print(cmd)
    socket.send_string(cmd)
    status=socket.recv_string()
    print(status)
    if status=="READY_FOR_CONFIG":
        socket.send_string(config.dump())
        the_config=socket.recv_string()
        print("Returned DAQ_CONFIG:\n%s"%the_config)
    else:
        print("WRONG STATUS -> exit()",status)
        exit()

    dataSize=30786 # 30784 + 2 for injection value
    if daq_options['compressRawData']==True:
            dataSize=15394 # 30784/2 + 2 for injection value
    dataStringUnpacker=struct.Struct('B'*dataSize)

    outputFile=None
    if options.dataNotSaved==False:
        while True:
            rawFileName=glb_options['outputRawDataPath']+"/Module"+str(glb_options['moduleNumber'])+"_"
            rawFileName=rawFileName+str(the_time.day)+"-"+str(the_time.month)+"-"+str(the_time.year)+"_"+str(the_time.hour)+"-"+str(the_time.minute)+"-"+str(the_time.second)
            if (int(daq_options['hv'])==0):
                rawFileName+='_HV_OFF'
            rawFileName=rawFileName+".raw"
            if os.path.exists(rawFileName): #to avoid overwriting
                continue
            else:
                print("open output file : ",rawFileName)
                outputFile = open(rawFileName,'wb')
                if glb_options['storeYamlFile']==True:
                    yamlFileName=glb_options['outputYamlPath']+"/Module"+str(glb_options['moduleNumber'])+"_"
                    yamlFileName=yamlFileName+str(the_time.day)+"-"+str(the_time.month)+"-"+str(the_time.year)+"_"+str(the_time.hour)+"-"+str(the_time.minute)+"-"+str(the_time.second)
                    if (int(daq_options['hv'])==0):
                        yamlFileName+='_HV_OFF'
                    yamlFileName=yamlFileName+".yaml"
                    print("save yaml file : ",yamlFileName)
                    config.dumpToYaml(yamlFileName)
                break

    '''-------Write Configuration to Pi-------'''

    cmd="CONFIGURE"
    print(cmd)
    socket.send_string(cmd)
    return_bitstring = socket.recv_string()
    print("Returned bit string = ",return_bitstring)
    bitstring=[int(i,16) for i in return_bitstring.split()]
    print("\t write bits string in output file")
    byteArray = bytearray(bitstring)
    if options.dataNotSaved==False:
        outputFile.write(byteArray)
    '''the_bit_string=sk2conf.bit_string()
    if daq_options['externalChargeInjection']==True:
        the_bit_string.set_channels_for_charge_injection(daq_options['channelIds'])
    if daq_options['preampFeedbackCapacitance']>63:
        print("!!!!!!!!! WARNING :: preampFeedbackCapacitance should not be higher than 63 !!!!!!!")
    the_bit_string.set_preamp_feedback_capacitance(daq_options['preampFeedbackCapacitance'])
    the_bit_string.set_channels_to_mask(daq_options['channelIdsToMask'])
    the_bit_string.set_channels_to_disable_trigger_tot(daq_options['channelIdsDisableTOT'])
    the_bit_string.set_channels_to_disable_trigger_toa(daq_options['channelIdsDisableTOA'])
    the_bit_string.set_lg_shaping_time(daq_options['shapingTime'])
    the_bit_string.set_hg_shaping_time(daq_options['shapingTime'])
    the_bit_string.set_tot_dac_threshold(daq_options['totDACThreshold'])
    a=the_bit_string.get_48_unsigned_char_p()
    #the_bit_string.Print()
    print( "outputBitString", [hex(a[i]) for i in range(len(a))] )'''   #still wrong!!!! Config Test missing!


    '''-----------Read Events and Online Data-analysis---------'''

    cmd="PROCESS_AND_PUSH_N_EVENTS"
    socket.send_string(cmd)
    mes=socket.recv_string()
    print('\t***',mes,'***')
    puller=context.socket(zmq.PULL)
    puller.connect("tcp://"+glb_options['serverIpAdress']+":5556")
    try:
        while True:
            full_noise_counter=[[0 for i in range(64)]for sk in testswitches['chip_array']]
            full_broken_counter=[[0 for i in range(64)] for sk in testswitches['chip_array']]
            full_to_counter=[[0 for i in range(64)] for sk in testswitches['chip_array']]
            for i in range(daq_options['nEvent']):
                daq_options['currEvent']=i
                str_data=puller.recv()
                rawdata=dataStringUnpacker.unpack(str_data)
                print("\n \n \n Receive event ",i)
                ''' #######ONLINE DATA TESTS######'''
                '''Setup'''
                byteArray = bytearray(rawdata)
                up=unpacker()
                up.unpack(byteArray)
                #up.showData(i)
                data_to_check=checker(up.sk2cms_data,up.rollMask,config)
                '''Perform tests: (see rpi_data_tests.py for details)'''
                if(testswitches['RollMask_full_ON']):
                    rm=data_to_check.check_full_RollMask()
                    for sk in testswitches['chip_array']:
                        if(rm[sk] == True): #Once a Rollmask issue = everytime a Rollmask issue
                            common_variables.rollMask_issue[sk]=True
                        else:
                            common_variables.rollMask_issue[sk]=False

                #if common_variables.rollMask_issue[0]==True:
                #    break

                if(testswitches['SCA_full_ON']):
                    noisy_ch_counter=0; noisy_channels=[]; broken_ch_counter=0; broken_channels=[] #initialization of the output variables of the current test
                    (noisy_ch_counter,noisy_channels,broken_ch_counter,broken_channels)=data_to_check.check_full_sca()
                    current_ch_broken_limit=math.ceil(config.sca_variables['th_n_ev_broken']*float(i+1)) #How many times a channel needs to be broken in order to be considered as broken
                    common_variables.broken_ch_list=[[None for i in range(0)] for sk in testswitches['chip_array']]
                    current_ch_noisy_limit=math.ceil(config.sca_variables['th_n_ev_noisy']*float(i+1)) #How many times a channel needs to be noisy in order to be considered as noisy
                    common_variables.noisy_ch_list=[[None for i in range(0)] for sk in testswitches['chip_array']]
                    for sk in testswitches['chip_array']:
                        for j in broken_channels[sk]:
                            full_broken_counter[sk][j]+=1
                        for j in noisy_channels[sk]:
                            full_noise_counter[sk][j]+=1
                        for j in range(64):
                            if(full_broken_counter[sk][j]>=current_ch_broken_limit):
                                #print(len(common_variables.broken_ch_list[1]))
                                common_variables.broken_ch_list[sk].append(j)
                            if(full_noise_counter[sk][j]>=current_ch_noisy_limit):
                                common_variables.noisy_ch_list[sk].append(j)
                        common_variables.n_noisy_ch_chip[sk]=len(common_variables.noisy_ch_list[sk]) #global for all event done so far
                        common_variables.n_broken_ch_chip[sk]=len(common_variables.broken_ch_list[sk]) #global for all event done so far
                        common_variables.chip_broken[sk]=(common_variables.n_broken_ch_chip[sk]>=config.sca_variables['th_broken_ch_chip'])
                        common_variables.chip_noisy[sk]=(common_variables.n_noisy_ch_chip[sk]>=config.sca_variables['th_noisy_ch_chip'])
                        if common_variables.chip_broken[sk]==True:
                            common_variables.hexaboard_broken=True
                        if common_variables.chip_noisy[sk]==True:
                            common_variables.hexaboard_noisy=True

                if(testswitches['ToT_ToA_full_ON']):
                    less_counts_than_threshold=[True for sk in testswitches['chip_array']]; wrong_To_list=[[] for sk in testswitches['chip_array']]
                    (less_counts_than_threshold,wrong_To_list)=data_to_check.check_full_TOA_TOT()
                    current_to_issue_limit=math.ceil(config.toa_tot_variables['th_n_ev_to_issue']*float(i+1))
                    common_variables.to_issue_ch_list=[[None for i in range(0)] for sk in testswitches['chip_array']]
                    for sk in testswitches['chip_array']:
                        for j in wrong_To_list[sk]:
                            full_to_counter[sk][j]+=1
                        for j in range(64):
                            if(full_to_counter[sk][j]>=current_to_issue_limit):
                                common_variables.to_issue_ch_list[sk].append(j)
                        common_variables.n_to_issues_chip[sk]=len(common_variables.to_issue_ch_list[sk]) #global for all event done so far
                        common_variables.chip_to_issue[sk]=(common_variables.n_to_issues_chip[sk]>=config.toa_tot_variables['th_to_ch_issue_chip'])
                        if common_variables.chip_to_issue[sk]==True:
                            common_variables.hexaboard_to_issue=True

                if(testswitches['printUnusualData_ON']):
                    data_to_check.printUnusualData()#full test
                '''print file'''
                if True: #options.dataNotSaved==False:
                    outputFile.write(byteArray)

                #calculate final result for chips and the HB
                for sk in testswitches['chip_array']:
                    bool_tests_executed_passed=((not testswitches['RollMask_full_ON'] or not common_variables.rollMask_issue[sk])and(not testswitches['SCA_full_ON'] or not common_variables.chip_broken[sk])) #only RM and SCA-broken can make the whole test fail
                    if(bool_tests_executed_passed):
                        common_variables.chip_results[sk]='PASS'
                        if common_variables.chip_noisy[sk]:
                            common_variables.chip_results[sk]+=' -NOISY'
                        if common_variables.chip_to_issue[sk]:
                            common_variables.chip_results[sk]+=' -TO_ISSUE'
                    else:
                        common_variables.chip_results[sk]='FAIL'

                common_variables.DUT_result='PASS'
                for sk in testswitches['chip_array']:
                    if common_variables.chip_results[sk]=='FAIL':
                        common_variables.DUT_result='FAIL'
                        break
                    elif common_variables.chip_results[sk]=='PASS -NOISY':
                        common_variables.DUT_result+=' '+str(sk)+'-NOISY'
                    elif common_variables.chip_results[sk]=='PASS -TO_ISSUE':
                        common_variables.DUT_result+=' '+str(sk)+'-TO_ISSUE'
                    elif common_variables.chip_results[sk]=='PASS -NOISY -TO_ISSUE':
                        common_variables.DUT_result+=' '+str(sk)+'-NOISY-TO_ISSUE'
            puller.close()
            socket.send_string("END_OF_RUN")
            if socket.recv_string()=="CLOSING_SERVER":
                print("CLOSING SERVER")
                socket.close()
                context.term()
            break

    except KeyboardInterrupt:
        print("keyboard interruption")
        keith.shutdown()
        os.system("ssh -T pi@"+glb_options['serverIpAdress']+" \" killall python\"")
    keith.shutdown()

'''-----------Class for GUI - APP---------'''
from kivy.app import App
class Select_and_launch_testsApp(App):
    def build(self):
        return client_GUI.Select_and_launch_tests(run_test,config)

if bool(1):
    myApp=Select_and_launch_testsApp()
    print('Select the tests you want to make and press LAUNCH')
    myApp.run()
else:
    run_test()
