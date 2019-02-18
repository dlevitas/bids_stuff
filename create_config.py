#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 16:21:06 2019

@author: dlevitas


Attempt to read dicom files to create a config file(s) needed for bids conversion
"""

import os, glob, json
from sys import argv
import numpy as np


dicom_dir='/Users/dlevitas/Desktop/create_config'
config_file_dir='/Users/dlevitas/Desktop'
bold_vols=870
task='std'


#dicom_dir=str(argv[1])
#config_file_dir=str(argv[2])
#bold_vols=argv[3]
#task=str(argv[4])

#Begin
try:
    import pydicom
except ImportError:
    os.system('pip install -U pydicom')
    import pydicom

#Find unique protocol dicoms
descriptions = []
sequences = []
data_types = []
modality_labels = []
custom_labels = []
sidecars = []
sidecar_num = 0

for i in np.unique([x.split("_")[1].split("_")[0] for x in os.listdir(dicom_dir)]):
    dicom = pydicom.dcmread(glob.glob(dicom_dir + '/*_%s_*.dcm' %i)[0])
    descriptions.append(str(dicom.SeriesDescription))
    sequences.append(str(dicom.SequenceName))
    

#Check for duplicates 
check = {i:descriptions.count(i) for i in descriptions}

iter = 0
for j in descriptions:
    
    if 'localizer' in j:
        sidecar_num+=check[j]
        
    elif 'T1w' in j and check[j] > 1:
        if iter == 0:
            sidecar_num+=check[j]
            sidecars.append(sidecar_num)
            data_types.append("anat")
            modality_labels.append("T1w")
            custom_labels.append('')
            iter+=1
        else:
            pass
                
    elif 'T1w' in j and check[j] == 1:
        sidecar_num+=check[j]
        sidecars.append(sidecar_num)
        data_types.append("anat")
        modality_labels.append("T1w")
        custom_labels.append('')
        
    elif 'T2w' in j and check[j] > 1:
        sidecar_num+=check[j]
        sidecars.append(sidecar_num)
        data_types.append("anat")
        modality_labels.append("T2w")
        custom_labels.append('')
        
    elif 'T2w' in j and check[j] == 1:
        sidecar_num+=check[j]
        sidecars.append(sidecar_num)
        data_types.append("anat")
        modality_labels.append("T2w")
        custom_labels.append('')
    
    elif 'FieldMap_AP' in j:
        sidecar_num+=check[j]
        sidecars.append(sidecar_num)
        data_types.append("fmap")
        modality_labels.append("epi")
        custom_labels.append('')
        
    elif 'FieldMap_PA' in j:
        sidecar_num+=check[j]
        sidecars.append(sidecar_num)
        data_types.append("fmap")
        modality_labels.append("epi")
        custom_labels.append('')
        
    elif 'bold' in j:
        nruns=check[j]
        print nruns
        if len(glob.glob(dicom_dir + '/*_*%s_*.dcm' %(sidecar_num+1))) != bold_vols:
            sidecar_num+=1
        else:
            sidecar_num+=1
            sidecars.append(sidecar_num)
            data_types.append("func")
            modality_labels.append("bold")
            custom_labels.append("task-%s" %task)
            
    else:
        sidecar_num+=1
        
        
for k in range(len(sidecars)):
    if sidecars[k] > 9:
        sidecars[k] = '0' + str(sidecars[k]) + '*'
    else:
        sidecars[k] = '00' + str(sidecars[k]) + '*'
    

dic = {"descriptions": []}
for i in range(len(data_types)):
    if data_types[i] == "func":
        dic['descriptions'].append({"dataType": data_types[i], 
                           "modalityLabel": modality_labels[i], 
                           "customLabels": custom_labels[i], 
                           "criteria":{"SidecarFilename": sidecars[i]}})
    else:
        dic['descriptions'].append({"dataType": data_types[i], 
           "modalityLabel": modality_labels[i], 
           "criteria":{"SidecarFilename": sidecars[i]}})
        
   
#Copy dictionary to .json file
with open('%s/config_%s.json' %(config_file_dir,task), 'w') as fp:
    json.dump(dic, fp, indent=2)