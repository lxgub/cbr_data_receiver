import logging

global_logger = None


def get_logger(loglevel=logging.INFO):
    global global_logger
    if not global_logger:
        logging.basicConfig(
            format=u"%(asctime)s  %(levelname)s: %(message)s",
            level=loglevel)
        global_logger = logging
    return global_logger
