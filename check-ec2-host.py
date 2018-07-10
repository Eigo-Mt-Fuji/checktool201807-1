import sys
import yaml
import json
import datetime

base_key = sys.argv[1] # 'prod.children'
inventory_file = sys.argv[2] # ./inventory.yml
running_instance_file = sys.argv[3] # ./describe-instances.json
hosts_value_key = "server_name"
dt_now = datetime.datetime.now()

def find_inventory_hosts_path(target_path, data, path_list):
  res = dparse(data, target_path, ".")
    
  if res is {} or res is None:
    return

  else:
    for key in res:
      next_path = target_path +"." + key

      if key == "hosts":
        path_list.append(next_path)
      else:
        if(type(res.get(key)) is dict):
          find_inventory_hosts_path(next_path, data, path_list)

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

  out_hosts_path_list = []
  find_inventory_hosts_path(base_key, data, out_hosts_path_list)

  for p in out_hosts_path_list:
    hosts = dparse(data, p, ".")
    for key in hosts.keys():
      print ("* " + p + "." + key)
      inventory_list.append(key)

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
    print ("```")
    print ("[")
    print ("\t\"" + "\",\n\t\"".join(inventory_not_in_ec2) + "\"")
    print ("]")
    print ("```")
  else:
    print ("* なし")

  print("### EC2 ( not in inventory )")
  if len(ec2_not_in_inventory) != 0:
    print ("```")
    print ("[")
    print ("\t\"" + "\",\n\t\"".join(ec2_not_in_inventory) + "\"")
    print ("]")
    print ("```")
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
