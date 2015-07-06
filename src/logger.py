__author__ = 'Reem'

import logging

# the logging

def init_log(log_file):
    # logging.basicConfig(level=logging.INFO,
    #                     #format='%(message)s',
    #                     format='%(asctime)s\t%(message)s',
    #                     datefmt='%d-%m-%Y %H:%M:%S',
    #                     filename=log_file,
    #                     filemode='w')
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s',
                        filename=log_file,
                        filemode='w')
    # add a header to the log (for now)
    message("operation", "type", "id", "position", "data") #no new id for now

def message(operation, type, id, position, data=None, new_id=None):
    #todo some check that the log file already exists
    #ignore the data for now, we don't need it
    logging.info('%s\t%s\t%s\t%s', operation, type, id, position)
    return