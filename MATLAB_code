function result=getHeatFlowData_yashVersion(pulsetime,lagTime ,dataduration,sendToVsCode,ends,note);
% Written by B.G. Thompson.
% Edited MCS February 2015 for Matlab session interface.
% Edited MCS June 2016 to add third and fourth thermistor
% Edited MCS January 2017 to add input voltage, V_0 for voltage divider
% Edited MCS October 2021 to add second input voltage, again V_0 but this
%   time for heater circuit
% function to send a pulse for the number of seconds given
%   by pulsetime and gather data from the thermistors
%   for the number of seconds dataduration.
% Uses the NIDAQ Data Aquisition Board.
% Wire DAC0_OUT to the pulse FET and also to the input
%   channel ACH0.
% Channel 0 takes the heater voltage.
% Channel 1 takes the input to the thermometer circuit
% Wire Analog Input channels 2 through 5 to the outputs of the thermistor
%   circuits.
% Returns data for three channels in rawData at the times timeData.
%
% Be careful to use the correct T0 for the different setups.
% Original BGT copper rod: T0 = 3440 K (listed in paper)
% Large copper arch (2016 construction): T0 = 3068 K
% Aluminum arch (2018 consctruction): T0 = 3518 K. 


% %%%%%%%%%Notes for Yash version September 2023
% Note for Prof. Matt:
% The new function for data capturing is structured as followed:
% getHeatFlowData_yashVersion(heatPulse,
% 			lagTime,
% 			duration, 
% 			save,
% 			ends, 
% 			note);
% heatPulse (int(sec)): heater on time
% lagTime (int(sec)): how much to wait before heating
% duration (int(sec)): time after lag time to capture data
% save (boolean): saves the data in the folder where we can retrive it from in vsCode
% ends (string) notes about the run such as conditions of rod's end
% note (String): other stuff
% Total duration of the run is lagTime + duration;
% Now if the heat pulse is set to 0 sec the heat WILL NOT turn on !!!
% 
% UPDATE!!!!!!!!!!!!!!!!!!!!
% working on new format of file naming and using that to import settings in python code automatically
%%%%% End September 2023 update



dataduration = dataduration+ lagTime;
SR = 100; %SR is nearly always 100 Hz.
NSAO = floor(pulsetime * SR);
NSAI = floor(dataduration * SR);
% set up analog input
%This uses the Session-based interface.  MCS Jan 2015
s = daq.createSession('ni');
addAnalogInputChannel(s,'Dev3',[0:6], 'Voltage');
s.Channels(1).InputType = 'SingleEnded'; % voltage on bottom of heater
s.Channels(2).InputType = 'SingleEnded'; % V_0 at top of voltage didiver (thermistor ckt)
s.Channels(3).InputType = 'SingleEnded'; % thermistor 1
s.Channels(4).InputType = 'SingleEnded'; % thermistor 2
s.Channels(5).InputType = 'SingleEnded'; % thermistor 3
s.Channels(6).InputType = 'SingleEnded'; % thermistor 4
s.Channels(7).InputType = 'SingleEnded'; % V_0 from top of heater ckt
s.Rate = SR;
s.DurationInSeconds = dataduration;

if NSAO >0
    addAnalogOutputChannel(s,'Dev3',0,'Voltage')
    outputData = zeros(1,dataduration*SR);
    outputData((lagTime*SR):(lagTime*SR)+NSAO) = 5;
    queueOutputData(s,outputData');
end

[rawData,timeData] = s.startForeground;


t=((1:NSAI)/SR)';



result(:,1) = t;  %times, in seconds
result(:,2) = rawData(:,1); % heater voltage data
result(:,3) = rawData(:,2); % thermometer input voltage
result(:,4) = rawData(:,3); % thermistor one
result(:,5) = rawData(:,4); % thermistor two
result(:,6) = rawData(:,5); % thermistor three
result(:,7) = rawData(:,6); % thermistor four
result(:,8) = rawData(:,7); % V_0 from top of heater ckt

%close all


y = plotHeatFlow(result,4);

% save data file 
t = now;
d = string(datetime(t,'ConvertFrom','datenum'));
%{
file naming format please don't change if you are using the corresponding python code to analysis.
 lagTime_pulseLength_experimentTime_endConditon_note_timeStamp.csv
%} 

if sendToVsCode == true
    
    path = "E:/ThermalDiffusion/";
    s =strcat(path,num2str(lagTime),"_",num2str(pulsetime),"_",num2str(dataduration-lagTime),"_",ends,"_",note,"_",datestr(datetime('now'),'mmmm dd, yyyy HH-MM AM'),".csv");
    writematrix(result,s);
    writematrix(y,strcat(path,"compare.csv"));
end    

%figure
plot(result(:,1), result(:,2));
