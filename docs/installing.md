Installing
==============

## Insalling from pip
Note that rlottie is included in the wheel package, you need not install librlottie.

To install, run the following:
```
pip3 install wheel
pip3 install rlottie-python
```

## Building from source

To build wheel, run the following:
```
git clone --recursive https://github.com/laggykiller/rlottie-python.git
cd rlottie-python
pip3 install -r requirements.txt
python3 -m build .
```

To install the built wheel, run `pip3 install dist/<name_of_the_wheel_file>.whl`

If you want to install directly, run the following:
```bash
git clone --recursive https://github.com/laggykiller/rlottie-python.git
cd rlottie-python
pip3 install -r requirements.txt
pip3 install .
```