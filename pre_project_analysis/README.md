Pre-project analysis of electrical load profiles is crucial when planning any electrical project, whether it's for a new building, a renewable energy installation, a grid upgrade, or any other application that interacts with the electricity grid. The analysis helps in understanding the energy consumption patterns, peak demands, and the overall behavior of loads. This assists in optimizing the energy management, designing infrastructure, and planning for potential expansions or integrations. This directory contains Python scripts to create plots to help put together a plan in the DSM strategy. The plots would help deptict a whole building electrical power setpoint to maintain and also a critical rate of change for an algorithm that would run at the building to detect a spike in electricity that can occur during building startup or other scenorio's.


This directory has some scripts to assist in creating line plots of power and weather:
![Alt text](/pre_project_analysis/plots/weather_power_line.png)

Highest demand day found in the dataset with `Highest Rate of Change` per unit of time:
![Alt text](/pre_project_analysis/plots/high_power_day.png)

The 10 highest max load dates and times found in the dataset:
![Alt text](/pre_project_analysis/plots/max_load_days.png)

Creating occupied building and unoccupied building scatter plots with `scatter_plots.py`:
![Alt text](/pre_project_analysis/plots/occ_unnoc_scatter.png)

Plots for averaged electrical load profiles averages per month can be made with `monthly_load_profs.py` where then in the plots sub directory there is a `gif_maker.py` which can be used to create an animated gif image for each month to see the different electrical use patterns for each week day per month to better understand the buildings electrical usage.

![Alt text](/pre_project_analysis/plots/monthly_load_prof_animation.gif)
