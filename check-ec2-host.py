import sys
import yaml
import json
import datetime

base_key = sys.argv[1] # 'prod.children'
inventory_file = sys.argv[2] # ./inventory.yml
running_instance_file = sys.argv[3] # ./describe-instances.json
dt_now = datetime.datetime.now()

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

print ("\033[m" + "# check-ec2-host " + dt_now.strftime("%Y-%m-%d %H:%M:%S"))
print ("## Inventory List")
inventory_list = []
with open(inventory_file) as f:
  data = yaml.load(f)
  groups = dparse(data, base_key, ".")
  for g in groups:
    print("* Loading Group " + g + "...")
    categories = dparse(data, base_key + "." + g, ".")
    for c in categories:
       print("\t* Loading Category " + c + "...")
       hosts = dparse(data, base_key + "." + g + "." + c, ".")
       inventory_list.extend(hosts.keys())
       for h in hosts:
         print ("\t\t* " + h)
f.closed

with open(running_instance_file, 'r') as f:
  ec2_list = json.load(f)

  print ("## Running EC2 List")
  for ec2 in ec2_list:
    print("* " + ec2 )
  
  inventory_not_in_ec2 = []
  for inventory in inventory_list:
    if inventory not in ec2_list:
      inventory_not_in_ec2.append(inventory)
  
  ec2_not_in_inventory = []
  for ec2 in ec2_list:
    if ec2 not in inventory_list:
      ec2_not_in_inventory.append(ec2)

  print("## 比較結果")  
  print("### Inventory ( not in EC2 )")
  if len(inventory_not_in_ec2) != 0:
    for h in inventory_not_in_ec2:
      print ("* " + h)
  else:
    print ("* なし")

  print("### EC2 ( not in inventory )")
  if len(ec2_not_in_inventory) != 0:
    for h in ec2_not_in_inventory:
      print ("* " + h)
  else:
    print ("* なし")
  if len(ec2_not_in_inventory) != 0 or len(inventory_not_in_ec2) != 0:
    print ("\033[91m" + "差分を検知しました")
    print ("\033[m" + "")
    sys.exit(1)
  else:
    print ('\033[m' + "差分はありません")
    sys.exit(0)


f.closed
