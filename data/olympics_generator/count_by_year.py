import csv
import json

createdCSVs = []


def write_index_json():
  with open('../index.json', 'w') as outfile:
    json.dump(createdCSVs, outfile)


def write_csv(year, medal_type, fieldnames, medals_per_country):
  if year is None:
    print('Invalid year -> file not written')
    return

  name = 'Olympic Games ' + year + ' (' + medal_type + ' Medals)'
  filename = 'olympics_' + year + '_' + medal_type.lower() + '.csv'

  # sort countries by sum of all medals
  sortedBySum = sorted(medals_per_country.items(), key=lambda x: sum(x[1].values()), reverse=True)

  print('----------------')
  print('Write ' + filename)
  print(fieldnames)
  print(sortedBySum)

  # get min and max value of the whole csv for the range
  maxValue = float('-inf')
  # minValue = float('inf') # does not work, because we fill empty cells with 0 by default

  with open('../' + filename, 'wb') as output:
    writer = csv.DictWriter(output, fieldnames=fieldnames, restval='0', dialect='excel')
    writer.writeheader()
    for k, v in sortedBySum:
      values = list(v.values())
      maxValue = max(maxValue, max(values))
      # minValue = min(minValue, min(values))
      v['CountryCode'] = k
      writer.writerow(v)

  # build stats for index.json
  stats = dict()
  stats['name'] = name
  stats['path'] = filename
  stats['type'] = 'matrix'
  stats['size'] = [len(sortedBySum), len(fieldnames)-1]  # -1 = CountryCode fieldname
  stats['rowtype'] = 'Country'
  stats['coltype'] = 'Discipline'
  stats['value'] = dict(type='real', range=[0, maxValue])

  createdCSVs.append(stats)

  print('----------------')


def read_csv(medal_type='Total'):
  with open('./MedalData1.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=['Games', 'Sport', 'Event', 'Athlete(s)', 'CountryCode', 'CountryName', 'Medal', 'ResultInSeconds'], dialect='excel-tab')
    next(reader)

    lastGames = None
    fieldnames = ['CountryCode']
    medals_per_country = dict()

    for row in reader:
      if row['Games'] != lastGames:
        # write old year when a new year is detected
        write_csv(lastGames, medal_type, fieldnames, medals_per_country)

        # clean up variables
        fieldnames = ['CountryCode']
        medals_per_country = dict()

      lastGames = row['Games']
      country = row['CountryCode']  # short-cut

      if row['Event'] not in fieldnames:
        fieldnames.append(row['Event'])

      if row['Medal'] == medal_type or medal_type == 'Total':
        if country not in medals_per_country:
          medals_per_country[country] = dict()
          # medals_per_country[country]['CountryCode'] = country

        if row['Event'] not in medals_per_country[country]:
          medals_per_country[country][row['Event']] = 0

        medals_per_country[country][row['Event']] += 1

      # print(row['Games'], row['Event'], country, row['Medal'])

    # write the last file
    write_csv(lastGames, medal_type, fieldnames, medals_per_country)


read_csv('Total')
read_csv('Bronze')
read_csv('Silver')
read_csv('Gold')

write_index_json()
