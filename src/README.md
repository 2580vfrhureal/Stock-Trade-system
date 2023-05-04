## how to run

### parameters:  
instance type: `t2.micro`  
InstanceID: `i-0588163cb41a73ccb`  
publicDNS: `ec2-54-90-183-189.compute-1.amazonaws.com`  
publicIP: `54.90.183.189`

config aws:  
```shell
$ aws configure  
$ aws ec2 run-instances --image-id ami-0d73480446600f555 --instance-type t2.micro --key-name vockey > instance.json
$ aws ec2 describe-instances --instance-id <your instance id>  
$ chmod 400 labsuser.pem  

# expose ports 
$ aws ec2 authorize-security-group-ingress --group-name default --protocol tcp --port 22 --cidr 0.0.0.0/0  
$ aws ec2 authorize-security-group-ingress --group-name default --protocol tcp --port 10001 --cidr 0.0.0.0/0  
$ aws ec2 authorize-security-group-ingress --group-name default --protocol tcp --port 20001 --cidr 0.0.0.0/0  
$ aws ec2 authorize-security-group-ingress --group-name default --protocol tcp --port 20002 --cidr 0.0.0.0/0  
$ aws ec2 authorize-security-group-ingress --group-name default --protocol tcp --port 20003 --cidr 0.0.0.0/0  
$ aws ec2 authorize-security-group-ingress --group-name default --protocol tcp --port 30001 --cidr 0.0.0.0/0
```
  
connect to aws server:  
```shell
$ ssh -i labsuser.pem ubuntu@<your-instance's-public-DNS-name>
```  
update and install packages:  
```shell
$ sudo apt-get update
$ sudo apt-get -y install python3-pip
$ pip3 install flask
```
cd to your directory  
start servers:  
```shell
$ python3 catalog.py
$ ID=1 PORT=20001 python3 order.py
$ ID=2 PORT=20002 python3 order.py
$ ID=3 PORT=20003 python3 order.py
$ python3 front_end.py
```
start client.py:  p is the probability can adjust between 0 and 1
```shell
$ FRONT=<aws-publicIP> p=0.5 python client.py 
```
