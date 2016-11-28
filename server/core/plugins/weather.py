#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import urllib.request
import json
import concurrent.futures

from .. import plugin

class Weather(plugin.Plugin):
    """
    Class to control the HomeCon weather functions
    
    """

    def initialize(self):

        # create a thread pool executor for loading api data
        self.executor = concurrent.futures.ThreadPoolExecutor(7)

        # add settings states
        self._states.add('settings/weather/service', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})
        self._states.add('settings/weather/apikey', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})
        self._states.add('weather/forecast/lastupdate', config={'type': 'number', 'quantity':'', 'unit':'','label':'', 'description':''})


        # add forecast states
        for i in range(7):
            self._states.add('weather/forecast/daily/{}'.format(i), config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        
        for i in range(24*7):
            self._states.add('weather/forecast/hourly/{}'.format(i), config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})


        # load the forecast
        self.forecast()

        logging.debug('Weather plugin Initialized')


    def load_url(self, url):
        """
        method for loading urls to be used in a thread pool executor

        """
        with urllib.request.urlopen(url, timeout=60) as conn:
            return conn.read()


    def forecast(self):
        """
        Loads a forecast from a webservice and schedules itself to run again an hour later

        """

        # schedule loading forecasts in an hour
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()

        dt_when = (dt_now + datetime.timedelta(hours=1)).replace(minute=1,second=0,microsecond=0)

        timestamp_now = (dt_now-dt_ref).total_seconds()
        timestamp_when = (dt_when-dt_ref).total_seconds()

        when = self._loop.time() + timestamp_when - timestamp_now

        self._loop.call_at(when,self.forecast)


        # check the last load time to avoid frequent loading upon restarts
        if self._states['weather/forecast/lastupdate'].value is None or self._states['weather/forecast/lastupdate'].value < timestamp_now-3599:

            # load the forecast
            if self._states['settings/weather/service'].value == 'darksky':
                self.darksky_forecast()

            self._states['weather/forecast/lastupdate'].value = timestamp_now

    def darksky_forecast(self):
        """
        Loads a forecast from darksky.net
        """

        
        # create a list of times to poll
        now = datetime.datetime.utcnow().replace( second=0, microsecond=0)
        timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

        timestamplist = [timestamp+i*24*3600 for i in range(7)]
        hourlyweatherforecast = []
        dailyweatherforecast = []

        future_to_timestamp = {}
        for timestamp in timestamplist:
            url = 'https://api.darksky.net/forecast/{}/{},{},{}?units=si'.format(self._states['settings/weather/apikey'].value,self._states['settings/location/latitude'].value,self._states['settings/location/longitude'].value,timestamp)
            future = self.executor.submit(self.load_url, url)
            future_to_timestamp[future] = timestamp 

        for future in concurrent.futures.as_completed(future_to_timestamp):
            timestamp = future_to_timestamp[future]

            try:
                response = json.loads(future.result().decode('utf-8'))

                # hourly values
                for data in response['hourly']['data']:
                    forecast = {}
                    forecast['timestamp'] = data['time']
                    forecast['temperature'] = data['temperature']
                    forecast['pressure'] = data['pressure']
                    forecast['humidity'] = data['humidity']
                    forecast['icon'] = data['icon']
                    forecast['clouds'] = data['cloudCover']
                    forecast['wind_speed'] = data['windSpeed']
                    forecast['wind_direction'] = data['windBearing']
                    try:
                        forecast['precipitation_intensity'] = data['precipIntensity']
                        forecast['precipitation_probability'] = data['precipProbability']
                    except:
                        forecast['precipitation_intensity'] = 0
                        forecast['precipitation_probability'] = 0

                    hourlyweatherforecast.append(forecast)
            
                # daily values
                data = response['daily']['data'][0]
                forecast = {}
                forecast['timestamp'] = data['time']
                forecast['temperature_day'] = data['temperatureMax']
                forecast['temperature_night'] = data['temperatureMin']
                forecast['pressure'] = data['pressure']
                forecast['humidity'] = data['humidity']
                forecast['icon'] = data['icon']
                forecast['clouds'] = data['cloudCover']
                forecast['wind_speed'] = data['windSpeed']
                forecast['wind_direction'] = data['windBearing']
                try:
                    forecast['precipitation_intensity'] = data['precipIntensity']
                    forecast['precipitation_probability'] = data['precipProbability']
                except:
                    forecast['precipitation_intensity'] = 0
                    forecast['precipitation_probability'] = 0


                dailyweatherforecast.append(forecast)

            except Exception as e:
                logging.error('Could not load data from Darksky.net: {}'.format(e))



        # set the states
        for i,forecast in enumerate(hourlyweatherforecast[:24*7]):
            self._states['weather/forecast/hourly/{}'.format(i)].value = forecast

        for i,forecast in enumerate(dailyweatherforecast[:7]):
            self._states['weather/forecast/daily/{}'.format(i)].value = forecast

        logging.debug('Weather forecast loaded from darksky.net')


