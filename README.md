# Eve-Insurance-Fraud

A simple python script that checks the specific region for Ships that would be profitable to buy off Sell order, insure and blow up in the method of your choosing!

## Installation
Pull down the repo
```shell
git clone https://github.com/skiedude/Eve-Insurance-Fraud.git
```

Create a virtual env
```shell
virtualenv venv
cd venv
source bin/activate
```

Install required pip packages
```shell
pip install -r requirements.txt
```

## Usage

### Help
```shell
$ python insurance.py -h
usage: insurance.py [-h] [--region REG_NAME] [--list-regions LIST_REGIONS]

Check for Profitable Insurance Frauds

optional arguments:
  -h, --help            show this help message and exit
  --region REG_NAME     Qouted Region Name ie: 'the forge'
  --list-regions LIST_REGIONS List all regions
```

### List Regions
```shell
$ python insurance.py --list-regions true
Derelik,The Forge,Vale of the Silent.......
```

### Check Specific Region
```shell
$ python insurance.py --region 'Genesis'
Looking up prices in Region: Genesis
Ship: Magnate
 Total Profit: 27,396.2
 Total Volume Remaining: 1
 Min price: 225,000.0
 Max Price: 225,000.0

Ship: Tormentor
 Total Profit: 78,299.4
 Total Volume Remaining: 3
 Min price: 260,000.0
 Max Price: 260,000.0

Ship: Navitas
 Total Profit: 378,775.0
 Total Volume Remaining: 10
 Min price: 200,000.0
 Max Price: 200,000.0

Ship: Incursus
 Total Profit: 391,393.6
 Total Volume Remaining: 8
 Min price: 200,000.0
 Max Price: 200,000.0
```
