import csv

def writeCSV(year, medalType, fieldnames, medalsPerCountry):
  if year is None:
    print('Invalid year -> file not written')
    return

  filename = year + '_' + medalType + '.csv'
  # sort countries by sum of all medals
  sortedBySum = sorted(medalsPerCountry.items(), key=lambda x: sum(x[1].values()), reverse=True)

  print('----------------')
  print('Write ' + filename)
  print(fieldnames)
  print(sortedBySum)

  with open('../' + filename, 'wb') as output:
    writer = csv.DictWriter(output, fieldnames=fieldnames, restval='0', dialect='excel-tab')
    writer.writeheader()
    for k, v in sortedBySum:
      v['CountryCode'] = k
      writer.writerow(v)

  print('----------------')

def readCSV(medalType = 'Total'):
  with open('./MedalData1.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=['Games','Sport','Event','Athlete(s)','CountryCode','CountryName','Medal','ResultInSeconds'], dialect='excel-tab')
    next(reader)

    lastGames = None
    fieldnames = ['CountryCode']
    medalsPerCountry = dict()

    for row in reader:
      if row['Games'] != lastGames:
        # write old year when a new year is detected
        writeCSV(lastGames, medalType, fieldnames, medalsPerCountry)

        # clean up variables
        fieldnames = ['CountryCode']
        medalsPerCountry = dict()

      lastGames = row['Games']
      country = row['CountryCode'] # short-cut

      if row['Event'] not in fieldnames:
        fieldnames.append(row['Event'])

      if row['Medal'] == medalType or medalType is 'Total':
        if country not in medalsPerCountry:
          medalsPerCountry[country] = dict()
          #medalsPerCountry[country]['CountryCode'] = country

        if row['Event'] not in medalsPerCountry[country]:
          medalsPerCountry[country][row['Event']] = 0

        medalsPerCountry[country][row['Event']] += 1

      #print(row['Games'], row['Event'], country, row['Medal'])

    # write the last file
    writeCSV(lastGames, medalType, fieldnames, medalsPerCountry)

readCSV('Total')
readCSV('Bronze')
readCSV('Silver')
readCSV('Gold')
