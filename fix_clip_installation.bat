@echo off
echo ============================================================
echo Fixing CLIP Installation
echo ============================================================
echo.
echo This script will fix the setuptools/pkg_resources issue
echo and install CLIP properly.
echo.

cd /d "%~dp0"

echo Step 1: Upgrading setuptools...
venv\Scripts\python.exe -m pip install --upgrade --force-reinstall setuptools
if errorlevel 1 (
    echo Failed to upgrade setuptools
    pause
    exit /b 1
)

echo.
echo Step 2: Verifying pkg_resources...
venv\Scripts\python.exe -c "import pkg_resources; print('pkg_resources OK')"
if errorlevel 1 (
    echo pkg_resources still not available, trying to fix...
    venv\Scripts\python.exe -m pip uninstall -y setuptools
    venv\Scripts\python.exe -m pip install setuptools
)

echo.
echo Step 3: Installing CLIP...
echo Trying PyPI method first...
venv\Scripts\python.exe -m pip install git+https://github.com/openai/CLIP.git
if errorlevel 1 (
    echo PyPI method failed, trying zip method...
    venv\Scripts\python.exe -m pip install --no-build-isolation https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip
)

if errorlevel 1 (
    echo.
    echo ============================================================
    echo CLIP installation failed.
    echo Please check the error messages above.
    echo ============================================================
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================
    echo CLIP installed successfully!
    echo You can now run webui.bat
    echo ============================================================
)

pause
