# #xtal th0
# xtal=111
# # -------------------
# # energy Calibration
# # for Fe-K, theo-exp
# th0= 12915906-13144313
# #xtal=311
# #th0= x -25737355
# # -------------------
# # abs data on I1_eh1
# transmcols=[0,2,29,30,4,5]
# #####
# # abs data on I0_eh2 (for sample P3Pt)
# #transmcols=[0,2,14,3,4,5]
# ##########
# #transmcols=[0,2,29,30,6,7]
# # transmcols=[0,2,18,19,6,7]
# fluocols=[0,2,3,4,5,16,17,18,19,20,21,22,23,24,25,26,27]



#xtal th0
xtal=111
# -------------------
# energy Calibration
# for Fe-K, theo-exp
th0= 12915906-13144313
#xtal=311
#th0= x -25737355
# -------------------
# Content ["energy/mono", "ebragg", "I0_EH1/2", "I1_EH1/2", "I1_EH2", "IR_EH2"]
transmcols=[0,2,29,30,4,5]
# Content ["Energy", "ebragg", "I0_EH2", "I1_EH2", "IR_EH2", 'fluo01', ... , 'fluo12']
fluocols=[0,2,5,6,7,16,17,18,19,20,21,22,23,24,25,26,27]
input_column_names = [
    'L_energy',
    'Epoch',
    'ebragg',
    'epitch',
    'srcur',
    'I0_eh2',
    'I1_eh2',
    'IX_eh2',
    'IR_eh2',
    'c8',
    'VPOS_enc',
    'HPOS2_enc',
    'RBENCH_enc',
    'EBENCH_enc',
    'ROT_enc',
    'HPOS1_enc',
    'fluo01',
    'fluo02',
    'fluo03',
    'fluo04',
    'fluo05',
    'fluo06',
    'fluo07',
    'fluo08',
    'fluo09',
    'fluo10',
    'fluo11',
    'fluo12',
    'fluo13',
    'I0_eh1',
    'I1_eh1',
    'IX_eh1',
    'c9',
    'volt1',
    'volt2',
    'sdd',
    'ebraggc',
    'Oxford503',
    'Seconds',
    'Seconds',
]
output_column_names = [
    '#eBraggEnergy',
    'I0_eh2',
    'I1_eh2',
    'fluo01',
    'fluo02',
    'fluo03',
    'fluo04',
    'fluo05',
    'fluo06',
    'fluo07',
    'fluo08',
    'fluo09',
    'fluo10',
    'fluo11',
    'fluo12',
    'fluo13',
]
if __name__ == '__main__':
    print(len(input_column_names))