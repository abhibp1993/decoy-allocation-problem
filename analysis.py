import json
from json import JSONDecoder
from tqdm import tqdm

num_nodes = 50
num_edges = 3
num_decoys = 3


class SetDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(SetDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)
        # JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        return obj


if __name__ == '__main__':
    with open(f"logs/search_n{num_nodes}_e{num_edges}_k{num_decoys}.json") as file:
        data = json.load(file)

    print(f"Analyzing file: search_n{num_nodes}_e{num_edges}_k{num_decoys}.json")
    for data_dict in data:
        try:
            covered_combinatorial = data_dict["covered_combinatorial"]
            covered_greedysetcover = data_dict["covered_greedysetcover"]
            covered_greedymax = data_dict["covered_greedymax"]

            if len(covered_combinatorial) != len(covered_greedymax) or \
                    len(covered_combinatorial) != len(covered_greedysetcover):

                print(f"--- INTERESTING CASE: Seed = {data_dict['seed']} --- ")
                print("covered_combinatorial: ", len(data_dict["covered_combinatorial"]))
                print("covered_greedysetcover: ", len(data_dict["covered_greedysetcover"]))
                print("covered_greedymax: ", len(data_dict["covered_greedymax"]))

        except KeyError:
            pass
