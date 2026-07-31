from utility import REGISTRY
import json
import sys
import nhl

if __name__ == '__main__':
    model = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) == 3 else None

    REGISTRY[model].request(params=params, train=True) if params else REGISTRY[model].request(train=True)
    REGISTRY[model].digest()
    REGISTRY[model].train()