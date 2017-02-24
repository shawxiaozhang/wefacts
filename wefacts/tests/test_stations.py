# import gmplot
#
# def plot_map(gps, matched, df_isd):
#     g_map = gmplot.GoogleMapPlotter(gps[0], gps[1], 10)
#     g_map.scatter(df_isd['LAT'].values, df_isd['LON'].values, color='cornflowerblue', size=5)
#     g_map.scatter([x[1] for x in matched.values()], [x[2] for x in matched.values()], color='red', size=9)
#     g_map.scatter([gps[0]], [gps[1]], color='purple', size=9)
#     g_map.draw("tmp/station_map.html")
#
#
# def test_station_quality(country='US', state=None):
#     df_station = load_stations(country, state)
#     lats_star, lngs_star, lats_poor, lngs_poor = [], [], [], []
#     for i in xrange(len(df_station)):
#         usaf, wban, lat, lng = df_station.iloc[i][['USAF', 'WBAN', 'LAT', 'LON']]
#         if usaf == 999999 or wban == 99999:
#             lats_poor.append(lat)
#             lngs_poor.append(lng)
#         else:
#             lats_star.append(lat)
#             lngs_star.append(lng)
#     center_lat, center_lng = 1.0*sum(lats_star)/len(lats_star), 1.0*sum(lngs_star)/len(lngs_star)
#     g_map = gmplot.GoogleMapPlotter(center_lat, center_lng, 10)
#     g_map.marker(center_lat, center_lng, title='coooooooooooooooooooooool')
#     # g_map.scatter(lats_star, lngs_star, color='red', size=8)
#     # g_map.scatter(lats_poor, lngs_poor, color='blue', size=5)
#     g_map.draw('../raw/star_stations.html')