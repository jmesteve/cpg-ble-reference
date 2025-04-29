# Change Log
All notable changes to this project will be documented in this file.


## 12.0
 - Memory optimizations
```
CONFIG_BOOT_BANNER=n
CONFIG_NCS_BOOT_BANNER=n
CONFIG_TIMESLICING=n
CONFIG_SPI_NOR=n
CONFIG_CBPRINTF_NANO=y
CONFIG_SETTINGS_DYNAMIC_HANDLERS=n
CONFIG_BT_LL_SOFTDEVICE_PERIPHERAL=y
CONFIG_BT_CTLR_SUBRATING=y
CONFIG_BT_GATT_CACHING=n
CONFIG_BT_SETTINGS_CCC_LAZY_LOADING=n
CONFIG_BT_SETTINGS_CCC_STORE_ON_WRITE=y
```

  - Disable unused CRACEN features
```
CONFIG_PSA_USE_CRACEN_HASH_DRIVER=n
CONFIG_PSA_USE_CRACEN_ASYMMETRIC_DRIVER=n
CONFIG_PSA_USE_CRACEN_ASYMMETRIC_SIGNATURE_DRIVER=n
CONFIG_PSA_USE_CRACEN_PAKE_DRIVER=n
CONFIG_PSA_USE_CRACEN_AEAD_DRIVER=n
CONFIG_MBEDTLS_MAC_SHA256_ENABLED=n
CONFIG_MBEDTLS_PSA_STATIC_KEY_SLOTS=y
CONFIG_MBEDTLS_PSA_KEY_SLOT_COUNT=6
CONFIG_MBEDTLS_PSA_STATIC_KEY_SLOT_BUFFER_SIZE=65
CONFIG_MBEDTLS_ENABLE_HEAP=n
CONFIG_FAULT_DUMP=0
CONFIG_ARM_MPU=n
CONFIG_BT_GATT_READ_MULTIPLE=n
CONFIG_BT_GATT_READ_MULT_VAR_LEN=n
```

- Activate Link Time Optimization (LTO)
```
CONFIG_LTO=y
CONFIG_ISR_TABLES_LOCAL_DECLARATION=y
```

  - Disable debug features
```
CONFIG_ASSERT=n
CONFIG_LOG=n
CONFIG_SERIAL=n
CONFIG_CONSOLE=n
CONFIG_UART_CONSOLE=n
CONFIG_RESET_ON_FATAL_ERROR=n
```

## 11.0
- CONFIG_BT_LOG_SNIFFER_INFO=n

## 10.0
- CONFIG_BT_MAX_CONN=3
- CONFIG_BT_MAX_PAIRED=3
- Increase the RAM in 2.4K  (41102B - 38687B = 2415B)

## 9.0
- Level 14 to see the unobfuscate API

## 8.0
- Added Drivers

## 7.0
- Removed logs

## 6.0
- unobfuscate API

## 5.0

### Added
- reports/20250424_main_5
- controller_sci: added Logi SCI configuration 
  
## 4.0

### Added
- reports/20250424_main_4
- p_hids_keyb: added Logi configuration 

## 3.0

### Added
- reports/20250423_main_3
- p_hids_keyb: peripeheral hids keyboard 
  
### Fixed
- Problems with long path lengths (CMAKE_OBJECT_PATH_MAX errors)
The build path length cannot exceed 255.


## 2.0

### Added
- reports/20250422_main_2
- reports/20250422_lto
- lto optimization

## 1.0

### Added
- reports/20250416_main_1
- peripehral_hids and central_hids  




