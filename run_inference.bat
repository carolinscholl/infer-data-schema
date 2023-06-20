@echo off
set BATDIR=%~dp0
set DATA_PATH=%~f1
set SCHEMA_PATH=%~f2

pushd "%BATDIR%"
set PYTHONPATH=%PYTHONPATH%;"%BATDIR%"

rem Define here the path to your conda installation
set CONDAPATH=C:\Program Files\Anaconda3
rem Define here the name of the environment
set ENVNAME=infer-schema

if %ENVNAME%==base (set ENVPATH="%CONDAPATH%") else (set "ENVPATH=%CONDAPATH%\envs\%ENVNAME%")

rem Activate the conda environment
rem Using call is required here, see: https://stackoverflow.com/questions/24678144/conda-environments-and-bat-files
call "%CONDAPATH%\Scripts\activate.bat" "%ENVPATH%"

if [%1]==[] goto help
if [%2]==[] goto standard_case
goto custom_schema_path

:help
python "%BATDIR%\infer_schema\main.py"
goto end

:standard_case
python "%BATDIR%\infer_schema\main.py" %DATA_PATH%
goto end

:custom_schema_path
python "%BATDIR%\infer_schema\main.py" %DATA_PATH% --schema_fpath %SCHEMA_PATH%
goto end

:end
call deactivate
