import numpy as np

class AWFedAvgCoordinator:
    """Coordinates Federated Averaging across decentralized institutional audit nodes."""

    def __init__(self):
        # Initial global model parameters (theta weights)
        self.global_weights = {
            "theta_Fn": 0.9888,
            "theta_Ac": 0.9824,
            "theta_Rrisk": 1.0141,
            "theta_Hpen": 1.0046
        }

    def aggregate_node_updates(self, node_submissions: list) -> dict:
        """
        Aggregates local weight vectors submitted by decentralized audit nodes,
        weighted by the volume of dossiers processed (`num_samples`).
        """
        if not node_submissions:
            return self.global_weights

        total_samples = sum(node.get("num_samples", 1) for node in node_submissions)
        aggregated_weights = {key: 0.0 for key in self.global_weights.keys()}

        for node in node_submissions:
            weight_factor = node.get("num_samples", 1) / total_samples
            local_weights = node.get("local_weights", {})

            for key in aggregated_weights:
                aggregated_weights[key] += local_weights.get(key, self.global_weights[key]) * weight_factor

        # Update current global state
        self.global_weights = {k: round(v, 4) for k, v in aggregated_weights.items()}

        return {
            "status": "FEDAVG_CONSENSUS_ACHIEVED",
            "participating_nodes": len(node_submissions),
            "total_dossiers_processed": total_samples,
            "updated_global_weights": self.global_weights
        }