@echo off

cd %USERPROFILE%\Desktop
mkdir HYCrawler
cd HYCrawler
echo installing Python3.6...
curl -o python36.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
python36.exe /quiet
echo downloading python codes ...
curl -LJO https://github.com/hgs3896/HYUPortalGradeCrawler/archive/refs/heads/main.zip
echo unzipping codes...
powershell -command "Expand-Archive -Path .\HYUPortalGradeCrawler-main.zip -DestinationPath .\\"
cd HYUPortalGradeCrawler-main
echo installing requirements...
pip install -r requirements.txt
echo start crawling script
python main.py
pause