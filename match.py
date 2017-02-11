import pandas as pd
import numpy as np
import gmplot

# use geohashing

np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_rows', 500)


FILE_ISD = 'config/isd-history.csv'


def load_isd(end_time=20170101):
    df = pd.read_csv(FILE_ISD)
    print df.columns.values
    i_alive = df['END'] >= end_time
    i_us = df['CTRY'] == 'US'
    i_state = df['STATE'] == 'NY'
    isd_select = df.loc[i_us & i_state & i_alive]
    temp = isd_select[['STATION NAME', 'CTRY', 'STATE', 'LAT', 'LON']].sort_values(by=['LON', 'LAT'], ascending=[1, 1])
    lats = temp['LAT'].values
    lngs = temp['LON'].values

    print len(isd_select)
    print temp

    plot_map(lats, lngs)
    # with open(FILE_ISD, 'r') as f:
    #     print len(f.readlines())
    #     for line in f.readlines()[:30]:
    #         print line


def plot_map(lats, lngs):
    center_lat, center_lng = np.mean(lats), np.mean(lngs)
    g_map = gmplot.GoogleMapPlotter(center_lat, center_lng, 6)
    g_map.scatter(lats, lngs, color='cornflowerblue', size=7)
    # g_map.heatmap(heat_lats, heat_lngs)
    g_map.draw("mymap.html")


if __name__ == '__main__':
    load_isd()