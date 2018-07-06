# README

## 概要

* 以下の流れで使う想定

```
1. ansibleのinventory fileを準備(yaml内でキー名がhostsの階層の直下のキー（もしくは項目値のserver_name）部分)
2. ec2instanceを取得(profile, regionは適宜読み替え)してjson保存
3. ツールを実行して終了コードを確認(1の場合エラー)
```

## 使い方
* git clone 

* ansibleのinventory fileを準備(4層目のキーがEC2のname属性と同じ想定)
  * 今回は手動作成
* vi ~/inventory.yml

```
stage:
  children:
    test:
      hosts:
        server1:
        server2:
    operation:
      hosts:
        server3:
        server4:
    api:
      children:
        official2:
          hosts:
            api1:  { server_name: "test_1" }
            api2:  { server_name: "test_2" }
            api3: { server_name: "test_3" }
        replica:
          vars:
            server_name: "test4"
          hosts:
            api4:
            api5:
        batch:
          hosts:
            batch1:
    proxy:
      hosts:
        proxy1:
```

* ec2instanceを取得(profile, regionは適宜読み替え)

```
$ aws --profile devops ec2 --region ap-southeast-1 describe-instances --filter "Name=instance-state-name,Values=running" --query 'Reservations[].Instances[] | [] . Tags[?Key==`Name`].Value|[0]' > describe-instances.json
[
  "server1",
  "server2",
  "server3",
  "server4",
  "test_1",
  "test_2",
  "test_3",
  "api4",
  "api5",
  "batch1",
  "proxy1",
  "invalid-host"
]
```

* check-ec2-host.pyを実行

```
$ python3 check-ec2-host.py stage.children ./inventory.yml describe-instances.json
# check-ec2-host 2018-07-07 07:58:08
## Inventory List
* stage.children.test.hosts.server1
* stage.children.test.hosts.server2
* stage.children.operation.hosts.server3
* stage.children.operation.hosts.server4
* stage.children.api.children.official2.hosts.api1.test_1
* stage.children.api.children.official2.hosts.api2.test_2
* stage.children.api.children.official2.hosts.api3.test_3
* stage.children.api.children.replica.hosts.api4
* stage.children.api.children.replica.hosts.api5
* stage.children.api.children.batch.hosts.batch1
* stage.children.proxy.hosts.proxy1
## Running EC2 List
* server1
* server2
* server3
* server4
* test_1
* test_2
* test_3
* api4
* api5
* batch1
* proxy1
* invalid-host
## 比較結果
### Inventory ( not in EC2 )
* なし
### EC2 ( not in inventory )
```
[
	"invalid-host"
]
```
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


