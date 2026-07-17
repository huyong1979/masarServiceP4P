'''
Created on Mar 7, 2012

@author: shengb
'''

"""
This is am template file how to config MASAR serviceconfiguration
and load service info, pv_group, and event configuration.
"""

# pv group name: [pv list file, description]
pvgroups= {
           'SR_ID_RB_20141015':                  ['SR_All_SCR_20141015/PV_ID_SR_20141003.TXT', 'SR ID readback'],
           # Storage Ring Power Supply Calibration Data
           #'SR_Quad_Sext_DCCT_Cal_20140917':     ['PS_Calc_20140917/PSI_DCCT_cal.pvs',    'Quad & Sext DCCT Calc'],
           #'SR_Quad_Sext_DAC_Cal_20140917':      ['PS_Calc_20140917/PSI_DAC_cal.pvs',     'Quad & Sext DAC Calc'],
           #'SR_Quad_Sext_PSV_Cal_20140917':      ['PS_Calc_20140917/PSI_Voltage_cal.pvs', 'Quad & Sext PS Voltage Calc'],
           #'SR_Quad_Sext_GNDI_Cal_20140917':     ['PS_Calc_20140917/PSI_Ground_cal.pvs',  'Quad & Sext Grounding Calc'],
           #'SR_Quad_Sext_RampRate_Val_20140917': ['PS_Calc_20140917/Ramprate_val.pvs',    'Quad & Sext Ramping rate'],

           # add ID BPMs for C03, C05, C08, C10, C11, C23, C28, C30
           #'SR_Diag_BPM_Atten_20140626':   ['BPMwIDs_20140625/SR_Diag_BPM_Atten_Wids.txt', 'RF Attenuator Setting'],
           #'SR_Diag_BPM_Offsets_20140626': ['BPMwIDs_20140625/SR_Diag_BPM_Offsets_Wids.txt', 'BBA, User and Reference Offset Settings'],
           #'SR_Diag_BPM_Timing_20140626':  ['BPMwIDs_20140625/SR_Diag_BPM_Timing_Wids.txt', 'Timing and Event Code Settings'],
           #'SR_Diag_BPM_Control_20140626': ['BPMwIDs_20140625/SR_Diag_BPM_Control_Wids.txt', "Control and Readout related PVs"],

           #'SR_Diag_BPM_Atten_20140423':   ['BPM_20140423/SR_Diag_BPM_Atten.txt', 'RF Attenuator Setting'],
           #'SR_Diag_BPM_Offsets_20140423': ['BPM_20140423/SR_Diag_BPM_Offsets.txt', 'BBA, User and Reference Offset Settings'],
           #'SR_Diag_BPM_SDI_20140423':     ['BPM_20140423/SR_Diag_BPM_SDI.txt', 'Fast Orbit Feedback Settings'],
           #'SR_Diag_BPM_Timing_20140423':  ['BPM_20140423/SR_Diag_BPM_Timing.txt', 'Timing and Event Code Settings'],
           #'SR_Diag_BPM_Control_20140423': ['BPM_20140423/SR_Diag_BPM_Control.txt', "Control and Readout related PVs"],
           #'SR_All_SCR_20140421': ['SR_All_20140421/SR-All_20140421.txt', 'All Storage Ring SCR PVs without IS kick and septum'],
           #'LTB_BR_BTS_20140421': ['LTB_BR_BTS_20140421/LTB_BR_BTS_20140421.txt', 'BR SCR PVs with IS kick and septum'],
           #'SR_Diag_BPM_Atten_20140422': ['BPM_20140421/SR_Diag_BPM_Atten.txt', 'RF Attenuator Setting'],
           #'SR_Diag_BPM_Offsets_20140422': ['BPM_20140421/SR_Diag_BPM_Offsets.txt', 'BBA, User and Reference Offset Settings'],
           #'SR_Diag_BPM_SDI_20140422':  ['BPM_20140421/SR_Diag_BPM_SDI.txt', 'Fast Orbit Feedback Settings'],
           #'SR_Diag_BPM_Timing_20140422':  ['BPM_20140421/SR_Diag_BPM_Timing.txt', 'Timing and Event Code Settings'],
           #'SR_Diag_BPM_Control_20140422': ['BPM_20140421/SR_Diag_BPM_Control.txt', "Control and Readout related PVs"],

           #'SR_All_SCR_20140326': ['SR_All_20140326/PV_all_SR_20140326.txt', 'All Storage Ring SCR PVs'],
           #'LTB_BR_BTS_20140328': ['LTB_BR_BTS_20140328/LTB_BR_BTS_20140328.txt', 'BR SCR PVs'],
           #'SR_All_SCR_20140304': ['SR_All_20140304/PV_all_SR.TXT', 'All Storage Ring SCR PVs'],
           #'LTB_BR_BTS_20140307': ['LTB_BR_BTS_20140307/LTB_BR_BTS_BINP2Masar.txt', 'Converted from BINP SCR'],
           # 
           #'Inj_Diag_BI_Control_20140228': ['BPM_20140228/Inj_Diag_BI_Control_20140228.txt', 'Injector BI non-BPM control'],
           # 
           #'Inj_Diag_BPM_Control_20140228': ['BPM_20140228/Inj_Diag_BPM_Control_20140228.txt', 'Injector BI BPM control'],
           # 
           #'Inj_Diag_BPM_Timing_20140228': ['BPM_20140228/Inj_Diag_BPM_Timing_20140228.txt', 'Injector BI BPM timing'],
           # 
           #'SR_Diag_BPM_Control_20140228': ['BPM_20140228/SR_Diag_BPM_Control_20140228.txt', 'Storage Ring BI BPM control'],
           # 
           #'SR_Diag_BPM_Timing_20140228': ['BPM_20140228/SR_Diag_BPM_Timing_20140228.txt', 'Storage Ring BI BPM timing'],
           # incremental pv group for LN Gun
           #'LN_Gun_Set_20131219': ['LN_LTB_All_20131219/LN_Gun_PV_Set.txt', 'linac gun operation Mode, grid voltage, SBM voltage, MBM voltage, and pulse voltage'],
           # Linac, LTB BPM expert 20131213
           #'LN_LTB_BPM_20131213': ['Diag-LN_LTB-allBPM-12.13.2013.expert/Linac_LTB.TXT', 'expert bpm pvs for linac and ltb'],
           # BR BPM Expert 20131213
           #'BR_BPM_20131213':     ['Diag-BR-allBPM-12.13.2013.expert/BR.TXT', 'expoert bpm pvs for booster ring'],
           # BR BPM Expert 20131212
           #'BR_BPM_20131212': ['Diag_BR_allBPM_20131212/BR.txt', 'Booster BPM for expoert'],
           # LN LTB All 20131209
           #'LN_Sol_Set_20131209': ['LN_LTB_All_20131209/LN_Sol_PV_Set.txt', 'linac solenoid current setpoint and on command'],
           #'LN_Cor_Set_20131209': ['LN_LTB_All_20131209/LN_Cor_PV_Set.txt', 'linac corrector x and y plane current setpoint and on command'],
           #'LN_Quad_Set_20131209': ['LN_LTB_All_20131209/LN_Quad_PV_Set.txt', 'linac Quads current setpoint and on command'],
           #'LN_Gun_Set_20131209': ['LN_LTB_All_20131209/LN_Gun_PV_Set.txt', 'linac gun operation Mode, grid voltage, SBM voltage, MBM voltage, and pulse voltage'],
           #'LN_LLRF_Set_20131209': ['LN_LTB_All_20131209/LN_LLRF_PV_Set.txt', 'linac LLRF amplitude, phase, waveform, feedforward setting, tigger event, mode, delay, width including subharmonic buncher, pre-buncher, klystron 1, 2, and 3.'],
           #'LN_HLRF_Set_20131209': ['LN_LTB_All_20131209/LN_HLRF_PV_Set.txt', 'linac HLRF modulator high voltage, pulse width, rep rate, tigger event, mode, delay, width of modulator 1, 2, and 3.'],
           #'LTB_MG_Set_20131209': ['LN_LTB_All_20131209/LTB_MG_PV_Set.txt', 'LTB magnet setpoint and on command'],

           # LTB Power Supply settings
           #'LTB_PS_PS_20131206': ['LTB_PS_SCR_20131206/ltbPS_masarList.txt', 'LTB PS SP'],
           # Booster RF setting
           #'BR_RF_Set_20130426': ['BR_RF_SC_20130426/BR_PV_set.txt', 'Booster RF']
           # Booster magnet power supply set points
           #'BR_MG_Set_20130419': ['pvs/BR_MG_PV_Set.txt', 'Booster magnet power supply set points']
           # test example
           #'test example': ['pvs/example.txt', 'example pv list for meeting at DLS']
           # Linac & LTB bpm group 20120621
#           'LN_LTB_BPM_20120621':           ['BPM/LN_LTB_BPM_20120621.txt', 'expert bpm pvs for linac and ltb']
#           # new pv groups for LN-LTB 20120511
#           'LN_Sol_Set_20120511':          ['LN_LTB_Configure_20120511/LN_Sol_PV_Set.txt',           'linac solenoid current setpoint and on command'],
#           'LN_Cor_Set_20120511':          ['LN_LTB_Configure_20120511/LN_Cor_PV_Set.txt',           'linac corrector x and y plane current setpoint and on command'],
#           'LN_Quad_Set_20120511':         ['LN_LTB_Configure_20120511/LN_Quad_PV_Set.txt',          'linac Quads current setpoint and on command'],
#           'LN_Gun_Set_20120511':          ['LN_LTB_Configure_20120511/LN_Gun_PV_Set.txt',           'linac gun operation Mode, grid voltage, SBM voltage, MBM voltage, and pulse voltage, and trigger event, delay, width setpoint'],
#           'LN_LLRF_Set_20120511':         ['LN_LTB_Configure_20120511/LN_LLRF_PV_Set.txt',          'linac LLRF amplitude, phase, waveform, feedforward setting, tigger event, mode, delay, width including subharmonic buncher, pre-buncher, klystron 1, 2, and 3.'], 
#           'LN_HLRF_Set_20120511':         ['LN_LTB_Configure_20120511/LN_HLRF_PV_Set.txt',          'linac HLRF modulator high voltage, pulse width, rep rate, tigger event, mode, delay, width of modulator 1, 2, and 3. '],
#           'LN_LTB_Diag_Time_Set_20120511':['LN_LTB_Configure_20120511/LN_LTB_Diag_Time_PV_Set.txt', 'linac and LTB digitizer timing setpoint'],
#           'LN_LTB_Dig_Time_Set_20120511': ['LN_LTB_Configure_20120511/LN_LTB_Diag_Scale_PV_Set.txt','linac and LTB digitizer scale setpoint'],
#           'LN_LTB_CamGN_Set_20120511':    ['LN_LTB_Configure_20120511/LN_LTB_CamGN_PV_Set.txt',     'linac and LTB camera exposure time setpoint'],
#           'LN_LTB_CamET_Set_20120511':    ['LN_LTB_Configure_20120511/LN_LTB_CamET_PV_Set.txt',     'linac and LTB camera gain setpoint'],
#           'LN_LTB_CamTrig_Set_20120511':  ['LN_LTB_Configure_20120511/LN_LTB_CamTrig_PV_Set.txt',   'linac and LTB camera trigger setpoint and on command'],
#           'LTB_MG_Set_20120511':          ['LN_LTB_Configure_20120511/LTB_MG_PV_Set.txt',           'LTB magnet setpoint and on command'],
#           'LTB_CamFilt_Set_20120511':     ['LN_LTB_Configure_20120511/LTB_CamFilt_PV_Set.txt',      'LTB camera filter setpoint'],
#           'LTB_ES_Set_20120511':          ['LN_LTB_Configure_20120511/LTB_ES_PV_Set.txt',           'LTB energy slit motor setpoint'],
#           'LN_Time_PV_Set_20120511':      ['LN_LTB_Configure_20120511/LN_Time_PV_Set.txt',          'LN timing setpoint']
#           #LN-LTB-PhaseI-SBM-All_20120426
#           'LN_Sol_Set':           ['LN_Sol_PV_Set.txt',            "linac solenoid current setpoint"],
#           'LN_Cor_Set':           ['LN_Cor_PV_Set.txt',            "linac corrector x and y plane current setpoint"],
#           'LN_Quad_Set':          ['LN_Quad_PV_Set.txt',           "linac Quads current setpoint"],
#           'LN_Gun_SBM_Set':       ['LN_Gun_SBM_PV_Set.txt',        "linac gun operation Mode, grid voltage, SBM voltage, MBM voltage, and pulse voltage, and trigger event, delay, width setpoint"],
#           'LN_LLRF_SBM_Set':      ['LN_LLRF_SBM_PV_Set.txt',       "linac LLRF amplitude, phase, waveform, tigger event, mode, delay, width including subharmonic buncher, pre-buncher, klystron 1, 2, and 3."], 
#           'LN_HLRF_SBM_Set':      ['LN_HLRF_SBM_PV_Set.txt',       "linac HLRF modulator high voltage, pulse width, rep rate, tigger event, mode, delay, width of modulator 1, 2, and 3. "],
#           'LN_LTB_Diag_Time_Set': ['LN_LTB_Diag_Time_PV_Set.txt',  "linac and LTB digitizer timing setpoint"],
#           'LN_LTB_Dig_Time_Set':  ['LN_LTB_Diag_Scale_PV_Set.txt', "linac and LTB digitizer scale setpoint"],
#           'LN_LTB_CamGN_Set':     ['LN_LTB_CamGN_PV_Set.txt',      "linac and LTB camera exposure time setpoint"],
#           'LN_LTB_CamET_Set':     ['LN_LTB_CamET_PV_Set.txt',      "linac and LTB camera gain setpoint"],
#           'LN_LTB_CamTrig_Set':   ['LN_LTB_CamTrig_PV_Set.txt',    "linac and LTB camera trigger setpoint"],
#           'LTB_MG_Set':           ['LTB_MG_PV_Set.txt',            "LTB magnet setpoint"],
#           'LTB_CamFilt_Set':      ['LTB_CamFilt_PV_Set.txt',       "LTB camera filter setpoint"],
#           'LTB_ES_Set':           ['LTB_ES_PV_Set.txt',            "LTB energy slit motor setpoint"],
#           'LN_Dev_OnOff_Set':     ['LN_DeV_OnOff_PV_Set.txt',      "linac device on-off setpoint"],
#           'LTB_Dev_OnOff_Set':    ['LTB_DeV_OnOff_PV_Set.txt',     "LTB device on-off setpoint"]
#           'VA_SR_MAG_SET':       ['virtsr.masar.mg.sp.txt', "virtual storage ring magnet set point"]
#           'LN_RF_set_20120402':       ['LN/Set_PV/LN_RF_PV_set_20120402.txt', "linac RF amplitude, phase, new pvs added"]
#           # LN_PhaseI_SC_All
#           'LN_FC_read':      ['LN/Read_PV/LN_FC_PV_read.txt', "Linac faraday cup bunch number, aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
#           'LN_Flag_read':    ['LN/Read_PV/LN_Flag_read.txt',  "linac flag's image, x/y  min. start position, x/y range,  centriods and rms sizes"],
#           'LN_WCM_read':     ['LN/Read_PV/LN_WCM_PV_read.txt', "linac WCM waveform readback"],
#           'LN_BPM_read':     ['LN/Read_PV/LN_BPM_PV_read.txt', "Linac measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
#           'LN_Timing_RF_Gun_Read':	['LN/Read_PV/LN_Timing_RF_Gun_Read.txt', "LN timing for PBU/SPB/LLRF 1,2,3/MOD 1,2,3/RF Det./PPT TDU/eGun SBM delay, width, divider,  timing mode readback"],
#           # LN_PhaseI_SCR_All
#           'LN_Gun_Set':      ['LN/Set_PV/LN_Gun_PV_set.txt', "linac gun operation Mode, grid voltage, MBM Voltage,  pulse voltage,"],
#           'LN_Cor_set':      ['LN/Set_PV/LN_Cor_PV_set.txt', "linac corrector x and y plane current setpoint"],
#           'LN_Sol_set':      ['LN/Set_PV/LN_Sol_PV_set.txt', "linac solenoid current setpoint"],
#           'LN_RF_set':       ['LN/Set_PV/LN_RF_PV_set.txt', "linac RF amplitude, phase"],
#           'LN_BPM_set':      ['LN/Set_PV/LN_BPM_PV_set.txt', "linac BPM golden traj x and y setpoint"],
#           'LN_aperture_set': ['LN/Set_PV/LN_aperture_PV_set.txt', "linac aperture position setpoint"],
#           'LN_WCM_Set':      ['LN/Set_PV/LN_WCM_PV_set.txt', "linac WCM zero offset, range, sample length setpoint"],
#           'LN_Quad_set':     ['LN/Set_PV/LN_Quad_PV_set.txt', "linac Quads current setpoint"],
#           'LN_FC_set':       ['LN/Set_PV/LN_FC_PV_set.txt', "linac faraday cup zero offset, range, sample length setpoint"],
#           'LN_Timing_RF_Gun_set':	['LN/Set_PV/LN_Timing_RF_Gun_set.txt', "LN timing for PBU/SPB/LLRF 1,2,3/MOD 1,2,3/RF Det./PPT TDU/eGun SBM delay, width, divider, ref. event, timing mode"],
#           # LTD1_PhaseI_SC_All
#           'LTD1_BPM_read':   ['LTD1/Read_PV/LTD1_BPM_PV_read.txt', "Linac to dump1 beam line measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
#           'LTD1_Flag_read':  ['LTD1/Read_PV/LTD1_Flag_PV_read.txt',"Linac to dump1 beam line flag's image, x/y  min. start position, centriods and rms sizes"],
#           'LTD1_ICT_read':   ['LTD1/Read_PV/LTD1_ICT_PV_read.txt', "Linac to dump1 beam line ICT aver. Charge, std. Charge Error and Interest shot number readback"],
#           'LTD1_FC_read':    ['LTD1/Read_PV/LTD1_FC_PV_read.txt',  "Linac to dump1 beam line faraday cup aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
#           'LTB_Dump12_Timing_Read': ['LTD1/Read_PV/LTB_Dump12_Timing_Read.txt', "LTB dump12 timing for Flag, FC, FCT, ICT-output, BCM-output, BCM1-Trig and BCM2-Trig's delay, width, divider, ref. event"],
#           #LTD1_PhaseI_SCR_All
#           'LTD1_BPM_set':    ['LTD1/Set_PV/LTD1_BPM_PV_set.txt',  "Linac to dump1 beam line BPM golden traj x and y setpoint"],
#           'LTD1_Flag_set':   ['LTD1/Set_PV/LTD1_Flag_PV_set.txt', "Linac to dump1 beam line flag position and filter wheel position setpoint"],
#           'LTD1_Cor_set':    ['LTD1/Set_PV/LTD1_Cor_PV_set.txt',  "Linac to dump1 beam line corrector x and y plane current setpoint"],
#           'LTD1_Quad_set':   ['LTD1/Set_PV/LTD1_Quad_PV_set.txt', "Linac to dump1 beam line Quads current setpoint"],
#           'LTD1_ICT_set':    ['LTD1/Set_PV/LTD1_ICT_PV_set.txt',  "Linac to dump1 beam line ICT gain, BCM output's and signal's zerooffset, range, sample length setpoint"],
#           'LTD1_Bend_set':   ['LTD1/Set_PV/LTD1_Bend_PV_set.txt', "Linac to dump1 beam line dipole magnet setpoint"],
#           'LTD1_FC_set':     ['LTD1/Set_PV/LTD1_FC_PV_set.txt',   "Linac to dump1 beam line faraday cup zerooffset, range, sample length setpoint"],
#           'LTB_Dump12_Timing_set': ['LTD1/Set_PV/LTB_Dump12_Timing_set.txt', "LTB dump12 timing for Flag, FC, FCT, ICT-output, BCM-output, BCM1-Trig and BCM2-Trig's delay, width, divider, ref. event"],
#           #LTD2_PhaseI_SC_All
#           'LTD2_BPM_read':   ['LTD2/Read_PV/LTD2_BPM_PV_read.txt', "Linac to dump2 beam line measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
#           'LTD2_Flag_read':  ['LTD2/Read_PV/LTD2_Flag_PV_read.txt',"Linac to dump2 beam line flag's image, x/y min. start position,  centriods and rms sizes"],
#           'LTD2_ES_read':    ['LTD2/Read_PV/LTD2_ES_PV_read.txt',  "Linac to dump2 beam line flag's image, x plane min. start position, centriods and rms sizes"],
#           'LTD2_FCT_read':   ['LTD2/Read_PV/LTD2_FCT_PV_read.txt', "Linac to dump2 beam line FCT waveform readback"],
#           'LTD2_ICT_read':   ['LTD2/Read_PV/LTD2_ICT_PV_read.txt', "Linac to dump2 beam line ICT aver. Charge, std. Charge Error and Interest shot number readback"],
#           'LTD2_FC_read':    ['LTD2/Read_PV/LTD2_FC_PV_read.txt',  "Linac to dump2 beam line faraday cup aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
#           #LTD2_PhaseI_SCR_All
#           'LTD2_BPM_set':    ['LTD2/Set_PV/LTD2_BPM_PV_set.txt',  "Linac to dump2 beam line BPM golden traj x and y setpoint"],
#           'LTD2_Flag_set':   ['LTD2/Set_PV/LTD2_Flag_PV_set.txt', "Linac to dump2 beam line flag position and filter wheel position setpoint"],
#           'LTD2_Cor_set':    ['LTD2/Set_PV/LTD2_Cor_PV_set.txt',  "Linac to dump2 beam line corrector x and y plane current setpoint"],
#           'LTD2_Quad_set':   ['LTD2/Set_PV/LTD2_Quad_PV_set.txt', "Linac to dump2 beam line Quads current setpoint"],
#           'LTD2_Bend_set':   ['LTD2/Set_PV/LTD2_Bend_PV_set.txt', "Linac to dump2 beam line dipole magnet setpoint"],
#           'LTD2_ES_set':     ['LTD2/Set_PV/LTD2_ES_PV_set.txt',   "Linac to dump2 beam line energy slit blade position setpoint"],
#           'LTD2_FCT_set':    ['LTD2/Set_PV/LTD2_FCT_PV_set.txt',  "Linac to dump2 beam line  FCT zerooffset, range, sample length setpoint"],
#           'LTD2_ICT_set':    ['LTD2/Set_PV/LTD2_ICT_PV_set.txt',  "Linac to dump2 beam line ICT gain, BCM output's and signal's zerooffset, range, sample length setpoint"],
#           'LTD2_FC_set':     ['LTD2/Set_PV/LTD2_FC_PV_set.txt',   "Linac to dump2 beam line faraday cup zerooffset, range, sample length setpoint"]
}

# config name: [config desc, system]
configs= {
          'SR_All_SCR_w_ID_20141015': ['SR daily SCR setpoint w/ ID readback, w/o IS kick and septum: SR and RF', 'SR'],
          # 'SR_Quad_Sext_DCCT_Cal_20140917':     ["Storage Ring Quad and Sext power supplies PSI DCCT calibration", "PowerSupply"],
          # 'SR_Quad_Sext_DAC_Cal_20140917':      ["Storage Ring Quad and Sext power supplies PSI DAC calibration", "PowerSupply"],
          # 'SR_Quad_Sext_PSV_Cal_20140917':      ["Storage Ring Quad and Sext power supplies PSI PS Voltage calibration","PowerSupply"],
          # 'SR_Quad_Sext_GNDI_Cal_20140917':     ["Storage Ring Quad and Sext power supplies PSI Ground Current calibration","PowerSupply"],
          # 'SR_Quad_Sext_RampRate_Val_20140917': ["Storage Ring Quad and Sext power supplies PS Ramp Rate value","PowerSupply"],
          # add ID BPMs
          #'SR_Diag_BPM_Atten_20140626':   ['RF Attenuator Setting', 'BPM'],
          #'SR_Diag_BPM_Offsets_20140626': ['BBA, User and Reference Offset Settings', 'BPM'],
          #'SR_Diag_BPM_Timing_20140626':  ['Timing and Event Code Settings', 'BPM'],
          #'SR_Diag_BPM_Control_20140626': ['Control and Readout related PVs', 'BPM'],

          #'SR_Diag_BPM_Atten_20140423':   ['RF Attenuator Setting', 'BPM'],
          #'SR_Diag_BPM_Offsets_20140423': ['BBA, User and Reference Offset Settings', 'BPM'],
          #'SR_Diag_BPM_SDI_20140423':     ['Fast Orbit Feedback Settings', 'BPM'],
          #'SR_Diag_BPM_Timing_20140423':  ['Timing and Event Code Settings', 'BPM'],
          #'SR_Diag_BPM_Control_20140423': ['Control and Readout related PVs', 'BPM'],
#          'SR_All_SCR_20140421': ['SR daily SCR setpoint without IS kick and septum: SR and RF', 'SR'],
#          'LTB_BR_BTS_20140421': ['BR SCR PVs with IS kick and septum: LTB, BT, BTS, SR IS', 'LTB, BR, BTS'],
#          'SR_Diag_BPM_Atten_20140422': ['RF Attenuator Setting', 'BPM'],
#          'SR_Diag_BPM_Offsets_20140422': ['BBA, User and Reference Offset Settings', 'BPM'],
#          'SR_Diag_BPM_SDI_20140422':  ['Fast Orbit Feedback Settings', 'BPM'],
#          'SR_Diag_BPM_Timing_20140422':  ['Timing and Event Code Settings', 'BPM'],
#          'SR_Diag_BPM_Control_20140422': ['Control and Readout related PVs', 'BPM'],
          #'LTB_BR_BTS_20140328': ['LTB BR and BTS SCR', 'LTB, BR, BTS'],
          #'SR-All-20140326': ['SR daily SCR setpoint: SR and IS PS, RF', 'SR'], 
          #'LTB_BR_BTS_BINP2Masar_20140307': ['LTB BR and BTS converted from BINP Apps', 'LTB, BR, BTS'],
          #'SR-All-20140304': ['SR daily SCR setpoint: SR and IS PS, RF', 'SR'], 
           # 'Inj_Diag_BI_Control_20140228':  ['Expert pvs for injector non-bpm controls', 'BPM'],
           # 'Inj_Diag_BPM_Control_20140228': ['Expert pvs for injector bpm controls', 'BPM'],
           # 'Inj_Diag_BPM_Timing_20140228':  ['Expert pvs for injector bpm timing', 'BPM'],
           # 'SR_Diag_BPM_Control_20140228':  ['Expert pvs for storage ring bpms controls', 'BPM'],
           # 'SR_Diag_BPM_Timing_20140228':   ['Expert pvs for storage ring bpm timing', 'BPM']
           #'LN-LTB-All-20131219': ['Linac and LTB daily SCR setpoint', 'Linac, LTB'],
           # Linac, LTB BPM expert 20131213
           #'Diag-LN_LTB-allBPM-12.13.2013.expert': ['Expert control pvs for Linac and LTB bpms', 'BPM'],
           # BR BPM Expert 20131213
           #'Diag-BR-allBPM-12.13.2013.expert':     ['Expert control pvs for Booster Ring bpms', 'BPM'],
          #'Diag-BR-allBPM-Expert': ['Booster BPM pv list, including machine type, trigger source and delay setting, wfm type, mode setting, and BPM calibrations, etc..', 'BPM'],
          #'LN-LTB-All-20131209': ['Linac and LTB daily SCR setpoint', 'Linac, LTB'],

          #'LTB_PS_SRC_20131206': ['LTB power supply setpoints, for saving/comparing/restoring', 'LTB'],
          #'BR_RF_SC_20130426': ['BR RF daily save', 'BR']
          # 'BR_MG_SCR_20130419': ['BR ramping PS daily SCR setpoint', 'BR']
#          'example config for DLS meeting': ['demo config for 20120711 DLS meeting', 'test']
#          'LN_LTB_BPM_Expert_20120621':  ['Expert control pvs for Linac and LTB bpms', 'BPM']
#          'LN-LTB-PhaseI-All_20120511': ['Linac and LTB daily SCR setpoint', 'Linac, LTB']
#          'LN-LTB-PhaseI-SBM-All_20120426': ['Linac and LTB daily SCR setpoint', 'Linac, LTB']
#          'VA_SR_MAG_SET':   ['virtual storage magnet setpoint on Apr 05, 2012','virtac']
#          'LN_PhaseI_SCR_All_20120402':   ['Linac daily SCR setpoint on Apr 02, 2012','Linac']
#          'LN_PhaseI_SC_All':    ['Linac daily reference',   'Linac'],
#          'LN_PhaseI_SCR_All':   ['Linac daily SCR setpoint','Linac'],
#          'LTD1_PhaseI_SC_All':  ['LTD1 daily reference',    'LTD1'],
#          'LTD1_PhaseI_SCR_All': ['LTD1 daily SCR setpoint', 'LTD1'], 
#          'LTD2_PhaseI_SC_All':  ['LTD2 daily reference',    'LTD2'],
#          'LTD2_PhaseI_SCR_All': ['LTD2 daily SCR setpoint', 'LTD2']
}

# config name: [pvgroup,]
pvg2config= {
           'SR_All_SCR_w_ID_20141015' : ['SR_ID_RB_20141015', 'SR_All_SCR_20140421'],
           #'SR_Quad_Sext_DCCT_Cal_20140917':     ["SR_Quad_Sext_DCCT_Cal_20140917"],
           #'SR_Quad_Sext_DAC_Cal_20140917':      ["SR_Quad_Sext_DAC_Cal_20140917"],
           #'SR_Quad_Sext_PSV_Cal_20140917':      ["SR_Quad_Sext_PSV_Cal_20140917"],
           #'SR_Quad_Sext_GNDI_Cal_20140917':     ["SR_Quad_Sext_GNDI_Cal_20140917"],
           #'SR_Quad_Sext_RampRate_Val_20140917': ["SR_Quad_Sext_RampRate_Val_20140917"],

          # add ID BPMs
          #'SR_Diag_BPM_Atten_20140626':   ['SR_Diag_BPM_Atten_20140626'],
          #'SR_Diag_BPM_Offsets_20140626': ['SR_Diag_BPM_Offsets_20140626'],
          #'SR_Diag_BPM_Timing_20140626':  ['SR_Diag_BPM_Timing_20140626'],
          #'SR_Diag_BPM_Control_20140626': ['SR_Diag_BPM_Control_20140626'],

          #'SR_Diag_BPM_Atten_20140423':   ['SR_Diag_BPM_Atten_20140423'],
          #'SR_Diag_BPM_Offsets_20140423': ['SR_Diag_BPM_Offsets_20140423'],
          #'SR_Diag_BPM_SDI_20140423':     ['SR_Diag_BPM_SDI_20140423'],
          #'SR_Diag_BPM_Timing_20140423':  ['SR_Diag_BPM_Timing_20140423'],
          #'SR_Diag_BPM_Control_20140423': ['SR_Diag_BPM_Control_20140423'],

#         'SR_All_SCR_20140421':           ['SR_All_SCR_20140421'],
#          'LTB_BR_BTS_20140421':          ['LTB_BR_BTS_20140421'],
#          'SR_Diag_BPM_Atten_20140422':   ['SR_Diag_BPM_Atten_20140422'],
#          'SR_Diag_BPM_Offsets_20140422': ['SR_Diag_BPM_Offsets_20140422'],
#          'SR_Diag_BPM_SDI_20140422':     ['SR_Diag_BPM_SDI_20140422'],
#          'SR_Diag_BPM_Timing_20140422':  ['SR_Diag_BPM_Timing_20140422'],
#          'SR_Diag_BPM_Control_20140422': ['SR_Diag_BPM_Control_20140422'],
    #'LTB_BR_BTS_20140328': ['LTB_BR_BTS_20140328'],
    #'SR-All-20140326': ['SR_All_SCR_20140326'],
    #'LTB_BR_BTS_BINP2Masar_20140307': ['LTB_BR_BTS_20140307'],
    #'SR-All-20140304': ['SR_All_SCR_20140304'],

    #'Inj_Diag_BI_Control_20140228':  ['Inj_Diag_BI_Control_20140228'],
    #'Inj_Diag_BPM_Control_20140228': ['Inj_Diag_BPM_Control_20140228'],
    #'Inj_Diag_BPM_Timing_20140228':  ['Inj_Diag_BPM_Timing_20140228'],
    #'SR_Diag_BPM_Control_20140228':  ['SR_Diag_BPM_Control_20140228'],
    #'SR_Diag_BPM_Timing_20140228':   ['SR_Diag_BPM_Timing_20140228'],
    #'LN-LTB-All-20131219': ['LN_Sol_Set_20131209',
    #                        'LN_Cor_Set_20131209',
    #                        'LN_Quad_Set_20131209',
    #                        'LN_Gun_Set_20131219',
    #                        'LN_LLRF_Set_20131209',
    #                        'LN_HLRF_Set_20131209',
    #                        'LTB_MG_Set_20131209'],
           #'Diag-LN_LTB-allBPM-12.13.2013.expert': ['LN_LTB_BPM_20131213'],
           #'Diag-BR-allBPM-12.13.2013.expert': ['BR_BPM_20131213'],
    #'Diag-BR-allBPM-Expert': ['BR_BPM_20131212'],
    #'LN-LTB-All-20131209': ['LN_Sol_Set_20131209',
    #                        'LN_Cor_Set_20131209',
    #                        'LN_Quad_Set_20131209',
    #                        'LN_Gun_Set_20131209',
    #                        'LN_LLRF_Set_20131209',
    #                        'LN_HLRF_Set_20131209',
    #                        'LTB_MG_Set_20131209'],

#             'LTB_PS_SRC_20131206': ['LTB_PS_PS_20131206'],
              #'BR_RF_SC_20130426':['BR_RF_Set_20130426']
#             'BR_MG_SCR_20130419': ['BR_MG_Set_20130419']
#             'example config for DLS meeting': ['test example']
#             'LN_LTB_BPM_Expert_20120621': ['LN_LTB_BPM_20120621']
#             'LN-LTB-PhaseI-All_20120511': ['LN_Sol_Set_20120511',
#                                            'LN_Cor_Set_20120511',
#                                            'LN_Quad_Set_20120511',
#                                            'LN_Gun_Set_20120511',
#                                            'LN_LLRF_Set_20120511',
#                                            'LN_HLRF_Set_20120511',
#                                            'LN_LTB_Diag_Time_Set_20120511',
#                                            'LN_LTB_Dig_Time_Set_20120511',
#                                            'LN_LTB_CamGN_Set_20120511',
#                                            'LN_LTB_CamET_Set_20120511',
#                                            'LN_LTB_CamTrig_Set_20120511',
#                                            'LTB_MG_Set_20120511',
#                                            'LTB_CamFilt_Set_20120511',
#                                            'LTB_ES_Set_20120511',
#                                            'LN_Time_PV_Set_20120511'
#                                            ]
#             'LN-LTB-PhaseI-SBM-All_20120426': ['LN_Sol_Set','LN_Cor_Set','LN_Quad_Set','LN_Gun_SBM_Set','LN_LLRF_SBM_Set','LN_HLRF_SBM_Set',
#                                                'LN_LTB_Diag_Time_Set','LN_LTB_Dig_Time_Set','LN_LTB_CamGN_Set','LN_LTB_CamET_Set','LN_LTB_CamTrig_Set',
#                                                'LTB_MG_Set','LTB_CamFilt_Set','LTB_ES_Set','LN_Dev_OnOff_Set','LTB_Dev_OnOff_Set']
#             'VA_SR_MAG_SET':    ['VA_SR_MAG_SET']
#             'LN_PhaseI_SCR_All_20120402': ['LN_Gun_Set', 'LN_Cor_set', 'LN_Sol_set', 'LN_RF_set_20120402', 'LN_BPM_set', 'LN_aperture_set', 'LN_WCM_Set', 'LN_Quad_set', 'LN_FC_set', 'LN_Timing_RF_Gun_set'],
#             'LN_PhaseI_SC_All':     ['LN_FC_read', 'LN_Flag_read', 'LN_WCM_read', 'LN_BPM_read', 'LN_Timing_RF_Gun_Read'],
#             'LN_PhaseI_SCR_All':    ['LN_Gun_Set', 'LN_Cor_set', 'LN_Sol_set', 'LN_RF_set', 'LN_BPM_set', 'LN_aperture_set', 'LN_WCM_Set', 'LN_Quad_set', 'LN_FC_set', 'LN_Timing_RF_Gun_set'],
#             'LTD1_PhaseI_SC_All':   ['LTD1_BPM_read', 'LTD1_Flag_read', 'LTD1_ICT_read', 'LTD1_FC_read', 'LTB_Dump12_Timing_Read'],
#             'LTD1_PhaseI_SCR_All':  ['LTD1_BPM_set', 'LTD1_Flag_set', 'LTD1_Cor_set', 'LTD1_Quad_set', 'LTD1_ICT_set', 'LTD1_Bend_set', 'LTD1_FC_set', 'LTB_Dump12_Timing_set'],
#             'LTD2_PhaseI_SC_All':   ['LTD2_BPM_read', 'LTD2_Flag_read', 'LTD2_ES_read', 'LTD2_FCT_read', 'LTD2_ICT_read', 'LTD2_FC_read'],
#             'LTD2_PhaseI_SCR_All':  ['LTD2_BPM_set', 'LTD2_Flag_set', 'LTD2_Cor_set', 'LTD2_Quad_set', 'LTD2_Bend_set', 'LTD2_ES_set', 'LTD2_FCT_set', 'LTD2_ICT_set', 'LTD2_FC_set']
}
