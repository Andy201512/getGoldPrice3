import time,json,re

with open('items.jl') as f:
    temp = f.readlines()

    temp.sort(key=lambda d : time.mktime(time.strptime(re.search(r'\d{4}-\d{2}-\d{2}', d).group(),"%Y-%m-%d")))
    
    for i in temp:
        json_temp = json.loads(i)
        try:
            price = float(json_temp["price"])
        except ValueError:
            print("以下条目存在价格缺失或错误")
            print(json_temp)

with open('sorted.jl', 'w') as f:
    for i in temp:
        f.write(i)
