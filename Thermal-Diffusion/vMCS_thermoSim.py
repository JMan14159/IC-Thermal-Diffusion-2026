# Imports
from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt


# offset by using lag time
def flatset(tempData,lagTime,dataTime):
    fronttrim = 2
    endtrim = 2
    temp = np.poly1d( np.polyfit(np.arange(fronttrim,lagTime-endtrim,0.01), tempData[int(fronttrim/0.01):int((lagTime-endtrim)/0.01)], 1) )
    tempData  -= temp(np.arange(0,int(lagTime)+int(dataTime),0.01))
    return tempData


# temperature converter
def tempConvert(rawData_,V_0_,att_, T_air_,T_0_,scal_,gain_,lagTime):
    offSet = np.mean(rawData_[int((lagTime)*100):int((lagTime+0.05)*100)])
    # V_0_ = np.mean(V_0_[round((lagTime+att_)*0.01)*-1:])
    # V_0_ = np.mean(V_0_[-100:])
    V_0_ = np.mean(V_0_[:])
    G = gain_
    #c = (4/(G * T_0_ * V_0_)) * ((T_air_+273.15)**(2))
    c  = (4/(G * T_0_ * V_0_)) * ((T_air_+273.15)**(2)) / ( 1 - (4/(G* T_0_ * V_0_)) * (rawData_ -offSet) * (T_air_+273.15) )
    temp_ = scal_ * c * (rawData_ -offSet)
    return temp_



# sum up the total q
def calculateQ(rawData_,dt_,att_,lagtime):
    lag =int(lagtime/0.01)
    V = rawData_[lag:round(100*att_+lag),7] - rawData_[lag:round(100*att_+lag),1]
    Q = 0
    #Req = 6.82   # Yash Mohod 2023 1/8" diameter rod   
    #Req = 9.848   # 2026 1/4" diameter rod
    #Req = 14.488 # 2026 3/8" diameter rod
    Req = 5.02  # 2026 aluminum rod

    for i in range(len(V)):
        Q += (V[i]**2 /Req ) *dt_
        #5.3
        # Q += (V[i]**2 /5.3) *dt_
        # Q += (V[i]**2 * Rh/Rtot**2) * dt_
        
    return Q

# analytical method
def anaMet(Q_,A_,kappa_,s_,t,d_,h_,a_,heatlossBool_,lag,dt_):

    t_  = np.arange(0,t,dt_)
    temp2 = np.zeros(int((t+lag)/dt_))
    if heatlossBool_:
        temp = Q_ / (2 * A_ * np.sqrt(np.pi * kappa_ * s_ * t_)) * np.e**(-(d_**2) * s_ / (4 * kappa_ * t_)) * np.e**(((-2*h_ / a_)*t_) / s_)
        temp2[int(lag/dt_):] = temp[:]
        return temp2
    else:
        temp  =  Q_ / (2 * A_ * np.sqrt(np.pi * kappa_ * s_ * t_)) * np.e**(-(d_**2) * s_ / (4 * kappa_ * t_))
        temp2[int(lag/dt_):] = temp[:]
        return temp2 

def sink(sinkMat,rodSeg,lambda_al,j,lambda_):
    # open side
    os = sinkMat[-1,j-1] + (2*lambda_al)*(sinkMat[-2,j-1]  - sinkMat[-1,j-1]  ) 

    # mid
    ms = sinkMat[1:-1,j-1] + (lambda_al*(sinkMat[:-2,j-1] - 2*sinkMat[1:-1,j-1] + sinkMat[2:,j-1]))

    # touching
    ts = sinkMat[0,j-1] + (lambda_al*(rodSeg - 2*sinkMat[0,j-1] + sinkMat[1,j-1]))

    return ts,ms,os


"""
#MCS  1D code using scipy.integrate here
"""
def numMCS(t, y, beta_, gamma_, delta_, x_h_, t_pulse_, bcS_):
    
    if t>=t_pulse_:
        gamma_= 0
    
    # Defining the output vector of temperatures on the rod
    rhs_out = np.zeros(len(y)) # Size of the output vector
    
    # This bit gets all the parts inbetween the two end of the rod
    # This command has to go all the way to N because the last point of the range is not included
    # in the range!  So it looks like we are doing the last N value twice, but including
    # N in the range actually means it goes to N-1.
    rhs_out[1:-1] = beta_*(y[2:]-2*y[1:-1]+y[:-2])+ gamma_*x_h_[1:-1] - delta_*y[1:-1]
    
    #Left side of the rod boundary conditions
    if bcS_[0] ==0:
        # Here is a heat sunk at the left side of the rod.
        rhs_out[0] = 0
    if bcS_[0] ==1:
        # This is the near end of the rod, floating.
        rhs_out[0] = (2*beta_)*(y[1]-y[0]) - delta_*y[0]
    
    #Right side of the rod boundary conditions
    if bcS_[1] ==0:
        # Here is a heat sunk at the left side of the rod.
        rhs_out[-1] = 0
    if bcS_[1] ==1:
        # This is the near end of the rod, floating.
        rhs_out[-1] = (2*beta_)*(y[-2]-y[-1]) - delta_*y[-1]
        
        
    return rhs_out


"""
#MCS  2D code using solve_ivp here.  First, the definition of the differential equation in 2D.
"""

def numMCS_2D(t_, y, tau_, gamma_, delta_, delta2_, beta_, x_h_, t_pulse_, bcS_):
    
    if t_>=t_pulse_:
        gamma_= 0
    
    # Defining the output vector of temperatures on the rod
    rhs_out = np.zeros(shape=(len(y[:,1]),len(y[1,:]))) # Size of the output vector
    r_index = rhs_out # Defining a 2D array that has the index number of the radial direction
    r_index[:,] = np.linspace(0,len(y[1,:])-1, len(y[1,:]) ) # Making each row just the index values
    
    # The vectorized function for all the points along the rod except the borders
    rhs_out[1:-1, 1:-1] = tau_*( (1 + 1/(2*r_index[1:-1,1:-1]) )*y[1:-1, 2:] + (1 - 1/(2*r_index[1:-1,1:-1]) )*y[1:-1, :-2] -2*(1+beta_**2)*y[1:-1,1:-1] + (beta_**2)*y[2:,1:-1] + (beta_**2)*y[:-2,1:-1] )  #No heat input or heat loss in interior.
    
##################    
    
    # z=0 boundary for all r values not 0 or R
    # Edited 2/27/25 to make boundary 2nd order in \Delta z 2/28 this seems to work.
    if bcS_[0]==1:
        rhs_out[0, 1:-1] = tau_*( (1 + 1/(2*r_index[0,1:-1]) )*y[0, 2:] + (1 - 1/(2*r_index[0,1:-1]) )*y[0, :-2] -(2+3.5*beta_**2)*y[0,1:-1] + 4*(beta_**2)*y[1,1:-1] -0.5*(beta_**2)*y[2,1:-1]  ) - delta2_*y[0,1:-1] # I think the heat loss term has the right surface area      
        
    # z = L boundary for all r values not 0 or R
    # Now error is second order in \Delta z, seems to work 2/28
    if bcS_[1]==1:
        rhs_out[-1, 1:-1] = tau_*( (1 + 1/(2*r_index[-1,1:-1]) )*y[-1, 2:] + (1 - 1/(2*r_index[-1,1:-1]) )*y[-1, :-2] -(2+3.5*beta_**2)*y[-1,1:-1]  + 4*(beta_**2)*y[-2,1:-1] -0.5*(beta_**2)*y[-3,1:-1] )  - delta2_*y[-1,1:-1] # I think the heat loss term has the right surface area      

############
        
    # r = 0 boundary for all z values not 0 or L
    # Edited 2/27/25 to make boundary 2nd order in \Delta r 2/28 no it's not working
    if bcS_[2]==1:
        #rhs_out[1:-1, 0] = tau_*( 4*y[1:-1, 1] +  -2*(2+beta_**2)*y[1:-1,0] + (beta_**2)*y[2:,0] + (beta_**2)*y[:-2,0] ) # no heat input or heat loss at r=0
        rhs_out[1:-1, 0] = tau_*(-1*y[1:-1, 2] +  8*y[1:-1, 1] +  -2*(3.5+beta_**2)*y[1:-1,0] + (beta_**2)*y[2:,0] + (beta_**2)*y[:-2,0] ) # no heat input or heat loss at r=0
        
    # r = R boundary for all z values not 0 or L
    # Edited 2/27/25 to make boundary 2nd order in \Delta r 2/28 no it's not working
    if bcS_[3]==1:
        rhs_out[1:-1, -1] = tau_*(2*y[1:-1, -2] -2*(1+beta_**2)*y[1:-1,-1] + (beta_**2)*y[2:,-1] + (beta_**2)*y[:-2,-1] )  + gamma_*x_h_[1:-1] - delta_*y[1:-1,-1] # All heat input and loss is here on the boundary.
        #rhs_out[1:-1, -1] = tau_*(-0.5*y[1:-1, -3] + 4*y[1:-1, -2] - (3.5+2*beta_**2)*y[1:-1,-1] + (beta_**2)*y[2:,-1] + (beta_**2)*y[:-2,-1]  )  + gamma_*x_h_[1:-1] - delta_*y[1:-1,-1] # All heat input and loss is here on the boundary.

###########    
    
    # Boundary at z=0, r=0
    # Problem here!!!  Fixed it 2/9/25
    if bcS_[4]==1:
        #rhs_out[0, 0] = tau_*(4*y[0, 1] -2*(2+beta_**2)*y[0,0] + 2*(beta_**2)*y[1,0] ) - delta2_*y[0,0] # no heat input, I think there is heat loss.
        rhs_out[0, 0] = tau_*(4*y[0, 1] -(4+3.5*beta_**2)*y[0,0] + 4*(beta_**2)*y[1,0] -0.5*(beta_**2)*y[2,0]  ) - delta2_*y[0,0] # no heat input, I think there is heat loss.
        #rhs_out[0, 0] = 0
        
    # Boundary at z=0, r=R
    # Edited 2/27/25 to make boundary 2nd order in \Delta r - no broken!! went back to old method.
    if bcS_[5]==1:
        rhs_out[0, -1] = tau_*( 2*y[0,-2] - (2+3.5*beta_**2)*y[0,-1] + 4*(beta_**2)*y[1,-1] -0.5*(beta_**2)*y[2,-1] ) - delta_*y[0,-1] - delta2_*y[0,-1] #no heat in. The heat loss is coming from end and side of rod.  Will this work?
        #rhs_out[0, -1] = tau_*(-0.5*y[0, -3] + 4*y[0,-2] -2*(1.75+beta_**2)*y[0,-1] + 2*(beta_**2)*y[1,-1] ) - delta_*y[0,-1] - delta2_*y[0,-1] #no heat in. The heat loss is coming from end and side of rod.  Will this work?
        #rhs_out[0, -1] = 0 


    # Boundary at z=L, r=0
    if bcS_[6]==1:
        #rhs_out[-1, 0] = tau_*( 4*y[-1, 1] -2*(2+beta_**2)*y[-1,0] + 2*(beta_**2)*y[-2,0] ) #no heat input and I really think there is no heat loss.
        rhs_out[-1, 0] = tau_*( 4*y[-1, 1] -(4+3.5*beta_**2)*y[-1,0] + 4*(beta_**2)*y[-2,0] -0.5*(beta_**2)*y[-3,0] ) - delta2_*y[-1,-1] #no heat input and I really think there is no heat loss.
        #rhs_out[-1, 0] = 0
        
    # Boundary at z=L, r=R
    # Edited 2/27/25 to make boundary 2nd order in \Delta r - broken!! 2/28
    if bcS_[7]==1:
        #rhs_out[-1, -1] = tau_*( 2*y[-1,-2] -2*(1+beta_**2)*y[-1,-1] + 2*(beta_**2)*y[-2,-1] ) - delta_*y[-1,-1] - delta2_*y[-1,-1] #no heat in. The heat loss is coming from end and side of rod.  Will this work?
        rhs_out[-1, -1] = tau_*(2*y[-1,-2] - (2+3.5*beta_**2)*y[-1,-1] + 4*(beta_**2)*y[-2,-1] -0.5*(beta_**2)*y[-3,-1] ) - delta_*y[-1,-1] - delta2_*y[-1,-1]
        #rhs_out[-1, -1] = 0 
        

        
    return rhs_out



