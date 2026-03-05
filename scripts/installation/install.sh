#!/bin/bash
echo "Installing all components..."

pip install -e api
pip install -e platform
pip install -e plugins/csv_datasource
pip install -e plugins/json_datasource
pip install -e plugins/xml_datasource
pip install -e plugins/block_visualizer
pip install -e plugins/simple_visualizer

echo "All components installed successfully!"