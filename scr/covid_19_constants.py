# Paths
DATA_SOURCES_PATH = '../configs/data_sources.json'
COUNTRIES_DATA_SET_PATH = '../reference_data/countries_data/ne_110m_admin_0_countries.shp'

# Pandas Settings
PANDAS_MAX_DISP_COL_ARG = 'display.max_columns'
PANDAS_MAX_DISP_COLS = 100

# Data frames constants
DF_COLS_TO_KEEP = ['Lat', 'Long', 'Province/State']
DF_COUNTRY_REGION_COL_NAME = 'Country/Region'
DF_VARIABLE_COL_NAME = 'variable'
DF_VALUE_COL_NAME = 'value'
DF_DATE_FORMAT = '%m/%d/%Y'
DF_START_YEAR = 2020
DF_START_MONTH = 1
DF_START_DAY = 22
DF_FILL_NA_WITH_STRING = 'No data'
COUNTRY_NAME_FORMAT = 'name_short'

GEO_DF_COLS_TO_KEEP = ['country', 'country_code', 'geometry']
GEO_DF_COUNTRY_COL_NAME = 'country'

DF_SUFFIXES = ('_cases', '_deaths', '_recovered')

# Visualization constants
MAP_TITLE = 'Coronavirus confirmed cases, {}'
MAP_INITIAL_TITLE = 'Coronavirus confirmed cases, {}'
BAR_PLOT_TITLE = 'Confirmed cases and number of deaths'
BAR_PLOT_XLABEL = 'Date'
BAR_PLOT_YLABEL = 'Number of persons'
BAR_PLOT_CASES_LABEL = 'Confirmed cases'
BAR_PLOT_DEATHS_LABEL = 'Number of Deaths'
BAR_PLOT_RECOVERED_LABEL = 'Number of People Recovered'
MAP_HOVER_TOOL_COUNTRY_TITLE = 'Country'
MAP_HOVER_TOOL_CASES_TITLE = 'Confirmed Cases'
BAR_PLOT_HOVER_TOOL_CASES_TITLE = 'Confirmed cases'
BAR_PLOT_HOVER_TOOL_DEATHS_TITLE = 'Number of deaths'
BAR_PLOT_HOVER_TOOL_RECOVERED_TITLE = 'Number of people recovered'
SLIDER_TITLE = 'Date'
BAR_PLOT_INIT_COUNTRY = 'Germany'
BAR_PLOT_INIT_COLS = [BAR_PLOT_INIT_COUNTRY + suffix for suffix in DF_SUFFIXES]
DROPDOWN_SELECT_TITLE = 'Select country'

PATCHES_LINE_WIDTH = 0.25
MAP_PLOT_HEIGHT = 500
MAP_PLOT_WIDTH = 800
BAR_PLOT_HEIGHT = 500
BAR_PLOT_WIDTH = 500
COLOR_BAR_WIDTH = 500
COLOR_BAR_HEIGHT = 20
COLOR_BAR_LOCATION = (0, 0)
COLOR_BAR_ORIENTATION = 'horizontal'
MAP_TOOL_BAR_LOCATION = 'below'
BAR_PLOT_TOOL_BAR_LOCATION = 'below'
BAR_PLOT_LEGEND_LOCATION = "top_left"
LAYOUT_SIZING_MODE = 'scale_width'

COLOR_MAPPER_NAN_COLOR = '#d9d9d9'
BAR_PLOT_LINE_COLOR = 'grey'
BAR_PLOT_CASES_COLOR = "#340585"
BAR_PLOT_DEATHS_COLOR = "#cf502d"
BAR_PLOT_RECOVERED_COLOR = "#568505"
COLOR_PALETTE = 'Plasma'
COLOR_PALETTE_NUMBER = 11
PATCHES_LINE_COLOR = 'black'

