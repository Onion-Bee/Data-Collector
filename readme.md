## Installation Guide

### Prerequisites

* **Python** (3.13.2): Download and install from [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/). Make sure to check "Add Python to PATH" during installation.
* **Visual Studio 2017 or newer** with "Desktop development with C++" workload (for building OpenFace) and **CMake** (install via [https://cmake.org/download/](https://cmake.org/download/))

### Clone the Repository
### Open Windows Powershell
```sh
# Open PowerShell or CMD as Administrator
git clone https://github.com/Onion-Bee/Data-Collector.git
cd Data-Collector
```

### Create and Activate a Virtual Environment

```sh
# Create a venv folder
pip install virtualenv
virtualenv venv
# Activate it
.\venv\Scripts\Activate.ps1
```

### Install Python Dependencies

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

### Install OpenFace on Windows 11

1. **Download Windows Binaries**

   * For 64-bit Windows, download the OpenFace v2.2.0 zip:
     `https://github.com/TadasBaltrusaitis/OpenFace/releases/download/OpenFace_2.2.0/OpenFace_v2.2.0_win_x64.zip` ([github.com](https://github.com/TadasBaltrusaitis/OpenFace/wiki/Windows-Installation?utm_source=chatgpt.com))
2. **Extract and Configure**

   ```sh
   # Extract to C:\OpenFace
   mkdir C:\OpenFace
   tar -xf OpenFace_v2.2.0_win_x64.zip -C C:\OpenFace
   ```
3. **Add to PATH**

   * Open System Properties → Advanced → Environment Variables
   * Under **System variables**, select **Path** → **Edit** → **New**, then add:

     ```txt
     C:\OpenFace\bin
     ```
4. **Download Models and Dependencies**

   * Open PowerShell as Administrator:

     ```ps1
     # Download DLLs and libraries
     C:\OpenFace\download_libraries.ps1
     # Download landmark and AU models
     C:\OpenFace\download_models.ps1
     ```
5. **(Optional) Python Wrapper**

   * If you need to use the OpenFace Python API:

     ```sh
     git clone https://github.com/cmusatyalab/openface.git
     cd openface
     pip install -r requirements.txt
     python setup.py install  # uses Python 2.7 by default ([stackoverflow.com](https://stackoverflow.com/questions/38020889/how-to-install-openface-in-windows-python?utm_source=chatgpt.com))
     ```

## Running Instructions

1. **Activate Virtual Environment** (if not already):

   ```sh
   .\venv\Scripts\Activate.ps1
   ```

2. **Run the Data Collector**

    ```sh
    cd App
    python main.py
    ```

