from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 11})
import vMCS_thermoSim as TS

T_air = 24.3 #dgree C

Gain=20
T_0 = 3068

# New Data

#path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\2026Data\Data\100_100_400_ss_AlRod_10cm_900gSinks_1V_roughvacuum_April 28, 2026 10-10 AM.csv"
#path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\2026Data\Data\100_0.5_300_ss_AlRod_10cm_900gSinks_1V_roughvacuum_May 06, 2026  3-00 PM, 24.5C.csv"
path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\2026Data\Data\100_10_400_ss_AlRod_10cm_900gSinks_1V_roughvacuum_May 05, 2026 10-55 AM, 24.3C.csv"

with open(path, 'r', encoding='utf-8-sig') as f:
    rawData = np.loadtxt(f,delimiter=",", dtype=float)


#rawData = np.loadtxt(path,delimiter=",", dtype=float)
path = path.split('\\')[-1].split("_")
lagTime = float(path[0])
heatPulse = float(path[1])
dataTime = float(path[2])
att = heatPulse


tempData = TS.tempConvert(rawData[:,4],rawData[:,2],att,T_air,T_0,1,Gain,lagTime)
tempData = TS.flatset(tempData,lagTime,dataTime)

# Old Data

#second_path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\PastData\100_100_300_ss_NewThermo_900gSinks_1Volt_16.9C_May 25, 2024  5-45 PM.csv"
#second_path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\PastData\100_0.5_300_ss_tempDriftCal_September 16, 2023  1-37 AM.csv"
second_path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\PastData\100_10_300_ss_NewThermo_900gSinks_1Volt_16.9C_May 25, 2024 12-15 PM (2).csv"

with open(second_path, 'r', encoding='utf-8-sig') as f:
    rawData2 = np.loadtxt(f,delimiter=",", dtype=float)


#rawData = np.loadtxt(path,delimiter=",", dtype=float)
second_path = second_path.split('\\')[-1].split("_")
lagTime2 = float(second_path[0])
heatPulse2 = float(second_path[1])
dataTime2 = float(second_path[2])
att2 = heatPulse2

tempData2 = TS.tempConvert(rawData2[:,4],rawData2[:,2],att2,T_air,T_0,1,Gain,lagTime2)
tempData2 = TS.flatset(tempData2,lagTime2,dataTime2)

# Plotting

plt.figure(figsize=(11, 7))

plt.plot(np.arange(0,lagTime+dataTime,0.01),tempData*1.4,label="Aluminum 10cm rod")
plt.plot(np.arange(0,lagTime2+dataTime2,0.01),tempData2,label="Copper 20cm rod",zorder=0)

plt.title("Comparing 20cm Cu rod to 10cm Al 10s pulse")
plt.legend(loc='upper right')
plt.xlabel("Time (s)")
plt.ylabel("ΔTemperature (°K)")
plt.grid()
plt.xlim(100, 400)
plt.show()