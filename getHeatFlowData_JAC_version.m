function result=getHeatFlowData_JAC_version(pulsetime,lagTime,dataduration,ends,note);

% Set up the beginning constants
dataduration = pulsetime + lagTime;
sample_rate = 100; % 100 Hz
NSAO = floor(pulsetime * sample_rate); % number of samples for analog output pulse
NSAI = floor(dataduration * sample_rate); % number of samples for analog input

% Begin the dataAcquisition interface
d = daq("ni");

addinput(d, 'Dev3', 'ai1', 'Voltage') % voltage on bottom of heater
addinput(d, 'Dev3', 'ai2', 'Voltage') % V_0 at top of voltage divider (thermistor circuit)
addinput(d, 'Dev3', 'ai3', 'Voltage') % thermistor 1
addinput(d, 'Dev3', 'ai4', 'Voltage') % thermistor 2
addinput(d, 'Dev3', 'ai5', 'Voltage') % thermistor 3
addinput(d, 'Dev3', 'ai6', 'Voltage') % thermistor 4
addinput(d, 'Dev3', 'ai7', 'Voltage') % V_0 from top of heater circuit
addinput(d, 'Dev3', 'ai8', 'Voltage') % Voltage across known resistor (for I)
addinput(d, 'Dev3', 'ai9', 'Voltage') % Voltage across calibrated thermistor

d.rate = sample_rate;
d.DurationInSeconds = dataduration;

if NSAO > 0
    addoutput(d, 'Dev3', 'ao0', 'Voltage')
    outputData = zeros(1, dataduration * sample_rate);
    outputData((lagTime * sample_rate):(lagTime * sample_rate) + NSAO) = 5;
    queueOutputData(d, outputData');
end


[rawData, timeData] = read(d);

% Record the voltages for finding resistance of calibrated thermistor at beginning and end of data collection
lagIndex = find(timeData == lagTime);
endIndex = find(timeData == (lagTime + pulsetime));

V_known_resistor_start = rawData(lagIndex, 9);
V_known_resistor_end = rawData(endIndex, 9);

V_calib_thermistor_start = rawData(lagIndex, 10);
V_calib_thermistor_end = rawData(endIndex, 10);

% Calculate the calibrated thermistor's reistance at start
R_calib_thermistor_start = V_calib_thermistor_start / (V_known_resistor_start - V_calib_thermistor_start) * 993.4; % Resistance of calibrated thermistor at start

% Calculate the calibrated thermistor's resistance at end
R_calib_thermistor_end = V_calib_thermistor_end / (V_known_resistor_end - V_calib_thermistor_end) * 993.4; % Resistance of calibrated thermistor at end

% Calculating temperature
a = 0.0033755692934735893;
b = -2.799385186275534;
c = 692.6654624819034;

Temp_start_roots = roots([a, b, c - R_calib_thermistor_start]);
Temp_end_roots = roots([a, b, c - R_calib_thermistor_end]);

Temp_start = Temp_start_roots(real(Temp_start_roots) >= 290 & real(Temp_start_roots) <= 320);
Temp_end = Temp_end_roots(real(Temp_end_roots) >= 290 & real(Temp_end_roots) <= 320);

Temp_start = real(Temp_start);
Temp_end = real(Temp_end);

t = ((1:NSAI) / sample_rate)';

result(:, 1) = t;  % times, in seconds
result(:, 2) = rawData(:, 1); % heater voltage data
result(:, 3) = rawData(:, 2); % thermometer input voltage
result(:, 4) = rawData(:, 3); % thermistor one
result(:, 5) = rawData(:, 4); % thermistor two
result(:, 6) = rawData(:, 5); % thermistor three
result(:, 7) = rawData(:, 6); % thermistor four
result(:, 8) = rawData(:, 7); % V_0 from top of heater circuit

y = plotHeatFlow(result,4);

path = "E:/ThermalDiffusion/";
file = strcat(path,num2str(lagTime),"_",num2str(pulsetime),"_",num2str(dataduration-lagTime),"_",ends,"_",Temp_start,"Ti","_",Temp_end,"Tf","_",note,"_",datestr(datetime('now'),'mmmm dd, yyyy HH-MM AM'),".csv");
writematrix(result,file);
