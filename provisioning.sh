#Install Python
echo 'installing python'
sudo apt-get install build-essential
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
mkdir temp 
cd temp
wget http://python.org/ftp/python/2.7.5/Python-2.7.5.tgz
tar -xvf Python-2.7.5.tgz
cd Python-2.7.5
./configure
make
sudo make install
#up to temp
cd ..
wget http://www.web2py.com/examples/static/web2py_src.zip
echo 'installing web2py'
cd /home/vagrant
sudo apt-get install unzip
unzip /home/vagrant/temp/web2py_src.zip -d /home/vagrant
cd /home/vagrant/web2py
echo 'Starting web2py with passwd: rimi'
sudo nohup python web2py.py -a 'rimi' -d WEB2PY_PID &
echo 'Done.'


