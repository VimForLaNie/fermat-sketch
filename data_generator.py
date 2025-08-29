import random

def gen_data(flow_id_range, victim_flow_ratio=0.2, packet_loss_rate=0.1,packets_per_flow = 10000):
    """
    Generate a synthetic data stream with specified parameters.

    Parameters:
    - flow_id_range: Range of flow IDs (1 to flow_id_range).
    - total_packets: Total number of packets in the stream.
    - victim_flow_ratio: Ratio of packets belonging to the victim flow.
    - packet_loss_rate: Probability of packet loss for non-victim flows.

    Returns:
    - List of flow IDs representing the data stream.
    """
    victim_flow_counts = int(flow_id_range * victim_flow_ratio)
    victim_flow_ids = random.sample(range(1, flow_id_range + 1), victim_flow_counts)
    num_victim_packets = int(packets_per_flow * packet_loss_rate)

    # Generate victim flow packets
    flow = []
    for _ in range(num_victim_packets):
        flow.append(random.choice(victim_flow_ids))

    random.shuffle(flow)
    return flow