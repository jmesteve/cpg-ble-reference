


# Installation
## Windows 11
## Python version
3.12.4
## Python dependencies
```
pip install -r .\requirements.txt
```

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

## Only generate the summary
```
python .\memory_report.py -r peripheral_hids -p nrf54l15dk/nrf54l15/cpuapp  -l 3 -b std1 --only-summary
```