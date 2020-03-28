def get_covid_19_cases(config_file_dict: dict):
    return config_file_dict.get('covid_19_cases')


def get_covid_19_deaths(config_file_dict: dict):
    return config_file_dict.get('covid_19_deaths')


def get_covid_19_recovered(config_file_dict: dict):
    return config_file_dict.get('covid_19_recovered')
