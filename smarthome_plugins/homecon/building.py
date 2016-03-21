#!/usr/bin/python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import numpy as np
import time

logger = logging.getLogger('')


class Zone():
	def __init__(self,homecon,item):
		self.homecon = homecon
		self.item = item
		self.item.conf['homeconobject'] = self

		# add all zone windows
		self.windows = []
		for item in self.homecon.find_item('window',parent=self.item):
			self.windows.append( Window(homecon,self,item) )

		# add all zone emission systems
		self.emissionsystems = []
		for item in self.homecon.find_item('emission',parent=self.item):
			self.emissionsystems.append( Emission(homecon,self,item) )

		# find all zone temperature measurement
		self.temperaturemeasurements = []
		for item in self.homecon.find_item('temperature',parent=self.item):
			self.temperaturemeasurements.append(item)

		# set the reference quantities
		self.temperature = self.item.temperature
		self.airquality = self.item.airquality
		self.solargains = self.item.solargains
		self.internalgains = self.item.internalgains


		self.raincountdown = -1
		

	def irradiation_max(self,average=False):
		"""
		calculates the maximum zone irradiation
		"""
		return sum([window.irradiation_max(average=average) for window in self.windows])

	def irradiation_min(self,average=False):
		"""
		calculates the minimum zone irradiation
		"""
		return sum([window.irradiation_min(average=average) for window in self.windows])	

	def irradiation_est(self,average=False):
		"""
		calculates the estimated zone irradiation and sets it to the appropriate item
		"""
		value = sum([window.irradiation_est(average=average) for window in self.windows])

		# set the irradiation item
		self.irradiation( value )
		return value


	def shading_control(self):
		"""
		Function tries to control the shading so the actual solar gains to the zone match the setpoint
		"""

		irradiation_set = self.irradiation.setpoint()

		#logger.warning( 'automatic shading control for zone: {0}, setpoint: {1:.1f}'.format( self.item.id(),self.irradiation.setpoint() )  )

		# sort all windows based on their averaged open irradiation
		windows = sorted(self.windows, key=lambda w: w.irradiation_open(average=True) , reverse=True)

		tolerance = 100


		# rain countdown
		if self.homecon.item.weather.current.precipitation():
			self.raincountdown = 15
		else:
			self.raincountdown = self.raincountdown-1
		
		# set position min/max values
		pos_min = []
		pos_max = []
		for window in windows:
			if window.shading != None:
				if self.raincountdown > 0 and ('open_when_raining' in window.shading.conf):
					pos_min.append( 0 )
					pos_max.append( 0 )
				elif window.shading.closed():
					pos_min.append( 1 )
					pos_max.append( 1 )
				elif (not window.shading.auto()) or window.shading.override():
					pos_min.append( window.shading_value2pos() )
					pos_max.append( window.shading_value2pos() )
				else:
					pos_min.append( 0 )
					pos_max.append( 1 )	
			else:
				pos_min.append(0)
				pos_max.append(0)

		# get old shading positions updated them with the new extreme values
		pos_old = []
		pos_new = []
		irradiation_open = []
		irradiation_closed = []
		for window,pmin,pmax in zip(windows,pos_min,pos_max):
			if window.shading != None:
				p = window.shading_value2pos()
				p = min(pmax,max(pmin,p))				
				pos_old.append( p )
				pos_new.append( p )
			else:
				pos_old.append(0)
				pos_new.append(0)
		
			irradiation_open.append( window.irradiation_open(average=True) )
			irradiation_closed.append( window.irradiation_closed(average=True) )

				
		# calculate the irradiation with the old shading positions updated with the current min and max
		irradiation = sum([(1-p)*irr_open+(p)*irr_closed for p,irr_open,irr_closed in zip(pos_old,irradiation_open,irradiation_closed)])

		# calculate new shading positions
		lower_shading = False
		raise_shading = False
		if irradiation < tolerance:
			# set all shades to their minimum value
			pos_new = pos_min
			#logger.warning('go to minimum')
		else:
			if irradiation < irradiation_set-tolerance:
				# raise more shades
				raise_shading = True
				irradiation_set_move = irradiation_set+0.75*tolerance
				#logger.warning('raising')
			elif irradiation > irradiation_set+tolerance:
				# lower more shades
				lower_shading = True
				irradiation_set_move = irradiation_set-0.75*tolerance
				#logger.warning('lowering')
			else: 
				# do nothing
				pass
				#logger.warning('do nothing')

			if lower_shading or raise_shading:
				if lower_shading:
					windowloop = enumerate(windows)
				else:
					windowloop = enumerate(reversed(windows))

				for i,window in windowloop:

					# maximum and minimum possible irradiation by changing this window only
					irradiation_max = irradiation - ((1-pos_old[i])*irradiation_open[i]+(pos_old[i])*irradiation_closed[i]) + ((1-pos_min[i])*irradiation_open[i]+(pos_min[i])*irradiation_closed[i])
					irradiation_min = irradiation - ((1-pos_old[i])*irradiation_open[i]+(pos_old[i])*irradiation_closed[i]) + ((1-pos_max[i])*irradiation_open[i]+(pos_max[i])*irradiation_closed[i])

					# to avoid devisions by zero
					if abs(irradiation_max-irradiation_min) > 1:
						pos_new[i] = (irradiation_max-irradiation_set_move)/(irradiation_max-irradiation_min)
						pos_new[i] = min(pos_max[i],max(pos_min[i],pos_new[i]))
			
					#logger.warning('window: {0}, pos_old: {1:.1f}, irr: {2:.0f}, irr_max:{3:.0f}, irr_min:{4:.0f}, pos_new: {5:.1f}'.format(window.item.id(),pos_old[i],irradiation,irradiation_max,irradiation_min,pos_new[i]))

					# update the irradiation value
					irradiation = irradiation - ((1-pos_old[i])*irradiation_open[i]+(pos_old[i])*irradiation_closed[i]) +  ((1-pos_new[i])*irradiation_open[i]+(pos_new[i])*irradiation_closed[i])

					if abs(irradiation - irradiation_set_move) < 0.1*tolerance:
						break



		# set shading positions which are auto and not override
		for i,window in enumerate(windows):
			if window.shading != None:
				# only actually set the shading position if
				# it is set to closed
				condition1 = window.shading.closed()
				# it is set to open when raining and it rains
				condition2 = self.raincountdown>0 and ('open_when_raining' in window.shading.conf)
				# auto is set and override is not set and if the change is larger than 20% or it is closed or open
				condition3 = window.shading.auto() and (not window.shading.override()) and (abs(pos_new[i]-pos_old[i]) > 0.2 or pos_new[i]==0 or pos_new[i]==1)
				if condition1 or condition2 or condition3:
					window.shading.value( window.shading_pos2value(pos_new[i]) )
					# wait for 0.05s as in my experience when executed on a fast computer eibd can't follow and some teleggrams dissappear
					time.sleep(0.05)
		
		# estimate the new value for irradiation and set it
		self.irradiation_est()

		#logger.warning(  ', '.join(['{0} pos: {1:.1f} min: {2:.1f} max:{3:.1f} irr: {4:.1f}'.format(w.item.id(),p,pmin,pmax,w.irradiation_est()) for w,p,pmin,pmax in zip(windows,pos_new,pos_min,pos_max)])  )
		#logger.warning( 'estimate: {2:.1f}'.format( self.item.id(),self.irradiation.setpoint(),self.irradiation_est(average=True) )  )		



class Window():
	def __init__(self,homecon,zone,item):
		self.homecon = homecon
		self.zone = zone
		self.item = item
		self.item.conf['homeconobject'] = self

		self.shading = None
		for item in self.homecon._sh.find_children(self.item, 'homeconitem'):
			if item.conf['homeconitem']== 'shading':
				self.shading = item
				self.shading.conf['homeconobject'] = self
		

	def irradiation_open(self,average=False):
		"""
		Returns the irradiation through a window when the shading is open
		"""
		return float(self.item.conf['area'])*float(self.item.conf['transmittance'])*self.homecon.weather.incidentradiation(surface_azimuth=float(self.item.conf['orientation'])*np.pi/180,surface_tilt=float(self.item.conf['tilt'])*np.pi/180,average=average)


	def irradiation_closed(self,average=False):
		"""
		Returns the irradiation through a window when the shading is closed if there is shading
		"""
		if self.shading != None:
			shading = float(self.shading.conf['transmittance'])
		else:
			shading = 1.0
		return self.irradiation_open(average=average)*shading

	def irradiation_max(self,average=False):
		"""
		Returns the maximum amount of irradiation through the window
		It checks the closed flag indicating the shading must be closed
		And the override flag indicating the shading position is fixed
		"""

		if self.shading != None:
			if self.shading.closed():
				return self.irradiation_closed(average=average)
			elif self.shading.override() or not self.shading.auto():
				return self.irradiation_est(average=average)
			else:
				return self.irradiation_open(average=average)
		else:
			return self.irradiation_open(average=average)

	def irradiation_min(self,average=False):
		"""
		Returns the minimum amount of irradiation through the window
		It checks the closed flag indicating the shading must be closed
		And the override flag indicating the shading position is fixed
		"""
		if self.shading != None:
			if self.shading.override() or not self.shading.auto():
				return self.irradiation_est(average=average)
			else:
				return self.irradiation_closed(average=average)
		else:
			return self.irradiation_open(average=average)

	def irradiation_est(self,average=False):
		"""
		Returns the estimated actual irradiation through the window
		"""
		if self.shading != None:
			shading = (self.shading.value()-float(self.shading.conf['open_value']))/(float(self.shading.conf['closed_value'])-float(self.shading.conf['open_value']))
			return self.irradiation_open(average=average)*(1-shading) + self.irradiation_closed(average=average)*shading
		else:
			return self.irradiation_open(average=average)

	def shading_override(self):
		self.shading.override(True)
		self.shading.closed(False)
		logger.warning('Overriding %s control'%self.shading)

		# release override after 4h
		def release():
			self.shading.override(False)
			logger.warning('Override of %s control released'%self.shading)
		
		threading.Timer(4*3600,release).start()

	def shading_value2pos(self,value=None):
		
		if self.shading != None:
			if value==None:
				value = self.shading.value()

			return (value-float(self.shading.conf['open_value']))/(float(self.shading.conf['closed_value'])-float(self.shading.conf['open_value']))
		else:
			return 0

	def shading_pos2value(self,pos):

		if self.shading != None:
			return float(self.shading.conf['open_value'])+pos*(float(self.shading.conf['closed_value'])-float(self.shading.conf['open_value']))
		else:
			return 0



class Emission():
	def __init__(self,homecon,zone,item):
		self.homecon = homecon
		self.zone = zone
		self.item = item
		self.item.conf['homeconobject'] = self
