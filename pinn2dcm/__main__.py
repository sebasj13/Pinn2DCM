from pinn2dcm.pinn2dcm import Pinn2DCM, create_DICOM_CT
import sys
import os

def main():

    try:
        if os.path.isdir(sys.argv[1]) and os.path.isdir(sys.argv[2]):
            create_DICOM_CT(sys.argv[1], sys.argv[2])
            
    except IndexError:
        Pinn2DCM()
        
if __name__ == "__main__":
    main()