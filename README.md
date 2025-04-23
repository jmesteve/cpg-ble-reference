


# Installation
## Windows 11
## Python version
3.12.4
## Python dependencies
```
pip install -r .\requirements.txt
```
## NRF Connnect
Install the last version of [NRF Connect](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop)

# Help
python .\memory_report.py

# Build and Generate memory reports

## Feature 1, repository central_hids 
```
python .\memory_report.py -r central_hids -p nrf54l15dk/nrf54l15/cpuapp -f feat1  
```

## Optimization 1, repository central_hids, 2 levels 
```
python .\memory_report.py -r central_hids -p nrf54l15dk/nrf54l15/cpuapp -f opt1 -l 2
```

## Optimization 1, repository central_hids, 2 levels 
```
python .\memory_report.py -r central_hids -p nrf54l15dk/nrf54l15/cpuapp -f feat10 -l 2
```

## baseline std1 vs Optimization 1
```
python .\memory_report.py -r central_hids -p nrf54l15dk/nrf54l15/cpuapp -b std1 -f opt1
```


## 1 feature peripheral_hids
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp -l 3 -b std1 -f feat3  
```
## Multiple features peripheral_hids
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp -l 3 -b std1 -f feat1 feat2 opt1  
```
## All the features peripheral_hids
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp -l 3 -b std1
```

## Only generate reports without build
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp  -l 3 -b std1 --only-report
```

## Only generate the summary without build and report
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp  -l 3 -b std1 --only-summary
```

## Add version
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp  -l 3 -b std1 -v 20250417_main_1
```

## Add Extra configuration to the build
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp  -l 3 -b std1 -f std1 -v 20250416_main_2 --extra-config=opt_lto
```

## Add Snippet to the build
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp  -l 3 -b std1 -f std1 -v 20250416_main_2 -S bt-ll-sw-split
```
