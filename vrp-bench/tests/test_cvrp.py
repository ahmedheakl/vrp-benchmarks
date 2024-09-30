from real_cvrp import generate_cvrp_dataset


def test_dataset_format():
    num_customers = 10
    dataset = generate_cvrp_dataset(num_customers)
    num_instances = len(dataset["locations"])
    num_depots = 1
    to_check = [
        "locations",
        "demands",
        "num_vehicles",
        "num_depots",
        "vehicle_capacities",
        "appear_times",
    ]
    for c in to_check:
        assert c in dataset.keys(), f"{c} not found in dataset keys"

    assert dataset["locations"].shape == (num_instances, num_customers + num_depots, 2)
    assert dataset["demands"].shape == (num_instances, num_customers + num_depots)
    assert dataset["num_vehicles"].shape == (num_instances,)
    assert dataset["num_depots"] == num_depots
    assert dataset["vehicle_capacities"].shape == (num_instances,)
    assert dataset["appear_times"].shape == (num_instances, num_customers + num_depots)
