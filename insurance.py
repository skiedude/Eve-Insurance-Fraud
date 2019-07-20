from esipy import EsiApp
from esipy import EsiClient
from string import capwords

import argparse
import shelve
import config
import json
import os
import sys

# -----------------------------------------------------------------------
# Args 
# -----------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Check for Profitable Insurance Frauds')
parser.add_argument('--region', action="store", dest='reg_name', default=10000002, help="Qouted Region Name ie: 'the forge'")
parser.add_argument('--list-regions', action="store", dest='list_regions', default=None, help="List all regions")
args = parser.parse_args()

# -----------------------------------------------------------------------
# ESIPY Init
# -----------------------------------------------------------------------
esiapp = EsiApp().get_latest_swagger

# -----------------------------------------------------------------------
# ESICLIENT Init
# -----------------------------------------------------------------------
esiclient = EsiClient(
    headers={'User-Agent': config.ESI_USER_AGENT}
)

# -----------------------------------------------------------------------
# Pull down market data by region 
# -----------------------------------------------------------------------
def get_market_data(cache, r_id):
  try:
    market = esiapp.op['get_markets_region_id_orders'](
      region_id = r_id,
      page = 1,
      order_type = 'sell',
    )
    res = esiclient.head(market)

    if res.status == 200:
      number_of_pages = res.header['X-Pages'][0]
      operations = []
      market_data = []
      for page in range(1, int(number_of_pages) + 1):
        operations.append(
          esiapp.op['get_markets_region_id_orders'](
            region_id = r_id,
            page = page,
            order_type = 'sell',
          )         
        )
      response = esiclient.multi_request(operations, raw_body_only=True)
      for resp in response:
        json_response = json.loads(resp[1].raw)
        market_data += json_response
      if cache.has_key('insurance_data'):
        data = cache['insurance_data']
        dicter = {}
        type_ids = list(data.keys())
        for entry in market_data:
          if entry['type_id'] in type_ids:
            if entry['type_id'] not in dicter:
              dicter[entry['type_id']] = []
            dicter[entry['type_id']].append(entry)
        market_ids = list(dicter.keys())
        cache[str(r_id) + '_market_ids'] = market_ids
        for m_id in market_ids:
          sorted_id =  sorted(dicter[m_id], key = lambda i: i['price'])
          cache[str(r_id) + '_' + str(m_id)] = sorted_id

  except Exception as e:
    print('Failed to fetch market data')
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
    sys.exit(1)


# -----------------------------------------------------------------------
# Populate Insurance to file cache from ESI 
# -----------------------------------------------------------------------
def get_insurance(cache):
  try:
    platinum_levels = {}
    insurance = esiapp.op['get_insurance_prices']()
    response = esiclient.request(insurance, raw_body_only=True)
    json_response = json.loads(response.raw)

    for val in json_response:
      for level in val['levels']:
        if level['name'] == 'Platinum':
          platinum_levels[val['type_id']] = level
          
    cache['insurance_data'] = platinum_levels
  except Exception as e:
    print('Failed to cache insurance data')
    print(e)
    sys.exit(1)

# -----------------------------------------------------------------------
# Populate Insurance to file cache from ESI 
# -----------------------------------------------------------------------
def get_regions(cache):
  try:
    regions = {}
    esi_regions = esiapp.op['get_universe_regions']()
    response = esiclient.request(esi_regions, raw_body_only=True)
    json_regions = json.loads(response.raw)

    for reg in json_regions:
      esi_region = esiapp.op['get_universe_regions_region_id'](
        region_id = reg,
      )
      response = esiclient.request(esi_region, raw_body_only=True)
      json_region = json.loads(response.raw)
      regions[json_region['region_id']] = json_region['name'] 
    cache['regions'] = regions

  except Exception as e:
    print('Failed to cache regions')
    print(e)
    sys.exit(1)

# -----------------------------------------------------------------------
# Run script 
# -----------------------------------------------------------------------
def runner(reg_name, list_regions):
  cache = shelve.open(config.CACHE_FILE, flag='c')
  insurance = None
    
  if not cache.has_key('insurance_data'):
    print('Insurance data was not cached, getting it')
    get_insurance(cache)
    
  if not cache.has_key('regions'):
    print('Region data was not cached, getting it')
    get_regions(cache)

  regions = cache['regions']

  if list_regions is not None:
    print(",".join(regions.values()))
    sys.exit(0)
      
  try:
    r_id = regions.keys()[regions.values().index(capwords(reg_name))]
    print('Looking up prices in Region: ' + capwords(reg_name))
  except:
    print('Unknown Region')
    sys.exit(1)

  try:
    insurance = cache['insurance_data']
    get_market_data(cache, r_id)

    for t_id in cache[str(r_id) + '_market_ids']:
      total_profit = 0
      total_volume_remaining = 0
      min_price = 0
      max_price = 0
      string_id = str(t_id)
      cached = cache[str(r_id) + '_' + string_id]
      min_price = cached[0]['price']
      for item in cached:
        profit = (insurance[t_id]['payout'] - (item['price'] + insurance[t_id]['cost']))
        profit = profit * item['volume_remain']
        if profit > 0:
          total_profit += profit
          total_volume_remaining += item['volume_remain']
          max_price = item['price']
        else:
          break
      if total_profit > 0:
        type_id_lookup = esiapp.op['get_universe_types_type_id'](
            type_id = t_id,
        )
        response = esiclient.request(type_id_lookup)
        print('Ship: ' + response.data['name'] + '\n' + ' Total Profit: ' + '{:,}'.format(total_profit) + '\n' + ' Total Volume Remaining: ' + str(total_volume_remaining) + '\n' + ' Min price: ' + '{:,}'.format(min_price) + '\n' + ' Max Price: ' + '{:,}'.format(max_price) + '\n')


  except Exception as e:
    print('Failed to get cached insurance data')
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

  finally:
    cache.close()

# ---------------------
# Run with args
# ---------------------
runner(args.reg_name, args.list_regions)
