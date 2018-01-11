import time
import numpy as np
import pandas as pd

from argparse import ArgumentParser

from combat import find_balance, fight
from unit import make_unit, Stack
from crtraits import data


names = [d[0] for d in data]

def calculate_scores(num_fights=500, log=100):
    num_units = len(names)
    scores = np.eye(num_units)

    t0 = time.time()
    total_pairs = 0
    for u_idx in range(num_units):
        u_name = names[u_idx]
        for v_idx in range(u_idx + 1, num_units):
            v_name = names[v_idx]
            cnt_u, cnt_v = find_balance(u_name, v_name, num_fights, None)
            scores[u_idx, v_idx] = cnt_u / float(cnt_v)
            scores[v_idx, u_idx] = cnt_v / float(cnt_u)
            print('%s vs %s %.3f' % (u_name, v_name, cnt_u / float(cnt_v)))
            total_pairs += 1
            if not total_pairs % log:
                print('Done {} pairs in {:.2f}s'.format(
                    total_pairs, time.time() - t0))

    return scores


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-n', '--num_fights', type=int, default=500)
    parser.add_argument('-o', '--output_file', default='scores.csv')
    parser.add_argument('-l', '--log_interval', type=int, default=100)
    args = parser.parse_args()

    scores = calculate_scores(args.num_fights, args.log_interval)
    scores = pd.DataFrame.from_records(scores, columns=names)
    scores.insert(0, 'Name', pd.Series(names))
    scores.to_csv(args.output_file)
