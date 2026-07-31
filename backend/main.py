from utility import REGISTRY
import json
import sys
import nhl

if __name__ == '__main__':
    process = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) == 3 else None

    REGISTRY[process].request(params=params) if params else REGISTRY[process].request()
    REGISTRY[process].digest()
    REGISTRY[process].transform()