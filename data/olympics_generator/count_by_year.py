import csv
import json

created_cvs_list = []


def write_index_json():
  with open('../index.json', 'w') as outfile:
    json.dump(created_cvs_list, outfile)


def write_csv(year, medal_type, fieldnames, medals_per_country):
  if year is None:
    print('Invalid year -> file not written')
    return

  name = 'Olympic Games ' + year + ' (' + medal_type + ' Medals)'
  filename = 'olympics_' + year + '_' + medal_type.lower() + '.csv'

  # sort countries by sum of all medals
  sorted_by_sum = sorted(medals_per_country.items(), key=lambda x: sum(x[1].values()), reverse=True)

  print('----------------')
  print('Write ' + filename)
  print(fieldnames)
  print(sorted_by_sum)

  # get min and max value of the whole csv for the range
  max_value = float('-inf')
  # min_value = float('inf') # does not work, because we fill empty cells with 0 by default

  with open('../' + filename, 'wb') as output:
    writer = csv.DictWriter(output, fieldnames=fieldnames, restval='0', dialect='excel')
    writer.writeheader()
    for k, v in sorted_by_sum:
      values = list(v.values())
      max_value = max(max_value, max(values))
      # min_value = min(min_value, min(values))
      v['CountryCode'] = k
      writer.writerow(v)

  # build stats for index.json
  stats = dict()
  stats['name'] = name
  stats['path'] = filename
  stats['type'] = 'matrix'
  stats['size'] = [len(sorted_by_sum), len(fieldnames)-1]  # -1 = CountryCode fieldname
  stats['rowtype'] = 'Country'
  stats['coltype'] = 'Discipline'
  stats['value'] = dict(type='real', range=[0, max_value])

  created_cvs_list.append(stats)

  print('----------------')


def read_csv(medal_type='Total'):
  with open('./MedalData1.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=['Games', 'Sport', 'Event', 'Athlete(s)', 'CountryCode', 'CountryName', 'Medal', 'ResultInSeconds'], dialect='excel-tab')
    next(reader)

    last_games = None
    fieldnames = ['CountryCode']
    medals_per_country = dict()

    for row in reader:
      if row['Games'] != last_games:
        # write old year when a new year is detected
        write_csv(last_games, medal_type, fieldnames, medals_per_country)

        # clean up variables
        fieldnames = ['CountryCode']
        medals_per_country = dict()

      last_games = row['Games']
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
    write_csv(last_games, medal_type, fieldnames, medals_per_country)


read_csv('Total')
read_csv('Bronze')
read_csv('Silver')
read_csv('Gold')

write_index_json()
