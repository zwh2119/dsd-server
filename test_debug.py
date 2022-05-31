import json

if __name__ == '__main__':
    with open('al/algo.json', 'r') as f:
        algo_list = json.load(f)
        print(list(algo_list.keys())[0])