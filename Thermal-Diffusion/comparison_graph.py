from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 11})
import vMCS_thermoSim as TS

T_air = 24.3 #dgree C

Gain=20
T_0 = 3068

# New Data

path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\2026Data\Data\100_100_400_ss_AlRod_10cm_900gSinks_1V_roughvacuum_April 28, 2026 10-10 AM.csv"
#path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\2026Data\Data\100_0.5_300_ss_AlRod_10cm_900gSinks_1V_roughvacuum_May 06, 2026  3-00 PM, 24.5C.csv"
#path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\2026Data\Data\100_10_400_ss_AlRod_10cm_900gSinks_1V_roughvacuum_May 05, 2026 10-55 AM, 24.3C.csv"

with open(path, 'r', encoding='utf-8-sig') as f:
    rawData = np.loadtxt(f,delimiter=",", dtype=float)


#rawData = np.loadtxt(path,delimiter=",", dtype=float)
path = path.split('\\')[-1].split("_")
lagTime = float(path[0])
heatPulse = float(path[1])
dataTime = float(path[2])
att = heatPulse


tempData = TS.tempConvert(rawData[:,3],rawData[:,2],att,T_air,T_0,1,Gain,lagTime)
tempData = TS.flatset(tempData,lagTime,dataTime)

# Old Data

second_path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\PastData\100_100_300_ss_NewThermo_900gSinks_1Volt_16.9C_May 25, 2024  5-45 PM.csv"
#second_path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\PastData\100_0.5_300_ss_tempDriftCal_September 16, 2023  1-37 AM.csv"
#second_path = r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\PastData\100_10_300_ss_NewThermo_900gSinks_1Volt_16.9C_May 25, 2024 12-15 PM (2).csv"


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

dx = 0.035

sim_data_al = np.loadtxt(
    r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\Simulated Data\Al_sim_data__400s_Q13.83980428240667.csv",
    delimiter=","
)

time_al = sim_data_al[:, 0]
temperature_al = sim_data_al[:, 1:]  # rows: time; columns: rod positions
x_al = np.arange(temperature_al.shape[1]) * dx
position_index_al = np.argmin(np.abs(x_al - 2))


sim_data_cu = np.loadtxt(
    r"C:\Users\joho1\Documents\Research with Matt\Data-and-Papers\Simulated Data\Cu_sim_data__400s_Q11.356561439132742.csv",
    delimiter=","
)

time_cu = sim_data_cu[:, 0]
temperature_cu = sim_data_cu[:, 1:]  # rows: time; columns: rod positions
x_cu = np.arange(temperature_cu.shape[1]) * dx
position_index_cu = np.argmin(np.abs(x_cu - 2))




    #Req = 6.82   # Yash Mohod 2023 1/8" diameter rod   
    #Req = 9.848   # 2026 1/4" diameter rod
    #Req = 14.488 # 2026 3/8" diameter rod
    #Req = 6.75  # 2026 aluminum rod 5.02
Q = TS.calculateQ(rawData,0.01,att,lagTime, 6.75)
heatlossBool = False

print("Heat Pulse: ",Q,'J')

Q_2 = TS.calculateQ(rawData2,0.01,att2,lagTime2, 6.82)
heatlossBool = False

print("Heat Pulse: ",Q_2,'J')


# Plotting

plt.figure(figsize=(11, 7))

plt.plot(lagTime+time_al, temperature_al[:, position_index_al],label="Simulated Aluminum 10cm rod")
plt.plot(lagTime+time_cu, temperature_cu[:, position_index_cu],label="Simulated Copper 20cm rod")


plt.plot(np.arange(0,lagTime+dataTime,0.01),tempData,label="Aluminum 10cm rod")
plt.plot(np.arange(0,lagTime2+dataTime2,0.01),tempData2,label="Copper 20cm rod",zorder=0)

plt.title("Comparing 20cm Cu rod to 10cm Al 100s pulse")
plt.legend(loc='upper right')
plt.xlabel("Time (s)")
plt.ylabel("ΔTemperature (°K)")
plt.grid()
plt.xlim(100, 400)
plt.show()