# README

## 概要

* 以下の流れで使う想定

```
1. ansibleのinventory fileを準備(4層目のキーがEC2のname属性と同じ想定)
2. ec2instanceを取得(profile, regionは適宜読み替え)してjson保存
3. ツールを実行して終了コードを確認(1の場合エラー)
```

## 使い方
* git clone 

* ansibleのinventory fileを準備(4層目のキーがEC2のname属性と同じ想定)
  * 今回は手動作成
* vi ~/inventory.yml
```
prod:
  children:
    official:
      hosts:
        server1:
        server2:
    api:
      hosts:
        server1:
        server3:
    operation-host:
      hostsother:
        server1:
        server2:
```

* ec2instanceを取得(profile, regionは適宜読み替え)

```
$ aws --profile devops ec2 --region ap-southeast-1 describe-instances --filter "Name=instance-state-name,Values=running" --query 'Reservations[].Instances[] | [] . Tags[?Key==`Name`].Value|[0]' > describe-instances.json
[
    "server1",
    "server2",
]
```

* check-ec2-host.pyを実行

```
$ python3 check-ec2-host.py prod.children ./inventory.yml describe-instances.json
# check-ec2-host 2018-07-04 22:38:19
## Inventory List
* Loading Group official...
	* Loading Category hosts...
		* server1
		* server2
* Loading Group api...
	* Loading Category hosts...
		* server1
		* server2
* Loading Group operation-host...
	* Loading Category hostsother...
		* server1
		* server3
## Running EC2 List
* server1
* server2
## 比較結果
### Inventory ( not in EC2 )
* server3
### EC2 ( not in inventory )
* なし
差分を検知しました
$ echo $?
1
```

## 備考

## 補足: 実行環境

```
$ python3 --version
Python 3.7.0

$ pip3 install git+https://github.com/yaml/pyyaml.git
$ pip3 list
Package    Version
---------- -------
clang      6.0.0.1
pip        10.0.1
PyYAML     4.1
setuptools 39.2.0
wheel      0.31.1
$ export PATH=~/.local/bin:~/Library/Python/3.7/bin:$PATH
$ pip3 install --user --upgrade awscli
$ brew upgrade awscli
```


