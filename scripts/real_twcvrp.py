import os
from typing import Dict, Tuple, Optional
import random

import numpy as np
from tqdm import tqdm

from travel_time_generator import sample_travel_time, get_distances
from common import (
    generate_base_instance,
    save_dataset,
    load_dataset,
    visualize_instance,
)
from constants import NUM_INSTANCES, DEMAND_RANGE, MAP_SIZE


def generate_time_window(earliest_time: int, latest_time: int) -> Tuple[int, int]:
    start = random.randint(
        earliest_time, latest_time - 60
    )  # At least 60 minutes window
    end = random.randint(start + 60, latest_time)
    return start, end


def generate_twcvrp_instance(
    num_customers: int,
    num_cities: Optional[int] = None,
    num_depots: int = 1,
    is_dynamic: bool = False,
) -> Dict:
    num_cities = num_cities if num_cities else max(1, num_customers // 50)
    instance = generate_base_instance(
        num_customers, MAP_SIZE, num_cities, num_depots, DEMAND_RANGE, is_dynamic
    )

    distances = get_distances(instance["map_instance"])

    travel_times = {}
    for i in range(len(instance["locations"])):
        for j in range(len(instance["locations"])):
            if i != j:
                current_time = random.randint(
                    0, 1440
                )  # Random start time for each trip
                travel_times[(i, j)] = sample_travel_time(i, j, distances, current_time)
            else:
                travel_times[(i, j)] = 0

    time_windows = [
        generate_time_window(0, 1440) for _ in range(num_customers + num_depots)
    ]

    instance["travel_times"] = travel_times
    instance["time_windows"] = np.array(time_windows)

    return instance


def generate_twcvrp_dataset(
    num_customers: int,
    num_cities: Optional[int] = None,
    num_depots: int = 1,
    precision=np.uint16,
    is_dynamic: bool = False,
) -> Dict:
    num_cities = num_cities if num_cities else max(1, num_customers // 50)
    dataset = {
        "locations": [],
        "demands": [],
        "travel_times": [],
        "time_windows": [],
        "map_size": MAP_SIZE,
        "num_cities": num_cities,
        "num_depots": num_depots,
    }
    for _ in tqdm(
        range(NUM_INSTANCES), desc=f"Generating {num_customers} customer instances"
    ):
        instance = generate_twcvrp_instance(
            num_customers, num_cities, num_depots, is_dynamic=is_dynamic
        )
        dataset["locations"].append(instance["locations"].astype(precision))
        dataset["demands"].append(instance["demands"].astype(precision))
        instance["travel_times"] = {
            k: round(v, 2) for k, v in instance["travel_times"].items()
        }
        dataset["travel_times"].append(instance["travel_times"])
        dataset["time_windows"].append(instance["time_windows"].astype(precision))
        if is_dynamic:
            dataset["appear_times"].append(instance["appear_time"])

    return {k: np.array(v) for k, v in dataset.items()}


def main():
    customer_counts = [10, 20, 50, 100, 200, 500, 1000]
    os.makedirs("data/real_twcvrp", exist_ok=True)
    for num_customers in tqdm(customer_counts):
        dataset = generate_twcvrp_dataset(num_customers)
        save_dataset(dataset, f"data/real_twcvrp/twvrp_{num_customers}.npz")


if __name__ == "__main__":
    main()
    dataset = load_dataset("data/real_twcvrp/twvrp_10.npz")
    visualize_instance(dataset)
