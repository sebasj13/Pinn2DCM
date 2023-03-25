import os
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pinn2dcm",
    version="1.0.0",
    author="Sebastian Schäfer",
    author_email="se.schaefer@uke.de",
    description="A Python package to convert old Pinnacle CTs to the DICOM format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sebasj13/Pinn2DCM",
    project_urls={"Bug Tracker": "https://github.com/sebasj13/Pinn2DCM/issues"},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy", "pydicom"],
    packages=["pinn2dcm"],
    scripts=["pinn2dcm/__main__.py"],
    entry_points={
        "console_scripts": ["pinn2dcm=pinn2dcm.__main__: main"],
    },
    keywords=["DICOM", "Pinnacle", "CT", "Radiation Therapy", "RT"],
    python_requires=">=3",
)
