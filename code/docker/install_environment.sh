apt-get update
apt-get install sudo
chmod +x *.sh
sudo apt-get install python -y
sudo apt-get install software-properties-common -y
sudo apt-get install curl -y
sudo apt-get install mplayer -y
sudo apt-get install imagemagick -y
sudo apt-get install python-pil -y
curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
sudo python2 get-pip.py
pip install numpy
pip install scipy
pip install matplotlib
pip install cvxopt
rm get-pip.py
sudo apt-get install texlive-base texlive-pictures -y
sudo apt-get install texlive-latex-extra -y
sudo apt-get install python-tk -y
