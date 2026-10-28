import matplotlib.pyplot as plt
import numpy as np

Temp = np.array([290.196,300.187,310.193,315.195,320.190])
Res = np.array([164.569,156.494,149.117,145.681,142.390])

slope, intercept = np.polyfit(Temp,Res,1)

predicted = Temp * slope + intercept

print("Approximation from 290K to 320K")
print(f"y={slope}x+{intercept}")

plt.figure()
plt.scatter(Temp,Res, color = "red")
plt.plot(Temp, predicted)
plt.show()