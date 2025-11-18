Smart Image Cropper & Resizer
A simple and fast cross-platform image cropping and resizing tool built with Python and PyQt5.

This tool allows you to:

Crop any image using drag-select

Resize output image based on percentage

Automatically scale images without resizing the window

Save output in PNG or JPG format

Supports Drag & Drop

This project provides:

Full open-source Python code

Prebuilt executables for Windows (EXE), macOS (APP), and Linux (ELF)

GitHub Actions automatically builds all releases from the source code.

Project Structure:
SmartImageCropper/
src/main.py
resources/icon.png
.github/workflows/build.yml
requirements.txt
README.md
LICENSE
.gitignore

Installation (run from source):
pip install -r requirements.txt
python src/main.py

Manual Build (PyInstaller):
Windows: pyinstaller --onefile --windowed src/main.py -n SmartImageCropper.exe
macOS: pyinstaller --onefile --windowed src/main.py -n SmartImageCropper
Linux: pyinstaller --onefile --windowed src/main.py -n SmartImageCropper

Automatic Build via GitHub Actions:
Executables for all platforms are automatically generated when you push a git tag starting with v.
Example:
git tag v1.0.0
git push origin v1.0.0

License:
MIT License.