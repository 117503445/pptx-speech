from htutil import file


def get_cfg():
    return file.read_yaml("config.yaml")