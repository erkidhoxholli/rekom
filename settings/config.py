import configparser

def load_configuration(path: str):
    config = configparser.ConfigParser()
    config.read(path)
    return config

def setup_configuration(env='dev'):
    dev_config = load_configuration('settings/dev.ini')
    prod_config = load_configuration('settings/dev.ini')

    if env != 'dev':
        return prod_config

    return dev_config

