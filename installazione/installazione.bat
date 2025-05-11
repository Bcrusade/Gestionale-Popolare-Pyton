@ECHO OFF

python --version 3>NUL
if errorlevel 1 goto errorNoPython
goto :hasPython
:errorNoPython
rem --Download python installer
curl "https://www.python.org/ftp/python/3.9.4/python-3.9.4-amd64.exe" -o python-installer.exe

rem --Install python
python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

rem --Refresh Environmental Variables
call RefreshEnv.cmd
:hasPython
cd ..
python -m venv venv
call .\venv\Scripts\activate.bat
pip install -U Flask
pip install pywin32
pip install waitress
call .\venv\Scripts\deactivate.bat

cd ./installazione
del python-installer.exe

pause