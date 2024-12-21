def select_evenly_spaced_elements(resources, num_elements=10, step=5):
    if not resources:
        return []
    selected_elements = [resources[i] for i in range(0, len(resources), step)]
    return selected_elements[:num_elements]
