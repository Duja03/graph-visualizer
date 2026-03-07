@echo off

echo Installing all dependencies...

pip install django
pip install flask
pip install flask_cors

echo All dependencies installed successfully!

echo Installing all components...

pip install -e api
pip install -e platform
pip install -e plugins/csv_datasource
pip install -e plugins/json_datasource
pip install -e plugins/xml_datasource
pip install -e plugins/block_visualizer
pip install -e plugins/simple_visualizer
pip install django flask flask_cors

echo.
echo All components installed successfully!
pause