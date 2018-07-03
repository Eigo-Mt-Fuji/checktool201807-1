import sys
import yaml
import json

base_key = sys.argv[1] # 'prod.children'
inventory_file = sys.argv[2] # ./inventory.yml
running_instance_file = sys.argv[3] # ./describe-instances.json

def dparse(dic, p, sep=".", default=None):
    lis = p.split(sep)
    def _(dic, lis, sep, default):
        if len(lis) == 0:
            return default
        if len(lis) == 1:
            return dic.get(lis[0], default)
        else:
            return _(dic.get(lis[0], {}), lis[1:], sep, default)
    return _(dic, lis, sep=sep, default=None)

inventory_list = []
with open(inventory_file) as f:
  data = yaml.load(f)
  groups = dparse(data, base_key, ".")
  for g in groups:
    print("Loading Category " + g + "...")
    hosts = dparse(data, base_key + "." + g + ".hosts" , ".")
    inventory_list.extend(hosts.keys())
  print ("Ansible yamlに登録されたリスト")
  for inventory in inventory_list:
    print (inventory)
f.closed

with open(running_instance_file, 'r') as f:
  ec2_list = json.load(f)

  for inventory in inventory_list:
    if inventory not in ec2_list:
      print("エラー: 実行中ホストではない " + inventory + " がhostsに含まれています")
      sys.exit(1)

  for ec2 in ec2_list:
    if ec2 not in inventory_list:
      print("エラー: 実行中ホスト " + ec2 + " がhostsに含まれていません")
      sys.exit(1)

f.closed
