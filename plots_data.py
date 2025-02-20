import calculations as calc

def getting_plots_data():
    data = calc.perform_analysis_determinate(10, 1, 1, [(3, 0)], [(100, 5)], [], [])
    print(data)

getting_plots_data()