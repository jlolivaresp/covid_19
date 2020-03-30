import json
import os

import pandas as pd
import geopandas as gpd
import datetime
import country_converter as coco
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, ColumnDataSource, DateSlider, \
    HoverTool, Select, Quad
from bokeh.palettes import mpl
from bokeh.io import curdoc
from bokeh.layouts import row, column

import covid_19_config_utils as config_utils
from covid_19_constants import DF_COLS_TO_KEEP, \
    DF_COUNTRY_REGION_COL_NAME, DATA_SOURCES_PATH, COUNTRIES_DATA_SET_PATH, GEO_DF_COLS_TO_KEEP, \
    GEO_DF_COUNTRY_COL_NAME, DF_VARIABLE_COL_NAME, DF_DATE_FORMAT, DF_VALUE_COL_NAME, MAP_TITLE, \
    DF_START_YEAR, DF_START_MONTH, DF_START_DAY, MAP_HOVER_TOOL_COUNTRY_TITLE, MAP_HOVER_TOOL_CASES_TITLE, \
    MAP_INITIAL_TITLE, COLOR_BAR_WIDTH, COLOR_BAR_HEIGHT, COLOR_BAR_ORIENTATION, COLOR_BAR_LOCATION, \
    MAP_PLOT_HEIGHT, MAP_PLOT_WIDTH, COLOR_PALETTE, COLOR_PALETTE_NUMBER, COLOR_MAPPER_NAN_COLOR, \
    MAP_TOOL_BAR_LOCATION, PATCHES_LINE_COLOR, PATCHES_LINE_WIDTH, SLIDER_TITLE, DF_SUFFIXES, \
    BAR_PLOT_TOOL_BAR_LOCATION, BAR_PLOT_HOVER_TOOL_CASES_TITLE, BAR_PLOT_HOVER_TOOL_DEATHS_TITLE, BAR_PLOT_TITLE, \
    BAR_PLOT_YLABEL, BAR_PLOT_XLABEL, BAR_PLOT_LINE_COLOR, BAR_PLOT_CASES_COLOR, BAR_PLOT_DEATHS_COLOR, \
    BAR_PLOT_CASES_LABEL, BAR_PLOT_DEATHS_LABEL, BAR_PLOT_LEGEND_LOCATION, BAR_PLOT_INIT_COUNTRY, BAR_PLOT_INIT_COLS, \
    DROPDOWN_SELECT_TITLE, LAYOUT_SIZING_MODE, DF_FILL_NA_WITH_STRING, COUNTRY_NAME_FORMAT, BAR_PLOT_WIDTH, \
    BAR_PLOT_HEIGHT, BAR_PLOT_RECOVERED_LABEL, BAR_PLOT_RECOVERED_COLOR, BAR_PLOT_HOVER_TOOL_RECOVERED_TITLE


# Define function that reads the config file and returns it as a dictionary.
def read_config(config_file_path: str):
    with open(config_file_path) as f:
        config_file_dict = json.load(f)
    return config_file_dict


# Define function that prepares the data for later usage.
def clean_data_frame(df: pd.DataFrame):
    cols_to_keep = [col for col in df.columns if col not in DF_COLS_TO_KEEP]
    clean_df = df[cols_to_keep]

    clean_df = clean_df.groupby(DF_COUNTRY_REGION_COL_NAME).sum().reset_index()
    clean_df[DF_COUNTRY_REGION_COL_NAME] = country_name_converter(clean_df[DF_COUNTRY_REGION_COL_NAME].to_list())

    dropped_cols_df = clean_df.copy()
    dropped_cols_df = dropped_cols_df.transpose()
    new_header = dropped_cols_df.iloc[0]
    dropped_cols_df = dropped_cols_df[1:]
    dropped_cols_df.columns = new_header

    clean_df = pd.melt(clean_df.reset_index(),
                       id_vars=DF_COUNTRY_REGION_COL_NAME,
                       value_vars=clean_df.columns[1:])

    return clean_df, dropped_cols_df


# Define function that converts the country names regardless of the format.
def country_name_converter(country_name_list: list):
    converted_country_name_list = coco.convert(names=country_name_list,
                                               to=COUNTRY_NAME_FORMAT)
    return converted_country_name_list


# Define function that formats the date of the data frames.
def date_formatter(date_string: str):
    split_date_list = date_string.split('/')
    formatted_split_date_list = split_date_list.copy()

    if split_date_list[0].startswith('0'):
        formatted_split_date_list[0] = split_date_list[0][-1]
    if split_date_list[1].startswith('0'):
        formatted_split_date_list[1] = split_date_list[1][-1]

    formatted_split_date_list[2] = split_date_list[2][2:]
    formatted_date = str.join('/', formatted_split_date_list)
    return formatted_date


# Define function that creates a json object merging two data frames.
def json_data(df_1, df_2, selected_date: str):
    date_df = df_1[df_1[DF_VARIABLE_COL_NAME] == selected_date]
    merged = df_2.merge(date_df,
                        left_on=GEO_DF_COUNTRY_COL_NAME,
                        right_on=DF_COUNTRY_REGION_COL_NAME,
                        how='left')
    merged.fillna({DF_VALUE_COL_NAME: DF_FILL_NA_WITH_STRING}, inplace=True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)

    return json_data


def main():
    # Define function to update the map plot data based on the selected date.
    def update_map_plot_source(init_date=None, slider_date=None):
        date = None

        if init_date:
            date = init_date
        elif slider_date:
            date = slider.value_as_datetime

        formatted_selected_date = date_formatter(date.strftime(DF_DATE_FORMAT))
        new_data = json_data(clean_cases_df, gdf, formatted_selected_date)
        geosource.geojson = new_data
        map_plot_fig.title.text = MAP_TITLE.format(date.strftime(DF_DATE_FORMAT))

    # Define the callback function to update the map plot.
    def update_map_plot(attr, old, new):
        selected_date = slider.value_as_datetime
        update_map_plot_source(slider_date=selected_date)

    # Define function to update the bar plot data based on the selected country.
    def update_bar_plot_source(country_name: str):
        country_name = country_name.replace(' ', '_')
        country_data_set_list = [country_name + i for i in DF_SUFFIXES]
        country_data_set_list.extend(['right', 'left'])
        df = all_countries_merged_df[country_data_set_list]

        return ColumnDataSource(data=df)

    # Define function to make the bar plot.
    def make_bar_plot(src, country_df_cols):
        # Create figure object.
        bar_plot_fig = figure(toolbar_location=BAR_PLOT_TOOL_BAR_LOCATION,
                              tools=['box_zoom', 'wheel_zoom', 'reset', 'save', 'pan'],
                              x_axis_type='datetime',
                              title=BAR_PLOT_TITLE,
                              x_axis_label=BAR_PLOT_XLABEL,
                              y_axis_label=BAR_PLOT_YLABEL,
                              plot_height=BAR_PLOT_HEIGHT,
                              plot_width=BAR_PLOT_WIDTH, )

        def make_quad_plot(col_to_plot: str, legend_label: str, color: str):
            quad = bar_plot_fig.quad(top=col_to_plot,
                                     bottom=0,
                                     left='left',
                                     right='right',
                                     color=color,
                                     line_color=BAR_PLOT_LINE_COLOR,
                                     source=src,
                                     legend_label=legend_label,
                                     alpha=0.85)
            return quad

        # Make the bar plots.
        quad_1 = make_quad_plot(country_df_cols[0], BAR_PLOT_CASES_LABEL, BAR_PLOT_CASES_COLOR)
        quad_2 = make_quad_plot(country_df_cols[2], BAR_PLOT_RECOVERED_LABEL, BAR_PLOT_RECOVERED_COLOR)
        quad_3 = make_quad_plot(country_df_cols[1], BAR_PLOT_DEATHS_LABEL, BAR_PLOT_DEATHS_COLOR)

        # Add hover tool.
        hover_2 = HoverTool(tooltips=[('Date', '@index{%F}'),
                                      (BAR_PLOT_HOVER_TOOL_CASES_TITLE, '@{}'.format(country_df_cols[0])),
                                      (BAR_PLOT_HOVER_TOOL_DEATHS_TITLE, '@{}'.format(country_df_cols[1])),
                                      (BAR_PLOT_HOVER_TOOL_RECOVERED_TITLE, '@{}'.format(country_df_cols[2]))],
                            formatters={'@index': 'datetime'},
                            renderers=[quad_1])

        bar_plot_fig.add_tools(hover_2)

        # Adjust the bar plot legend location.
        bar_plot_fig.legend.location = BAR_PLOT_LEGEND_LOCATION
        return bar_plot_fig

    # Define the callback function to update the bar plot
    def update_bar_plot(attr, old, new):
        new_src = update_bar_plot_source(dropdown.value)
        src.data = dict(new_src.data)
        country_df_cols = [dropdown.value.replace(' ', '_') + i for i in DF_SUFFIXES]
        second_column.children[0] = make_bar_plot(src, country_df_cols)

    # Define the parent path
    project_dir_path = os.path.dirname(__file__)

    # Load COVID-19 data sources dictionary
    data_sources_full_path = os.path.join(project_dir_path, DATA_SOURCES_PATH)
    covid_19_data_sources_dict = read_config(data_sources_full_path)

    # Load data frames
    cases_df = pd.read_csv(config_utils.get_covid_19_cases(covid_19_data_sources_dict))
    deaths_df = pd.read_csv(config_utils.get_covid_19_deaths(covid_19_data_sources_dict))
    recovered_df = pd.read_csv(config_utils.get_covid_19_recovered(covid_19_data_sources_dict))

    # Clean data frames
    clean_cases_df, dropped_cols_cases_df = clean_data_frame(cases_df)
    clean_deaths_df, dropped_cols_deaths_df = clean_data_frame(deaths_df)
    clean_recovered_df, dropped_cols_recovered_df = clean_data_frame(recovered_df)

    # Read shapefile using Geopandas
    shapefile_full_path = os.path.join(project_dir_path, COUNTRIES_DATA_SET_PATH)
    gdf = gpd.read_file(shapefile_full_path)[['ADMIN', 'ADM0_A3', 'geometry']]

    # Rename columns.
    gdf.columns = GEO_DF_COLS_TO_KEEP
    gdf[GEO_DF_COUNTRY_COL_NAME] = country_name_converter(gdf[GEO_DF_COUNTRY_COL_NAME].to_list())

    # Input GeoJSON source that contains features for plotting.
    initialization_date = datetime.date.today() - datetime.timedelta(days=1)
    geosource = GeoJSONDataSource(geojson=json_data(clean_cases_df, gdf, initialization_date.strftime(DF_DATE_FORMAT)))

    # Define a sequential multi-hue color palette.
    palette = mpl[COLOR_PALETTE][COLOR_PALETTE_NUMBER]

    # Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette=palette,
                                     low=clean_cases_df[DF_VALUE_COL_NAME].min(),
                                     high=clean_cases_df[DF_VALUE_COL_NAME].max(),
                                     nan_color=COLOR_MAPPER_NAN_COLOR)

    # Add hover tool for the map plot.
    hover = HoverTool(tooltips=[(MAP_HOVER_TOOL_COUNTRY_TITLE, '@{}'.format(GEO_DF_COUNTRY_COL_NAME)),
                                (MAP_HOVER_TOOL_CASES_TITLE, '@{}'.format(DF_VALUE_COL_NAME))])

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper,
                         label_standoff=8,
                         width=COLOR_BAR_WIDTH,
                         height=COLOR_BAR_HEIGHT,
                         border_line_color=None,
                         location=COLOR_BAR_LOCATION,
                         orientation=COLOR_BAR_ORIENTATION)

    # Create figure object for the bar plot.
    map_plot_fig = figure(title=MAP_INITIAL_TITLE,
                          plot_height=MAP_PLOT_HEIGHT,
                          plot_width=MAP_PLOT_WIDTH,
                          toolbar_location=MAP_TOOL_BAR_LOCATION,
                          tools=[hover, 'pan', 'box_zoom', 'wheel_zoom', 'reset', 'save'])
    map_plot_fig.xgrid.grid_line_color = None
    map_plot_fig.ygrid.grid_line_color = None

    # Add patch renderer to figure.
    map_plot_fig.patches('xs', 'ys',
                         source=geosource,
                         fill_color={'field': DF_VALUE_COL_NAME, 'transform': color_mapper},
                         line_color=PATCHES_LINE_COLOR,
                         line_width=PATCHES_LINE_WIDTH,
                         fill_alpha=1)

    # Specify layout.
    map_plot_fig.add_layout(color_bar, 'below')

    # Initialize map plot source.
    update_map_plot_source(init_date=initialization_date)

    # Make a slider object: slider.
    slider = DateSlider(title=SLIDER_TITLE,
                        start=datetime.date(DF_START_YEAR, DF_START_MONTH, DF_START_DAY),
                        end=initialization_date,
                        step=1 * 24 * 60 * 60 * 1000,
                        value=initialization_date,
                        show_value=True)
    slider.on_change(DF_VALUE_COL_NAME, update_map_plot)

    # Make merged DF from the confirmed and deaths cases.
    dropped_cols_recovered_df = dropped_cols_recovered_df.add_suffix('_recovered')
    all_countries_merged_df = dropped_cols_cases_df.merge(dropped_cols_deaths_df,
                                                          left_index=True,
                                                          right_index=True,
                                                          how='outer',
                                                          suffixes=DF_SUFFIXES[0:2]).merge(dropped_cols_recovered_df,
                                                                                           left_index=True,
                                                                                           right_index=True,
                                                                                           how='outer')

    all_countries_merged_df.index = pd.to_datetime(all_countries_merged_df.index)

    # Create datetime columns with offset so the bars of the bar plot can be wider.
    all_countries_merged_df['left'] = all_countries_merged_df.index - datetime.timedelta(days=0.5)
    all_countries_merged_df['right'] = all_countries_merged_df.index + datetime.timedelta(days=0.5)

    all_countries_merged_df_columns = []
    for c in all_countries_merged_df.columns:
        all_countries_merged_df_columns.append(c.replace(' ', '_'))

    all_countries_merged_df.columns = all_countries_merged_df_columns

    # Update bar plot data source based on selected country and make the bar plot
    src = update_bar_plot_source(BAR_PLOT_INIT_COUNTRY)
    bar_plot_fig = make_bar_plot(src, BAR_PLOT_INIT_COLS)

    # Get a list of countries to select for the Select tool and define the Select object.
    country_list = sorted(list(gdf[GEO_DF_COUNTRY_COL_NAME]))
    dropdown = Select(title=DROPDOWN_SELECT_TITLE,
                      options=country_list,
                      value=BAR_PLOT_INIT_COUNTRY)
    dropdown.on_change('value', update_bar_plot)

    # Make the layout and add it to the current document
    second_column = column(bar_plot_fig, dropdown)
    lay_out = row(column(map_plot_fig, slider), second_column)
    lay_out.sizing_mode = LAYOUT_SIZING_MODE

    curdoc().add_root(lay_out)
    show(lay_out)


main()
