from gpxcsv import gpxtolist
gpx_list = gpxtolist('/Users/hank.zhao/Developer/gpx2fit/data/origin/Test_Run.gpx')

#if you have pandas
import pandas as pd
df = pd.DataFrame(gpx_list)
csv= df.to_csv("/Users/hank.zhao/Developer/gpx2fit/data/result.csv")
print(csv)
