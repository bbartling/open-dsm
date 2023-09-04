# Pre-project Analyst Work

Thorough analysis of electrical load profiles is a pivotal step when embarking on any electrical project, be it for a new construction, a renewable energy setup, a grid enhancement, or any venture linked to the electricity grid. This analysis serves as the cornerstone for comprehending energy consumption patterns, identifying peak demands, and gaining insights into load behaviors. Such understanding proves instrumental in optimizing energy management strategies, devising infrastructure layouts, and laying groundwork for potential expansions or integrations. Within this repository, you'll find Python scripts tailored to generate plots that play a pivotal role in shaping the Demand Side Management (DSM) strategy. These plots not only assist in visualizing the entire building's electrical power setpoint to be maintained but also establish a critical rate of change. This rate forms the foundation of an algorithm deployed within the building, aimed at detecting abrupt electricity spikes that may occur during scenarios like building startups or other occurrences.


This directory has some scripts to assist in creating line plots of power and weather:
![Alt text](/pre_project_analysis/plots/weather_power_line.png)

Highest demand day with weather:
![Alt text](/pre_project_analysis/plots/high_power_day.png)

Highest demand day found in the dataset and `Highest Rate of Change` per unit of time on minute level data:
![Alt text](/pre_project_analysis/plots/high_power_day_with_rate_of_change.png)

The 10 highest max load dates and times found in the dataset:
![Alt text](/pre_project_analysis/plots/max_load_days.png)

Creating occupied building and unoccupied building scatter plots with `scatter_plots.py`:
![Alt text](/pre_project_analysis/plots/occ_unnoc_scatter.png)

Plots for averaged electrical load profiles averages per month can be made with `monthly_load_profs.py` where then in the plots sub directory there is a `gif_maker.py` which can be used to create an animated gif image for each month to see the different electrical use patterns for each week day per month to better understand the buildings electrical usage.

![Alt text](/pre_project_analysis/plots/monthly_load_prof_animation.gif)
