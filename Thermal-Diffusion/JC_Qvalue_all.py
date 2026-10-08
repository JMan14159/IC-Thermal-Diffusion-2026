import vMCS_thermoSim as TS
import os
import numpy as np

old_data = []
new_data = []

path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\PastData"
path2 = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\2026Data\Data"

def calculateQ(rawData_,dt_,att_,lagtime,Req):
    lag =int(lagtime/0.01)
    V = rawData_[lag:round(100*att_+lag),7] - rawData_[lag:round(100*att_+lag),1]
    Q = 0
    #Req = 6.82   # Yash Mohod 2023 1/8" diameter rod   
    #Req = 9.848   # 2026 1/4" diameter rod
    #Req = 14.488 # 2026 3/8" diameter rod
    #Req = 6.75  # 2026 aluminum rod 5.02

    for i in range(len(V)):
        Q += (V[i]**2 /Req ) *dt_
        #5.3
        # Q += (V[i]**2 /5.3) *dt_
        # Q += (V[i]**2 * Rh/Rtot**2) * dt_
        
    return Q

def qval_each_data_in_folder(path, data_path,Req):

    for e in os.scandir(path):
        if e.is_file():
            with open(e.path, 'r', encoding='utf-8-sig') as f:
                rawData = np.loadtxt(f,delimiter=",", dtype=float)

            newpath = e.path.split('\\')[-1].split("_")
            lagTime = float(newpath[0])
            heatPulse = float(newpath[1])
            dataTime = float(newpath[2])
            att = heatPulse
            #print("lagTime: ",lagTime,'s')
            #print("heatPulse: ",heatPulse,'s')
            #print("dataTime: ",dataTime,'s')
            Q = calculateQ(rawData,0.01,att,lagTime,Req)
            #print("Heat Pulse: ",Q,'J')
            data = [lagTime,heatPulse,dataTime,Q]
        data_path.append(data)

qval_each_data_in_folder(path, old_data, 6.82)
qval_each_data_in_folder(path2, new_data,6.75)

print(old_data)
print("--------------------------------------------")
print(new_data)

for i in range(len(old_data)):
    print(old_data[i][3])

print("--------------------------------------------")
for i in range(len(new_data)):
    print(new_data[i][3])