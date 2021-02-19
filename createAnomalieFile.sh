cd /root/GateWay/UpdatedAnomali/ || exit
echo abcd | sudo -S rm anomalies.csv
echo abcd | sudo -S cp anomaliesTemp.csv anomalies.csv

echo abcd | sudo -S rm allowes.csv
echo abcd | sudo -S cp allowesTemp.csv allowes.csv