def prepare_graph_data(current_report, past_reports):
    """
    Formats data for Matplotlib/Chart.js on the frontend.
    Focuses on tracking specific biomarkers over time.
    """
    # Identify common keys (tests present in both reports)
    test_history = {}
    
    # Add current data
    current_date = current_report['upload_date'].strftime("%Y-%m-%d")
    for test, value in current_report['confirmed_data'].items():
        if test not in test_history:
            test_history[test] = {"dates": [], "values": []}
        test_history[test]["dates"].append(current_date)
        test_history[test]["values"].append(value)

    # Add past data
    for report in past_reports:
        r_date = report['upload_date'].strftime("%Y-%m-%d")
        if 'confirmed_data' in report:
            for test, value in report['confirmed_data'].items():
                if test in test_history:
                    test_history[test]["dates"].insert(0, r_date)
                    test_history[test]["values"].insert(0, value)

    return test_history