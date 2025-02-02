import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

class CustomQuantumKernel:
    def __init__(self, feature_dimension):
        self.feature_dimension = feature_dimension

    def construct_feature_map(self, x):
        """Constructs a quantum circuit (feature map) encoding the input data."""
        qc = QuantumCircuit(self.feature_dimension)
        for i in range(self.feature_dimension):
            qc.h(i)  # Apply a Hadamard gate to put qubits in superposition
            qc.rz(x[i], i)  # Apply rotation based on the input feature
        return qc

    def compute_kernel_matrix(self, X):
        """Compute the kernel matrix using statevector overlaps."""
        kernel_matrix = np.zeros((len(X), len(X)))

        for i in range(len(X)):
            for j in range(len(X)):
                # Construct feature maps for data points X[i] and X[j]
                qc1 = self.construct_feature_map(X[i])
                qc2 = self.construct_feature_map(X[j]).inverse()

                # Combine the circuits for inner product estimation
                combined_qc = qc1.compose(qc2)

                # Simulate the statevector
                statevector = Statevector.from_instruction(combined_qc)

                # Compute the inner product (overlap) as the kernel value
                kernel_matrix[i, j] = np.abs(np.vdot(statevector.data, statevector.data))

        return kernel_matrix


class QuantumOptimizerWithCustomKernel:
    def __init__(self, feature_dimension, bounds):
        self.kernel = CustomQuantumKernel(feature_dimension)
        self.bounds = bounds
        self.samples = []
        self.evaluations = []

    # def objective_function(self, params):
    #     """Simulated objective function to evaluate trading performance (replace with actual logic)."""
    #     rsi_high, rsi_low, position_size = params
    #     # Placeholder reward: Replace with real trading performance metrics
    #     # return -np.abs(rsi_high - 75) + np.abs(rsi_low - 20) + 0.5 * position_size
    #     print("Core's Objective")
    #     return 0

    def ucb_acquisition_function(self, x, kernel_matrix, kappa=2.5):
        """UCB acquisition function based on the kernel matrix."""
        # Compute a simple UCB criterion (for demo purposes, this is simplified)
        mean = np.mean(kernel_matrix)
        std = np.std(kernel_matrix)
        return mean + kappa * std

    def optimize(self, X, max_iters=10):
        """Main optimization loop using UCB."""
        # Compute the kernel matrix for initial points
        kernel_matrix = self.kernel.compute_kernel_matrix(X)

        for iteration in range(max_iters):
            # If no samples yet, initialize randomly within bounds
            if len(self.samples) == 0:
                x_next = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1])
            else:
                # Minimize the negative UCB to select the next sample point
                res = minimize(lambda x: -self.ucb_acquisition_function(x, kernel_matrix),
                               x0=np.random.uniform(self.bounds[:, 0], self.bounds[:, 1]),
                               bounds=self.bounds)
                x_next = res.x

            # Evaluate the objective function
            y_next = self.objective_function(x_next)

            # Update history
            self.samples.append(x_next)
            self.evaluations.append(y_next)

            # print(f"Iteration {iteration + 1}: Sampled Params={x_next}, Objective={y_next}")

        # Return the best-found parameters
        best_index = np.argmax(self.evaluations)
        return self.samples[best_index], self.evaluations[best_index]