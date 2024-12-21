def select_evenly_spaced_elements(resources, num_elements):
    step = len(resources) // num_elements
    selected_elements = [resources[i] for i in range(0, len(resources), step)]
    return selected_elements[:num_elements]
