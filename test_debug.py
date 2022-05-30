import json

if __name__ == '__main__':
    with open('al/algo.json', 'r') as f:
        algo_list = json.load(f)
        a = json.dumps(algo_list)
        print(a)