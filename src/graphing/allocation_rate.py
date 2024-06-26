# The max allocation rate is defined as the difference bewtween the heap usage at GC event A and event A+1.
# To find it, given a list of data, find the difference between values in "column"
#
from src.filter_and_group import filter_and_group
from matplotlib import pyplot as plt
import numpy as np

#       calculate_allocation_rate
#
#   Calculates and reports the allocation rate during runtime from gc information.
#   Optional parameter: percentile: If used, then calculates the specified percentile 
#                       allocation rate. If left as None, finds the mean allocation rate.
#   Optional parameter: interval_duration: Groups collected data into ranges, then either
#                       finds the mean or a percentile based on above optional param.
#
def calculate_allocation_rate(
    gc_event_dataframes,  # list of dataframes, containing gc event information. 
    group_by=None,  # A string to explain what groups to make within 1 gc_event_dataframe
    filter_by=None, # resitrctions on the data. list of tuples: (column, boolean-function) 
    labels=None,    # list of str labels to describe each gc_event_dataframe.  
    interval_duration=None, # integer or float. Creates groups of this size to find alloc rate.
    colors=None,    # colors to override 
    plot=None, #    matplotlib ax to plot onto. If none provided, one is created
    column_before="HeapBeforeGC", # Column used as information before event
    column_after= "HeapAfterGC", # Column used to find information after event
    column_timing = None, # Timing information used for X axis. List of floats or ints
    percentile = None, #  If True, and interval_duration is not None, plots the percentile
    line_graph = False # Plots as a line graph rather than a scatter plot
):  
# Filter and group data. Update colors and labels to reflect to-be-plotted data
    timestamp_groups, before_list, labels, colors, _ = filter_and_group(
        gc_event_dataframes, group_by, filter_by, labels, column_before, colors, column_timing
    )
    timestamp_groups, after_list, labels, colors, _ = filter_and_group(
        gc_event_dataframes, group_by, filter_by, labels, column_after, colors, column_timing
    )

    # if no plot is passed in, create a new plot
    if not plot:
        f, plot = plt.subplots()
    # Create a scatter plot with all data
    if len(before_list) > len(labels):
        print("Not enough labels to plot")
    if len(after_list) > len(colors):
        print("Not enough colors to plot")
    # plot the data
    for time, before_list, after_list, color, label in zip(timestamp_groups, before_list, after_list, colors, labels):
        time = list(time)
        start_times, datapoints = get_difference(list(before_list), list(after_list), time, interval_duration, percentile)
        if line_graph:
            plot.plot(start_times, datapoints, label=label, color=color)
        else:
            plot.scatter(start_times, datapoints,  label=label, color=color)
            
    plot.legend(bbox_to_anchor=(1.05, 1), loc="upper left") # Pins the legend OUTSIDE the graph. 
    #                                                        (which isnt default behavior for some reason??)
    # return a plot object to be displayed or modified
    return plot

#       get_difference
#
#   Purpose: Given a list of heap sizes before and after GC runs, with associated times, calculate the mean or nth
#   percentile rate at which the bytes are allocated, grouped by time intervals.
#   Return a list of timestamps and allocation rates.
#
def get_difference(before_list, after_list, time, interval_duration, percentile):
    times = []
    interval_start_time = time[0]
    allocated_bytes_rate= []
    rates = []
    # Create a list of all allocation rates within a time interval.
    # Then, take the mean or percentile rate from that list. Return a list of these rates, and associated timestamps
    for index in range(len(before_list) - 1):
        time_delta = (time[index + 1] - time[index])
        if time_delta != 0:
            allocated_bytes_rate.append((before_list[index + 1] - after_list[index]) / time_delta)
            elapsed_seconds = time[index + 1] - interval_start_time
            if (elapsed_seconds >= interval_duration):
                times.append(time[index]) # Set the timestamp for this time interval
                if percentile is None:
                    current_rate = np.mean(allocated_bytes_rate)
                else:
                    current_rate = np.percentile(allocated_bytes_rate, percentile)

                rates.append(current_rate)

                interval_start_time = time[index + 1]
                allocated_bytes_rate = []
    return times, rates
    
