#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 16:21:06 2019

@author: dlevitas


This script organizes dicoms to create a config file(s) needed for dicom conversion
Dicom conversion will adhere to the BIDS format (using dcm2bids and dcm2niix)
"""

import os, glob, json
from sys import argv
import numpy as np

subj=str(argv[1])
dicom_dir=str(argv[2])
config_file_dir=str(argv[3])
task=str(argv[4])


#Begin
try:
    import pydicom
except ImportError:
    os.system('pip install -U pydicom --user')
    import pydicom

#Find unique protocol dicoms
descriptions = []
sequences = []
data_types = []
modality_labels = []
custom_labels = []
series = []

for i in np.unique([x.split("_")[1].split("_")[0] for x in os.listdir(dicom_dir + '/sub-{}'.format(subj)) if '.dcm' in x]):
    dicom = pydicom.dcmread(glob.glob(dicom_dir + '/sub-{}/*_{}_*.dcm'.format(subj,i))[0])
    descriptions.append(str(dicom.SeriesDescription))
    sequences.append(str(dicom.SequenceName))
    series.append(int(dicom.SeriesNumber))
    

#Check for duplicates 
protocol = {i:descriptions.count(i) for i in descriptions}

#Set up the configuration file for dcm2bids
T1w_dup = [1]
T2w_dup = [1]
se_ap_dup = [1]
se_pa_dup = [1]
bold_count = 1
sbref_count = 1
for j in range(len(descriptions)):
    
    if 'localizer' in descriptions[j]:
        series[j] = -1
        
    elif 'T1w' in descriptions[j]:
        if len(T1w_dup) < protocol[descriptions[j]]:
            T1w_dup.append(1)
            series[j] = -1
        else:
            data_types.append("anat")
            modality_labels.append("T1w")
            custom_labels.append('')
        
    elif 'T2w' in descriptions[j]:
        if len(T2w_dup) < protocol[descriptions[j]]:
            T2w_dup.append(1)
            series[j] = -1
        else:
            data_types.append("anat")
            modality_labels.append("T2w")
            custom_labels.append('')
       
    elif 'fmap' in descriptions[j]:
        if 'AP' in descriptions[j]:
            if len(se_ap_dup) < protocol[descriptions[j]]:
                se_ap_dup.append(1)
                series[j] = -1
            else:
                data_types.append("fmap")
                modality_labels.append("epi")
                custom_labels.append('')
        elif 'PA' in descriptions[j]:
            if len(se_pa_dup) < protocol[descriptions[j]]:
                se_pa_dup.append(1)
                series[j] = -1
            else:
                data_types.append("fmap")
                modality_labels.append("epi")
                custom_labels.append('')
                
    elif any(x in descriptions[j] for x in ['SBRef']):
        sbref_count+=1
        data_types.append("func")
        modality_labels.append("bold")
        custom_labels.append("task-{}_sbref".format(task))
            
    elif any(x in descriptions[j] for x in ['bold_task','bold_rest', 'bold']):
        if any(x in descriptions[j] for x in ['SBRef']):
            sbref_count+=1
            data_types.append("func")
            modality_labels.append("bold")
            custom_labels.append("task-{}_sbref".format(task))
        else:
            bold_count+=1
            data_types.append("func")
            modality_labels.append("bold")
            custom_labels.append("task-{}".format(task))
            
#    elif 'DWI' in descriptions[j]:
#        data_types.append("dwi")
#        modality_labels.append("dwi")
#        custom_labels.append('')
            
    else:
        pass
      

series = [x for x in series if x != -1]  
for k in range(len(series)):
    if series[k] > 9:
        series[k] = '0' + str(series[k]) + '*'
    else:
        series[k] = '00' + str(series[k]) + '*'
    
    
dic = {"descriptions": []}
for i in range(len(data_types)):
    if data_types[i] == "func":
        dic['descriptions'].append({"dataType": data_types[i], "modalityLabel": modality_labels[i], "customLabels": custom_labels[i], "criteria":{"SidecarFilename": series[i]}})
    else:
        dic['descriptions'].append({"dataType": data_types[i], "modalityLabel": modality_labels[i], "criteria":{"SidecarFilename": series[i]}})
        
        
#Copy dictionary to .json file
with open('{}/config_{}_{}.json'.format(config_file_dir, subj, task), 'w') as fp:
    json.dump(dic, fp, indent=3)
