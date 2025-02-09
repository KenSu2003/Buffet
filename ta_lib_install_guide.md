
# Guide to Installing TA-Lib on Raspberry Pi (Including Python Wrapper)

This guide will help you successfully install the **TA-Lib 0.6.4 C library** and the Python wrapper on a Raspberry Pi. Follow these steps carefully to resolve any build issues.

---

## **1. Install System Dependencies**
Update the system and install the necessary development tools:

```bash
sudo apt-get update
sudo apt-get install -y build-essential automake libtool python3-dev python3-pip
```

---

## **2. Download and Install the TA-Lib C Library (0.6.4)**
Download and compile the TA-Lib C core library:

```bash
# Download the source
wget https://github.com/TA-Lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz

# Extract the source
tar -xzvf ta-lib-0.6.4-src.tar.gz
cd ta-lib-0.6.4

# Configure, build, and install
./configure --prefix=/usr
make
sudo make install
```

### **Verify the Installation:**
Ensure that the necessary files are installed:

```bash
ls /usr/lib | grep ta-lib
```

You should see files like:
```
libta_lib.so
libta_lib.a
```

---

## **3. Set Up the Library Path**
Update the shared library cache to make sure the system can find the installed libraries:

```bash
echo "/usr/lib" | sudo tee -a /etc/ld.so.conf.d/ta-lib.conf
sudo ldconfig
```

Verify that the system recognizes the library:

```bash
ldconfig -p | grep ta-lib
```

---

## **4. Install the Python TA-Lib Wrapper**
### **Step 1: Clone the TA-Lib Python repository**
```bash
git clone https://github.com/TA-Lib/ta-lib-python.git
cd ta-lib-python
```

### **Step 2: Clean any previous builds**
```bash
python3 setup.py clean
```

### **Step 3: Build and install the Python wrapper**
```bash
export CFLAGS="-I/usr/include/ta-lib"
export LDFLAGS="-L/usr/lib"
pip install .
```

---

## **5. Verify the Installation**
Activate your virtual environment (if applicable):

```bash
source ~/Buffet/venv/bin/activate
```

Then test the installation:

```bash
python3 -c "import talib; print(talib.__version__)"
```

You should see something like:
```
0.6.3
```

---

## **6. Troubleshooting Tips**
- If you encounter **ModuleNotFoundError: No module named 'talib._ta_lib'**, ensure that the shared library path is correctly set:

  ```bash
  export LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
  ```

- If `ldconfig -p | grep ta-lib` does not show the library, make sure you ran `sudo ldconfig` after installing the C library.

---

By following this guide, you should be able to consistently install and link **TA-Lib** on any Raspberry Pi without issues! 😊
