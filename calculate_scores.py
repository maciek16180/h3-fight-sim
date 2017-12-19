import time
import numpy as np
import pandas as pd

from argparse import ArgumentParser

from combat import find_balance, fight
from unit import make_unit, Stack, data


def calculate_scores(num_fights=500, log=100):
    units = data.values[:-5]
    scores = np.zeros((units.shape[0], units.shape[0]))

    t0 = time.time()
    total_pairs = 0
    for u_idx in range(units.shape[0]):
        u_name = units[u_idx][0]
        for v_idx in range(u_idx + 1, units.shape[0]):
            v_name = units[v_idx][0]
            print('%s vs %s' % (u_name, v_name))
            cnt_u, cnt_v = find_balance(u_name, v_name, num_fights)
            scores[u_idx, v_idx] = cnt_u / float(cnt_v)
            scores[v_idx, u_idx] = cnt_v / float(cnt_u)
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
    scores = pd.DataFrame.from_records(
        scores, columns=data.Singular.values[:-5])
    scores.insert(0, 'Name', pd.Series(data.Singular.values[:-5]))
    scores.to_csv(args.output_file)
