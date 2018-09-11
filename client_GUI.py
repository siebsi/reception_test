import common_variables
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty
from kivy.graphics.instructions import Canvas
from kivy.graphics import Color
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
import yaml_writer
import yaml
#from daq_zmq_client_with_GUI import yaml_config

class Select_and_launch_tests(GridLayout):
    Window.clearcolor = (1, 1, 1, 1) #white background
    Window.size = (2100, 900) #positioning and size
    Window.top = 100
    Window.left = 100
    # conf=yaml.YAMLObject()
    red = ListProperty([1,0,0,1])
    green = ListProperty([0,1,0,1])
    yellow = ListProperty([1,1,0,1])
    gray= ListProperty([0.5,0.5,0.5,1])
    """col_chip0=ListProperty([0.5,0.5,0.5,1])
    col_chip1=ListProperty([0.5,0.5,0.5,1])
    col_chip2=ListProperty([0.5,0.5,0.5,1])
    col_chip3=ListProperty([0.5,0.5,0.5,1])
    col_chip0RM=ListProperty([0.5,0.5,0.5,1])
    col_chip1RM=ListProperty([0.5,0.5,0.5,1])
    col_chip2RM=ListProperty([0.5,0.5,0.5,1])
    col_chip3RM=ListProperty([0.5,0.5,0.5,1])
    col_chip0SCA=ListProperty([0.5,0.5,0.5,1])
    col_chip1SCA=ListProperty([0.5,0.5,0.5,1])
    col_chip2SCA=ListProperty([0.5,0.5,0.5,1])
    col_chip3SCA=ListProperty([0.5,0.5,0.5,1])
    col_chip0TO=ListProperty([0.5,0.5,0.5,1])
    col_chip1TO=ListProperty([0.5,0.5,0.5,1])
    col_chip2TO=ListProperty([0.5,0.5,0.5,1])
    col_chip3TO=ListProperty([0.5,0.5,0.5,1])
    col_DUT=ListProperty([0.5,0.5,0.5,1])"""

    config = None

    def __init__(self,runtest,config):
        super(Select_and_launch_tests, self).__init__()
        self.config = config
        self.my_run=runtest
        self.ids.ev.text=str(config.default_options['daq_options']['nEvent'])
        self.ids.acqtype.text=config.default_options['daq_options']['acquisitionType']
        self.ids.inputch.text=str(config.default_options['daq_options']['channelIds'])
        self.ids.injDAC.text=str(config.default_options['daq_options']['injectionDAC'])
        self.ids.delay.text=str(config.default_options['daq_options']['pulseDelay'])
        self.ids.DUT.text=str(config.default_options['glb_options']['moduleNumber'])
        self.ids.Hardwaretype.text=str(config.default_options['glb_options']['type_of_hardware'])
        self.ids.Manufacturer.text=str(config.default_options['glb_options']['manufacturer'])

#below : change the functions to change the text in the buttons/buttons colors
    def test_full_RollMask(self,obj):
        self.config.default_options['testswitches']['RollMask_full_ON'] = not self.config.default_options['testswitches']['RollMask_full_ON']
        if (self.config.default_options['testswitches']['RollMask_full_ON']==True):
            print ('Test Full RollMask active')
            self.ids.btnRM.background_color= 0.2, 0.6, 0, 1 #light green
        else:
            print ('Test Full RollMask inactive')
            self.ids.btnRM.background_color= 0.5, 0.5, 0.5, 1 #gray

    def test_full_ToT_ToA(self,obj):
        self.config.default_options['testswitches']['ToT_ToA_full_ON']=not self.config.default_options['testswitches']['ToT_ToA_full_ON']
        if (self.config.default_options['testswitches']['ToT_ToA_full_ON']==True):
            print ('Test Full TOA TOT active')
            self.ids.btnTO.background_color= 0.2, 0.6, 0, 1 #light green
        else:
            print ('Test Full TOA TOT inactive')
            self.ids.btnTO.background_color= 0.5, 0.5, 0.5, 1 #gray

    def test_full_SCA(self,obj):
        self.config.default_options['testswitches']['SCA_full_ON']=not self.config.default_options['testswitches']['SCA_full_ON']
        if (self.config.default_options['testswitches']['SCA_full_ON']==True):
            print ('Test Full SCA active')
            self.ids.btnSCA.background_color = 0.2, 0.6, 0, 1 #light green
        else:
            print ('Test Full SCA inactive')
            self.ids.btnSCA.background_color= 0.5, 0.5, 0.5, 1 #gray

    def test_printUnusualData(self,obj):
        self.config.default_options['testswitches']['printUnusualData_ON']=not self.config.default_options['testswitches']['printUnusualData_ON']
        if (self.config.default_options['testswitches']['printUnusualData_ON']==True):
            print ('Test Print unusual Data active')
            self.ids.btnPRINT.background_color = 0.2, 0.6, 0, 1 #light green
        else:
            print ('Test Print unusual Data inactive')
            self.ids.btnPRINT.background_color= 0.5, 0.5, 0.5, 1 #gray

    def test_iv_curve(self,obj):
        self.config.default_options['testswitches']['IV_curve']=not self.config.default_options['testswitches']['IV_curve']
        if (self.config.default_options['testswitches']['IV_curve']==True):
            print ('IV-curve active')
            self.ids.btnIV.background_color = 0.2, 0.6, 0, 1 #light green
        else:
            print ('IV-curve inactive')
            self.ids.btnIV.background_color= 0.5, 0.5, 0.5, 1 #gray

    def do_injection(self,obj):
        if (self.ids.btnINJ.text=='OFF'):
            self.ids.btnINJ.text='ON'
            self.config.default_options['daq_options']['externalChargeInjection']=True
            print('Injection ON')
        else:
            self.ids.btnINJ.text='OFF'
            self.config.default_options['daq_options']['externalChargeInjection']=False
            print('Injection OFF')

    def launch_tests(self,obj):
        self.config.default_options['daq_options']['nEvent']=int(self.ids.ev.text)
        self.config.default_options['daq_options']['acquisitionType']=self.ids.acqtype.text
        self.config.default_options['daq_options']['channelIds']=self.ids.inputch.text
        self.config.default_options['daq_options']['injectionDAC']=int(self.ids.injDAC.text)
        self.config.default_options['daq_options']['pulseDelay']=int(self.ids.delay.text)
        self.config.default_options['glb_options']['moduleNumber']=self.ids.DUT.text
        self.config.default_options['glb_options']['type_of_hardware']=self.ids.Hardwaretype.text
        self.config.default_options['glb_options']['manufacturer']=self.ids.Manufacturer.text

        '''Perform tests: (see rpi_data_tests.py for details)'''
        #Read GUI-Input
        '''common_variables.DuT_name=self.ids.DUT.text
        common_variables.n_ev=int(self.ids.ev.text)
        common_variables.Type_of_hardware=self.ids.Hardwaretype.text
        common_variables.Manufacturer=self.ids.Manufacturer.text
        common_variables.acquisitionType=self.ids.acqtype.text
        common_variables.injectionDAC=int(self.ids.injDAC.text)
        common_variables.pulse_delay=int(self.ids.delay.text)
        common_variables.inputch=[int(self.ids.inputch.text)]'''

        """#Reset Result Colors
        self.col_chip0=self.gray
        self.col_chip1=self.gray
        self.col_chip2=self.gray
        self.col_chip3=self.gray
        self.col_chip0RM=self.gray
        self.col_chip1RM=self.gray
        self.col_chip2RM=self.gray
        self.col_chip3RM=self.gray
        self.col_chip0SCA=self.gray
        self.col_chip1SCA=self.gray
        self.col_chip2SCA=self.gray
        self.col_chip3SCA=self.gray
        self.col_chip0TO=self.gray
        self.col_chip1TO=self.gray
        self.col_chip2TO=self.gray
        self.col_chip3TO=self.gray
        self.col_DUT=self.gray"""
        #Perform tests
        self.my_run()
        """#Change Result Label colours
        if(self.config.default_options['testswitches']['RollMask_full_ON']):
            if(common_variables.rollMask_issue[0]):
                self.col_chip0RM=self.red
            else:
                self.col_chip0RM=self.green
            if(common_variables.rollMask_issue[1]):
                self.col_chip1RM=self.red
            else:
                self.col_chip1RM=self.green
            if(common_variables.rollMask_issue[2]):
                self.col_chip2RM=self.red
            else:
                self.col_chip2RM=self.green
            if(common_variables.rollMask_issue[3]):
                self.col_chip3RM=self.red
            else:
                self.col_chip3RM=self.green

        if(self.config.default_options['testswitches']['SCA_full_ON']):
            if(common_variables.chip_broken[0]):
                self.col_chip0SCA=self.red
            elif(common_variables.chip_noisy[0]):
                self.col_chip0SCA=self.yellow
            else:
                self.col_chip0SCA=self.green
            if(common_variables.chip_broken[1]):
                self.col_chip1SCA=self.red
            elif(common_variables.chip_noisy[1]):
                self.col_chip1SCA=self.yellow
            else:
                self.col_chip1SCA=self.green
            if(common_variables.chip_broken[2]):
                self.col_chip2SCA=self.red
            elif(common_variables.chip_noisy[2]):
                self.col_chip2SCA=self.yellow
            else:
                self.col_chip2SCA=self.green
            if(common_variables.chip_broken[3]):
                self.col_chip3SCAs=self.red
            elif(common_variables.chip_noisy[3]):
                self.col_chip3SCA=self.yellow
            else:
                self.col_chip3SCA=self.green

        if(self.config.default_options['testswitches']['ToT_ToA_full_ON']):
            if(common_variables.chip_to_issue[0]):
                self.col_chip0TO=self.red
            else:
                self.col_chip0TO=self.green
            if(common_variables.chip_to_issue[1]):
                self.col_chip1TO=self.red
            else:
                self.col_chip1TO=self.green
            if(common_variables.chip_to_issue[2]):
                self.col_chip2TO=self.red
            else:
                self.col_chip2TO=self.green
            if(common_variables.chip_to_issue[3]):
                self.col_chip3TO=self.red
            else:
                self.col_chip3TO=self.green"""

        if((self.config.default_options['testswitches']['RollMask_full_ON'] or self.config.default_options['testswitches']['ToT_ToA_full_ON']) or self.config.default_options['testswitches']['SCA_full_ON']):
            #yaml_writer.writeLogfile()
            """if(common_variables.chip_results[0]=='FAIL'):
                self.col_chip0=self.red
            elif(common_variables.chip_results[0]=='PASS'):
                self.col_chip0=self.green
            else:
                self.col_chip0=self.yellow
            if(common_variables.chip_results[1]=='FAIL'):
                self.col_chip1=self.red
            elif(common_variables.chip_results[1]=='PASS'):
                self.col_chip1=self.green
            else:
                self.col_chip1=self.yellow
            if(common_variables.chip_results[2]=='FAIL'):
                self.col_chip2=self.red
            elif(common_variables.chip_results[2]=='PASS'):
                self.col_chip2=self.green
            else:
                self.col_chip2=self.yellow
            if(common_variables.chip_results[3]=='FAIL'):
                self.col_chip3=self.red
            elif(common_variables.chip_results[3]=='PASS'):
                self.col_chip3=self.green
            else:
                self.col_chip3=self.yellow
            if(common_variables.DUT_result=='FAIL'):
                self.col_DUT=self.red
            elif(common_variables.DUT_result=='PASS'):
                self.col_DUT=self.green
            else:
                self.col_DUT=self.yellow"""
