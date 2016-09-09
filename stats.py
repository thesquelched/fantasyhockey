import os.path
import pandas as pd


def canonical_position(raw):
    return ','.join(sorted(raw.translate(raw.maketrans('', '', ' W')).split(',')))


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
    data = pd.DataFrame.from_csv(path, index_col='name')
    data['positions'] = data['positions'].map(canonical_position)

    return data


def parse_corsica(path):
    data = pd.DataFrame.from_csv(path)
    data['Player'] = data['Player'].map(lambda name: name.replace('.', ' ').title())
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

    return corsica_all.join(corsica_pp.drop(['PPGP', 'PPFOW', 'PPFOL'], axis=1))


def join_yahoo_corsica(yahoo, corsica):
    data = corsica.reset_index().set_index('name').join(yahoo)
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


if __name__ == '__main__':
    corsica, projection = load_data()
    corsica.to_csv('data/corsica/skater.csv')
    projection.to_csv('data/projection.csv')
