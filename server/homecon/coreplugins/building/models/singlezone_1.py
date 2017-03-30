#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pyomo.environ as pyomo

from . import model
from .... import core


"""
Notation
--------
Q : heat flow                          [W]
P : electric power                     [W]
C : thermal heat capacity            [J/K]
UA : thermal UA value                [W/K]

T : temperature                     [degC]

Subscripts
----------
_amb : ambient
_liv : living zone
_nig : night zone
_bat : bathroom
_sol : solar
_hea : heating
_int : internal

_est : estimated
_ini : initial

"""


class Singlezone_1(model.Buildingmodel):

    def __init__(self):

        self.parameters = {'C_liv': 10e6, 'UA_liv_amb': 800} 


        # state constraints are used in both models
        def state_T_liv(model, i):
            if i+1 < len(model.i):
                return model.C_liv*(model.T_liv_est[i+1]-model.T_liv_est[i])/(model.timestamp[i+1]-model.timestamp[i]) == model.UA_liv_amb*(model.T_amb[i]-model.T_liv_est[i]) + model.Q_hea[i] + model.Q_sol[i] + model.Q_int[i]
            else:
                return pyomo.Constraint.Feasible

        self.identification_constraints = {
            'state_T_liv': state_T_liv,
        }

        self.set_identification_model()
        self.set_validation_model()


    def set_identification_model(self):
        """
        """
        model = pyomo.AbstractModel()
        model.i = pyomo.Set(doc='time index')

        model.timestamp = pyomo.Param(model.i)
        model.T_amb = pyomo.Param(model.i)
        model.T_liv = pyomo.Param(model.i)

        model.Q_hea = pyomo.Param(model.i)
        model.Q_sol = pyomo.Param(model.i)
        model.Q_int = pyomo.Param(model.i)

        model.C_liv = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['C_liv'], bounds=(1e3,100e9))
        model.UA_liv_amb = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['UA_liv_amb'], bounds=(1,10000e3))
        model.T_liv_est = pyomo.Var(model.i,domain=pyomo.Reals,initialize=lambda model,i: model.T_liv[i] if not np.isnan(model.T_liv[i]) else 20.)


        # contstraints
        model.state_liv = pyomo.Constraint(model.i,rule=self.identification_constraints['state_T_liv'])
        model.state_liv_ini = pyomo.Constraint(rule=lambda model: model.T_liv_est[0] == model.T_liv[0] if not np.isnan(model.T_liv[0]) else pyomo.Constraint.Feasible)

        # objective
        model.objective = pyomo.Objective(rule=lambda model: sum( (model.T_liv[i]-model.T_liv_est[i])**2 for i in model.i if not np.isnan(model.T_liv[i])), sense=pyomo.minimize)

        self.identification_model = model


    def set_validation_model(self):
        """
        """
        model = pyomo.AbstractModel()
        model.i = pyomo.Set(doc='time index')

        model.timestamp = pyomo.Param(model.i)
        model.T_amb = pyomo.Param(model.i)
        model.T_liv = pyomo.Param(model.i)

        model.Q_hea = pyomo.Param(model.i)
        model.Q_sol = pyomo.Param(model.i)
        model.Q_int = pyomo.Param(model.i)

        model.C_liv = pyomo.Param(initialize=self.parameters['C_liv'])
        model.UA_liv_amb = pyomo.Param(initialize=self.parameters['UA_liv_amb'])
        model.T_liv_est = pyomo.Var(model.i,domain=pyomo.Reals,initialize=lambda model,i: model.T_liv[i])

        # contstraints
        model.state_liv = pyomo.Constraint(model.i,rule=self.identification_constraints['state_T_liv'])
        model.state_liv_ini = pyomo.Constraint(rule=lambda model: model.T_liv_est[0] == model.T_liv[0])

        # objective
        model.objective = pyomo.Objective(rule=lambda model: sum( (model.T_liv[i]-model.T_liv_est[i])**2 for i in model.i ), sense=pyomo.minimize)

        self.validation_model = model


    def get_identification_data(self):

        data = super().get_identification_data()

        zones = [zone for zone in core.components.find(type='zone')]

        data['T_amb'] = core.states['weather/temperature'].history(data['timestamp'])
        data['T_liv'] = np.mean( [zone.states['temperature'].history(data['timestamp']) for zone in zones], axis=0)
        data['Q_sol'] = np.sum( [zone.states['solargain'].history(data['timestamp']) for zone in zones], axis=0 )
        data['Q_int'] = np.sum( [zone.states['internalgain'].history(data['timestamp']) for zone in zones], axis=0 )
        data['Q_hea'] = np.sum( [heatemissionsystem.calculate_power(timestamp=data['timestamp']) for zone in zones for heatemissionsystem in core.components.find(type='heatemissionsystem',zone=zone)], axis=0 )


        # make sure all values are lists
        if not hasattr(data['Q_hea'],'__len__'):
            data['Q_sol'] += np.zeros(len(data['timestamp']))
        if not hasattr(data['Q_hea'],'__len__'):
            data['Q_int'] += np.zeros(len(data['timestamp']))
        if not hasattr(data['Q_hea'],'__len__'):
            data['Q_hea'] += np.zeros(len(data['timestamp']))


        return data


    def get_identification_result(self,model):

        result = super().get_identification_result(model)

        result['parameters']['C_liv'] = pyomo.value(model.C_liv)
        result['parameters']['UA_liv_amb'] = pyomo.value(model.UA_liv_amb)

        result['inputs']['timestamp'] = [int(pyomo.value(model.timestamp[i])) for i in model.i]
        result['inputs']['T_amb'] = [np.round(pyomo.value(model.T_amb[i]),2) for i in model.i]
        result['inputs']['Q_hea'] = [np.round(pyomo.value(model.Q_hea[i]),2) for i in model.i]
        result['inputs']['Q_sol'] = [np.round(pyomo.value(model.Q_sol[i]),2) for i in model.i]
        result['inputs']['Q_int'] = [np.round(pyomo.value(model.Q_int[i]),2) for i in model.i]

        result['estimates']['T_liv'] = [np.round(pyomo.value(model.T_liv_est[i]),2) for i in model.i]

        result['observations']['T_liv'] = [np.round(pyomo.value(model.T_liv[i]),2) for i in model.i]

        error = np.array([pyomo.value(model.T_liv[i]-model.T_liv_est[i]) for i in model.i])
        rmse = np.mean( error**2 )**0.5

        result['fitquality']['rmse'] = rmse
        result['fitquality']['max_error'] = np.max(np.abs(error))
        result['fitquality']['success'] = False

        if rmse < 2.0 and np.max(np.abs(error)) < 2.0:
            result['fitquality']['success'] = True


        return result


    def create_ocp_variables(self,model):
        
        # get data
        timestamps = [model.timestamp[i] for i in model.i]

        zones = core.components.find(type='zone')

        # calculate the suns position
        latitude = core.states['settings/location/latitude'].value    # N+
        longitude = core.states['settings/location/longitude'].value   # E+
        elevation = core.states['settings/location/elevation'].value

        if elevation is None:
            elevation = 0

        forecasts = [core.states['weather/forecast/hourly/{}'.format(i)] for i in range(24*7)]
        cloudcover = np.interp(timestamps,[f['timestamp'] for f in forecasts],[f['cloudcover'] for f in forecasts])
        solargain = np.zeros(len(timestamps))
        I_direct = np.zeros(len(timestamps))
        I_diffuse = np.zeros(len(timestamps))
        solar_azimuth = np.zeros(len(timestamps))
        solar_altitude = np.zeros(len(timestamps))

        for i,ts in enumerate(timestamps):
            solar_azimuth[i],solar_altitude[i] = util.weather.sunposition(latitude,longitude,elevation=elevation,timestamp=ts)
            I_direct_clearsky,I_diffuse_clearsky = util.weather.clearskyirrradiance(solar_azimuth[i],solar_altitude[i],timestamp=ts)
            I_direct[i], I_diffuse[i] = util.weather.cloudyskyirrradiance(I_direct_clearsky[i],I_diffuse_clearsky[i],cloudcover[i],solar_azimuth[i],solar_altitude[i],timestamp=ts)


        Q_sol_max_zone = {}
        Q_sol_min_zone = {}
        for zone in zones:
            # FIXME take schedules into account in min/max shading position dertermination
            shading_relativeposition = [[0.0*np.ones(len(timestamps)) for shading in core.components.find(type='shading',window=window.path)] for window in core.components.find(type='window',zone=zone.path)]
            Q_sol_max_zone[zone.path] = zone.calculate_solargain(I_direct=I_direct_cloudy,I_diffuse=I_diffuse_cloudy,solar_azimuth=solar_azimuth,solar_altitude=solar_altitude,shading_relativeposition=shading_relativeposition)

            shading_relativeposition = [[1.0*np.ones(len(timestamps)) for shading in core.components.find(type='shading',window=window.path)] for window in core.components.find(type='window',zone=zone.path)]
            Q_sol_min_zone[zone.path] = zone.calculate_solargain(I_direct=I_direct_cloudy,I_diffuse=I_diffuse_cloudy,solar_azimuth=solar_azimuth,solar_altitude=solar_altitude,shading_relativeposition=shading_relativeposition)


        Q_sol_max = sum(Q for Q in Q_sol_max_zone.values())
        Q_sol_min = sum(Q for Q in Q_sol_min_zone.values())

        model.building_Q_sol = pyomo.Var(model.i,domain=pyomo.NonNegativeReals,initialize=0,bounds=lambda model,i:(Q_sol_min[i],Q_sol_max[i]))
        model.building_Q_int = pyomo.Var(model.i,domain=pyomo.NonNegativeReals,initialize=0,bounds=lambda model,i:(0,0))
        model.building_Q_hea = pyomo.Var(model.i,domain=pyomo.NonNegativeReals,initialize=0)



    def create_ocp_constraints(self,model):

        # state estimation?  # FIXME
        T_liv_ini = np.mean( [zone.states['temperature'].history(timestamps[0]) for zone in core.components.find(type='zone')], axis=0)


        # constraints
        model.building_constraint_state_liv= pyomo.Constraint(model.i,
            rule=lambda model,i: self.parameters['C_liv']*(model.building_T_liv[i+1]-model.building_T_liv[i])/model.timestep[i] == self.parameters['UA_liv_amb']*(model.T_amb[i]-model.building_T_liv[i]) + model.building_Q_hea[i] + model.building_Q_sol[i] + model.building_Q_int[i] if i < len(model.i)-1 else pyomo.Constraint.Feasible 
        )
        model.building_constraint_state_liv_ini = pyomo.Constraint(rule=lambda model: model.building_T_liv[0] == T_liv_ini)


        zones = core.components.find(type='zone')

        Q_list = []
        for zone in zones:
            heatemissionsystems = core.components.find(type='heatemissionsystem',zone=zone.path)
            Q_list += [heatemissionsystem.ocp_variables['Q'] for heatemissionsystem in heatemissionsystems]


        model.building_constraint_Q_hea = pyomo.Constraint(model.i,rule=lambda model,i: model.building_Q_hea[i] == sum(var[i] for var in Q_list))





