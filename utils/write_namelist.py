#!/home/users/ban/opt/bin/python
import collections
import numpy as np
from datetime import datetime
from doms.utils import f90nml


def write_namelist(PATH_Dict, out_path, flag='WPS', **kwargs):
    DBG = 0

    # Read the namelist mode
    if flag == 'WPS':
        cmd = "{:}/utils/namelist_wps.mod".format(PATH_Dict['oms'])
        nml = f90nml.read(cmd)

        if kwargs is not None:
            for key, value in list(kwargs.items()):
                if key == 'max_dom':
                    max_dom = value
        # Use kargs to set values other than the defaults
        if kwargs is not None:
            for key, value in list(kwargs.items()):
                if (key == 'max_dom'):
                    nml['share']['max_dom'] = value
                if (key == 'start_date'):
                    if max_dom == 2:
                        nml['share']['start_date'] = [value, value]
                    elif max_dom == 3:
                        nml['share']['start_date'] = [value, value, value]

                if (key == 'end_date'):
                    if max_dom == 2:
                        nml['share']['end_date'] = [value, value]
                    elif max_dom == 3:
                        nml['share']['end_date'] = [value, value, value]
                if (key == 'interval_seconds'):
                    nml['share']['interval_seconds'] = value

                # For geogrid
                if (key == 'parent_id'):
                    nml['geogrid']['parent_id'] = value
                if (key == 'parent_grid_ratio'):
                    nml['geogrid']['parent_grid_ratio'] = value
                if (key == 'i_parent_start'):
                    nml['geogrid']['i_parent_start'] = value
                if (key == 'j_parent_start'):
                    nml['geogrid']['j_parent_start'] = value
                if (key == 'e_we'):
                    nml['geogrid']['e_we'] = value
                if (key == 'e_sn'):
                    nml['geogrid']['e_sn'] = value
                if (key == 'geog_data_res'):
                    nml['geogrid']['geog_data_res'] = value
                if (key == 'dx'):
                    nml['geogrid']['dx'] = value
                if (key == 'dy'):
                    nml['geogrid']['dy'] = value
                if (key == 'map_proj'):
                    nml['geogrid']['map_proj'] = value
                if (key == 'ref_lat'):
                    nml['geogrid']['ref_lat'] = value
                if (key == 'ref_lon'):
                    nml['geogrid']['ref_lon'] = value
                if (key == 'truelat1'):
                    nml['geogrid']['truelat1'] = value
                if (key == 'truelat2'):
                    nml['geogrid']['truelat2'] = value
                if (key == 'stand_lon'):
                    nml['geogrid']['stand_lon'] = value
                if (key == 'geog_data_path'):
                    nml['geogrid']['geog_data_path'] = value

        nml.write('{:}/namelist.wps'.format(PATH_Dict['WPS']))

        logger.info("The new namelist.wps has been generated !")

    elif flag == 'WRF':
        cmd = "{:}/utils/namelist_input.mod".format(PATH_Dict['oms'])
        nml = f90nml.read(cmd)

        if kwargs is not None:
            for key, value in list(kwargs.items()):
                if key == 'max_dom':
                    max_dom = value
        # Use kargs to set values other then the defaults
        if kwargs is not None:
            for key, value in list(kwargs.items()):
                if key == 'start_date':
                    s_date = datetime.strptime(value, '%Y-%m-%d_%H:%M:%S')
                    if max_dom == 2:
                        nml['time_control']['start_year'] = [s_date.year, s_date.year]
                        nml['time_control']['start_month'] = [s_date.month, s_date.month]
                        nml['time_control']['start_day'] = [s_date.day, s_date.day]
                        nml['time_control']['start_hour'] = [s_date.hour, s_date.hour]
                        nml['time_control']['start_minute'] = [s_date.minute, s_date.minute]
                        nml['time_control']['start_second'] = [s_date.second, s_date.second]
                    elif max_dom == 3:
                        nml['time_control']['start_year'] = \
                            [s_date.year, s_date.year, s_date.year]
                        nml['time_control']['start_month'] = \
                            [s_date.month, s_date.month, s_date.month]
                        nml['time_control']['start_day'] = \
                            [s_date.day, s_date.day, s_date.day]
                        nml['time_control']['start_hour'] = \
                            [s_date.hour, s_date.hour, s_date.hour]
                        nml['time_control']['start_minute'] = \
                            [s_date.minute, s_date.minute, s_date.minute]
                        nml['time_control']['start_second'] = \
                            [s_date.second, s_date.second, s_date.second]

                    # ----test codes ----
                    if DBG:
                        print(("Key {:} exist !".format(key)))
                        print(("s_date is {:}".format(s_date)))
                        print(("NML test : {:}".format(nml['time_control'])))

                if key == 'end_date':
                    e_date = datetime.strptime(value, '%Y-%m-%d_%H:%M:%S')
                    if max_dom == 2:
                        nml['time_control']['end_year'] = [e_date.year, e_date.year]
                        nml['time_control']['end_month'] = [e_date.month, e_date.month]
                        nml['time_control']['end_day'] = [e_date.day, e_date.day]
                        nml['time_control']['end_hour'] = [e_date.hour, e_date.hour]
                        nml['time_control']['end_minute'] = [e_date.minute, e_date.minute]
                        nml['time_control']['end_second'] = [e_date.second, e_date.second]
                    elif max_dom == 3:
                        nml['time_control']['end_year'] = \
                            [e_date.year, e_date.year, e_date.year]
                        nml['time_control']['end_month'] = \
                            [e_date.month, e_date.month, e_date.month]
                        nml['time_control']['end_day'] = \
                            [e_date.day, e_date.day, e_date.day]
                        nml['time_control']['end_hour'] = \
                            [e_date.hour, e_date.hour, e_date.hour]
                        nml['time_control']['end_minute'] = \
                            [e_date.minute, e_date.minute, e_date.minute]
                        nml['time_control']['end_second'] = \
                            [e_date.second, e_date.second, e_date.second]

                    # ----test codes ----
                    if DBG:
                        print(("Key {:} exist !".format(key)))
                        print(("e_date is {:}".format(e_date)))
                        print(("NML test : {:}".format(nml['time_control'])))

                if ('s_date' in locals()) and ('e_date' in locals()):
                    run_date = e_date - s_date
                    nml['time_control']['run_days'] = run_date.days
                    nml['time_control']['run_hours'] = run_date.seconds // 3600
                    nml['time_control']['run_minutes'] = (run_date.seconds // 60) % 60
                    nml['time_control']['run_seconds'] = run_date.seconds % 60

                    # ----test codes ----
                    if DBG:
                        print(("run_date is {:}".format(run_date)))
                        print(("NML test : {:}".format(nml['time_control'])))

                # -- Set the time_control from 'start_year'../'end_year'../'run_days'.. --
                time_keywords = np.asarray(
                    ['start_year', 'start_month', 'start_day', 'start_hour', 'start_minute', 'start_second',
                     'end_year', 'end_month', 'end_day', 'end_hour', 'end_minute', 'end_second',
                     'run_days', 'run_hours', 'run_minutes', 'run_seconds',
                     'interval_seconds'])
                if np.any(key == time_keywords):
                    nml['time_control'][key] = value
                    print(("NML test : {:}".format(nml['time_control'])))

                # -- Set domains --
                if (("time_step" in key) or ("e_" in key) or ("_id" in key) or
                        ("num_metgrid_" in key) or ("_parent_start" in key)):
                    nml['domains'][key] = value

                domain_keywords = np.asarray(
                    ['max_dom', 'p_top_requested', 'dx', 'dy', 'parent_grid_ratio', 'parent_time_step_ratio'])
                if np.any(key == domain_keywords):
                    nml['domains'][key] = value

        nml.write("{:}/namelist.input".format(PATH_Dict["WRF"]))
        logger.info("The new namelist.input has been generated !")

    # Read the namelist mode
    elif flag == 'FVCOM':
        cmd = "{:}/utils/FVCOM_run.nml".format(PATH_Dict['oms'])
        nml = f90nml.read(cmd)

        # Use kargs to set values other than the defaults
        if kwargs is not None:
            for key, value in list(kwargs.items()):
                if key == 'case_title':
                    nml['NML_CASE']['CASE_TITLE'] = value
                if key == 'start_date':
                    nml['nml_case']['start_date'] = value
                    nml['NML_NETCDF']['NC_FIRST_OUT'] = value
                if key == 'end_date':
                    nml['NML_CASE']['END_DATE'] = value

                if key == 'input_dir':
                    nml['NML_IO']['INPUT_DIR'] = value
                if key == 'output_dir':
                    nml['NML_IO']['OUTPUT_DIR'] = value

                if key == 'time_step':
                    nml['NML_INTEGRATION']['EXTSTEP_SECONDS'] = value
                if key == 'isplit':
                    nml['NML_INTEGRATION']['ISPLIT'] = value

                if key == 'wind_file':
                    nml['NML_SURFACE_FORCING']['WIND_FILE'] = value
                    nml['NML_SURFACE_FORCING']['HEATING_FILE'] = value
                    nml['NML_SURFACE_FORCING']['PRECIPITATION_FILE'] = value
                    nml['NML_SURFACE_FORCING']['AIRPRESSURE_FILE'] = value

                if key == 'nesting_wave_file':
                    nml['NML_NESTING_WAVE']['NESTING_FILE_NAME_WAVE'] = value

        nml.write("{:}/NCS_run.nml".format(out_path))
        logger.info("The new Casename_run.nml has been generated !")
    elif flag == 'Tide':
        nml = f90nml.Namelist(kwargs)
        nml.write("{:}/NCS_run.nml".format(out_path))
        logger.info("The new Casename_run.nml has been generated !")
    return
