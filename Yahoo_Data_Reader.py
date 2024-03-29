class Yahoo_Reader():
    # Create new instance: data = Yahoo_Reader('IBM')
	# Read the instance data: data.read()

    def __init__(self, symbol=None, start=None, end=None):
		import datetime, time
		from dateutil.relativedelta import relativedelta
        import pandas as pd
        self.symbol = symbol
        
		# providing start/end dates if non-available:
		if end is None:
			end  = datetime.datetime.today()
		if start is None:
			start = end - relativedelta(years=5) 

		self.start = start
		self.end = end
        
        # convert dates to unix time strings
        unix_start = int(time.mktime(self.start.timetuple()))
        day_end = self.end.replace(hour=23, minute=59, second=59)
        unix_end = int(time.mktime(day_end.timetuple()))
        
        url = 'https://finance.yahoo.com/quote/{}/history?'
        url += 'period1={}&period2={}'
        url += '&filter=history'
        url += '&interval=1d'
        url += '&frequency=1d'
        self.url = url.format(self.symbol, unix_start, unix_end)
        
    def read(self):
        import requests, re, json
        import pandas as pd
       
        r = requests.get(self.url)
        
        ptrn = r'root\.App\.main = (.*?);\n}\(this\)\);'
        txt = re.search(ptrn, r.text, re.DOTALL).group(1)
        jsn = json.loads(txt)
        df = pd.DataFrame(
                jsn['context']['dispatcher']['stores']
                ['HistoricalPriceStore']['prices']
                )
        df.insert(0, 'symbol', self.symbol)
        df['date'] = pd.to_datetime(df['date'], unit='s').dt.date
        df.set_index(u'date',inplace = True)
        df.index.rename(None, inplace = True)
        
        # drop rows that aren't prices
        df = df.dropna(subset=['close'])
        
        df = df[['symbol', 'high', 'low', 'open', 'close', 'volume', 'adjclose']]
        
        return df
    
