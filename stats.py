import os.path
import pandas as pd
import string


PP_STATS = ('PPG', 'PPA', 'PPP')
SH_STATS = ('SHG', 'SHA', 'SHP')
STATS = ('G', 'A', 'P', 'SH', 'FOW', 'H', 'BLK') + PP_STATS
D_STATS = [stat for stat in STATS if stat != 'FOW']
VALID_CHARS = frozenset(string.ascii_letters + " -'")


def canonical_position(raw):
    return ','.join(sorted(raw.translate(raw.maketrans('', '', ' W')).split(',')))


def convert_percentage(value):
    return float(value.strip('%'))


def parse_yahoo(path):
    """Parse Yahoo draft analysis data, producing a DataFrame like:

               avg_round pct_drafted positions avg_pick
name
Patrick Kane         1.2        100%         R      1.4
Alex Ovechkin        1.2        100%         L      2.2
Sidney Crosby        1.2        100%         C      3.3
Jamie Benn           1.2        100%         L      4.6
Connor McDavid       1.2        100%         C      5.0
"""
    data = pd.DataFrame.from_csv(path, index_col=None)

    def correct_name(name):
        return ''.join(char for char in name if char in VALID_CHARS).title()

    data['name'] = data['name'].map(correct_name)
    data['positions'] = data['positions'].map(canonical_position)
    data['pct_drafted'] = data['pct_drafted'].map(convert_percentage)

    return data.set_index('name')


def parse_corsica(path):
    corrections = {
        'Parenteau': 'Pierre-Alexandr Parenteau',
        'Steen': 'Alexander Steen',
        'Cammalleri': 'Michael Cammalleri',
        'Edler': 'Alexander Edler',
    }

    def correct_name(name):
        # Remove period joining first/last names
        first, last = name.rsplit('.', 1)
        name = first.replace('.', '').title() + ' ' + last.title()
        name = ''.join(char for char in name if char in VALID_CHARS)

        for key, correction in corrections.items():
            if key in name:
                name = correction
                break

        return name

    data = pd.DataFrame.from_csv(path)
    data['Player'] = data['Player'].map(correct_name)
    data['Season'] = data['Season'].astype(str)

    translation = [
        ('Player', 'name'),
        ('Season', 'season'),
        ('Position', 'position'),
        ('GP', 'GP'),
        ('TOI', 'TOI'),
        ('G', 'G'),
        ('A', 'A'),
        ('P', 'P'),
        ('iSF', 'SH'),
        ('iSh%', 'SH%'),
        ('iFOW', 'FOW'),
        ('iFOL', 'FOL'),
        ('iHF', 'H'),
        ('iBLK', 'BLK'),
    ]
    return (data
            .rename(columns=dict(translation))
            .filter(list(zip(*translation))[1])
            .set_index(['name', 'position', 'season']))


def corsica_projection(data):
    # Remove season from index
    data = data.reset_index().set_index(['name', 'position'])

    season_weights = {'20152016': 4, '20142015': 2, '20132014': 1}
    data['weight'] = data.apply(lambda row: season_weights[row.season], axis=1)

    def projection(df):
        return df.mul(df.weight, axis=0).sum() / df.weight.sum()

    return data.groupby(level=(0, 1)).apply(projection).drop(['weight', 'season', 'SH%'], axis=1)


def corsica_add(*dataframes):
    """Add two corsica dataframe together. Useful for combining similar situations, e.g. 5v4 and
    5v3"""
    if len(dataframes) == 1:
        return dataframes[0]

    # Drop shooting percentage
    dropped = [df.drop(['SH%'], axis=1) for df in dataframes]

    result = dropped[0]
    for df in dropped[1:]:
        result = result.add(df, fill_value=0)

    return result


def load_corsica(datadir):
    corsica_all = parse_corsica(os.path.join(datadir, 'corsica', 'skater_3yr_all.csv'))

    corsica_5v4 = parse_corsica(os.path.join(datadir, 'corsica', 'skater_3yr_5v4.csv'))
    corsica_5v3 = parse_corsica(os.path.join(datadir, 'corsica', 'skater_3yr_5v3.csv'))
    corsica_pp = corsica_add(corsica_5v4, corsica_5v3)
    corsica_pp.rename(columns={col: 'PP' + col for col in corsica_pp.columns}, inplace=True)

    corsica_4v5 = parse_corsica(os.path.join(datadir, 'corsica', 'skater_3yr_4v5.csv'))
    corsica_3v5 = parse_corsica(os.path.join(datadir, 'corsica', 'skater_3yr_3v5.csv'))
    corsica_sh = corsica_add(corsica_4v5, corsica_3v5)
    corsica_sh.rename(columns={col: 'SH' + col for col in corsica_sh.columns}, inplace=True)

    pp_reduced = corsica_pp.filter(PP_STATS)
    sh_reduced = corsica_sh.filter(SH_STATS)
    return corsica_all.join(pp_reduced)
    # return corsica_all.join(pp_reduced).join(sh_reduced)


def join_yahoo_corsica(yahoo, corsica, indicator=False):
    data = (corsica.reset_index().set_index('name')
            .merge(yahoo, how='left', left_index=True, right_index=True,
                   indicator=indicator))
    data.positions.fillna(data.position, inplace=True)
    data.avg_round.fillna(data.avg_round.max() + 1, inplace=True)
    data.avg_pick.fillna(data.avg_pick.max() + 1, inplace=True)
    data.pct_drafted.fillna(0, inplace=True)
    data.drop(['position'], axis=1, inplace=True)

    return data


def load_data():
    datadir = os.path.join(os.path.dirname(__file__), 'data')
    yahoo = parse_yahoo(os.path.join(datadir, 'yahoo.csv'))

    corsica = load_corsica(datadir)
    projection = corsica_projection(corsica)

    return join_yahoo_corsica(yahoo, corsica), join_yahoo_corsica(yahoo, projection)


def nth_best(data, stat, n):
    return data.sort_values(stat, ascending=False).iloc[n].loc[stat]


def stats_above_replacement(data, n_players, stats=None):
    if stats is None:
        stats = STATS

    stats = list(stats)
    others = [col for col in data.columns if col not in stats]
    rl_stats = pd.Series({stat: nth_best(data, stat, n_players) for stat in stats})

    def subtract_replacement(row):
        subtracted = row.loc[stats] - rl_stats
        return pd.concat([subtracted, row.loc[others]])

    return data.apply(subtract_replacement, axis=1)


def stddev_stats(data, n_players, stats=None):
    if stats is None:
        stats = STATS

    sar = stats_above_replacement(data, n_players, stats=stats).filter(stats)
    stats_std = (sar - sar.mean()) / sar.std()

    return pd.concat([stats_std, data.filter([col for col in data.columns if col not in stats])],
                     axis=1)


def rank_by_std(data, n_players, stats=None):
    if stats is None:
        stats = STATS

    std = stddev_stats(data, n_players, stats=stats)
    std['value'] = std.filter(stats).sum(axis=1)

    std = std[['value'] + std.columns.tolist()[:-1]]

    return std.sort_values('value', ascending=False)


if __name__ == '__main__':
    corsica, projection = load_data()
    corsica.to_csv('data/skater.csv')
    projection.to_csv('data/skater_projection.csv')
