# Pinn2DCM

## Introduction

This modules serves to convert old Pinnacle CTs into the DICOM format. It can be called from the command line for batch processing, however an optional GUI is also available. 

Currently, this module is the minimum viable product. It was tested with a single anonymized dataset, therefore many features that might be of interested are not yet available. Please feel free to contact me if you have any questions or suggestions!

## Usage

The script requires you to provide two paths: the path to the Pinnacle CT directory and the path to the output directory. The Pinnacle CT directory needs to contain the following files:
```bash
├── Pinnacle CT directory  
│   ├── *.img
│   ├── *.header
│   ├── *.ImageInfo
│   ├── *.ImageSet
```	

To start conversion, run the following command:

```console
$ pinn2dcm "path to Pinnacle CT directory" "path to output directory"   
```

To start the GUI, run the fcommand without any arguments:

```console 
$ pinn2dcm
```

![GUI](https://user-images.githubusercontent.com/87897942/227711992-3b7791f3-a094-4d1d-bb03-879f56db592f.png)

## Installation

You can either download the repository manually and extract it, use `git clone`, or install using pip:

```console
$ pip install pinn2dcm   
```

#### Note: If Python is not added to your PATH, you may need to preface the above commands with `python -m` !

## Dependencies

* Numpy
* Pydicom

## Contact

If you have any questions or suggestions, please feel free to contact me at se.schaefer@uke.de!
