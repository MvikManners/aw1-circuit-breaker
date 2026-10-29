"""
AW-1 Circuit Breaker: High-Throughput Latency Benchmark Suite
Measures p50, p95, and p99 overhead across deterministic AST inspection runs.
"""

import ast
import time
import statistics
import re
from typing import List

DANGEROUS_SHELL_PATTERNS = [
    r";\s*rm\s+-rf", r"\|\s*bash", r"\|\s*sh",
    r"`.*`", r"\$\(.*\)", r"/dev/tcp/", r"\bnc\s+-e\b"
]

FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__", "subprocess.Popen", "socket.socket"}
FORBIDDEN_MODULES = {"socket", "subprocess", "pty", "shutil"}

BENIGN_CODE = """
import math
data = [12.4, 45.2, 88.1, 99.4, 23.5]
result = math.sqrt(sum(x**2 for x in data) / len(data))
"""

ADVERSARIAL_CODE = """
import base64
payload = base64.b64decode('ZXZhbCgiaGVsbG8iKQ==')
eval(compile(payload, '<string>', 'exec'))
"""

SHELL_PAYLOAD = "cat /var/log/syslog | grep error; rm -rf /tmp/data"


class BenchmarkVisitor(ast.NodeVisitor):
    def __init__(self):
        self.blocked = False

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name.split(".")[0] in FORBIDDEN_MODULES:
                self.blocked = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            curr = node.func
            while isinstance(curr, ast.Attribute):
                parts.append(curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                parts.append(curr.id)
            func_name = ".".join(reversed(parts))
        if func_name in FORBIDDEN_CALLS:
            self.blocked = True
        self.generic_visit(node)


def benchmark_ast(code: str, iterations: int = 1000) -> List[float]:
    times = []
    # Warmup
    for _ in range(50):
        t = ast.parse(code)
        BenchmarkVisitor().visit(t)

    for _ in range(iterations):
        start = time.perf_counter_ns()
        tree = ast.parse(code)
        BenchmarkVisitor().visit(tree)
        times.append((time.perf_counter_ns() - start) / 1_000_000)  # ms
    return times


def benchmark_shell(payload: str, iterations: int = 1000) -> List[float]:
    times = []
    for _ in range(50):
        for p in DANGEROUS_SHELL_PATTERNS:
            re.search(p, payload)

    for _ in range(iterations):
        start = time.perf_counter_ns()
        for p in DANGEROUS_SHELL_PATTERNS:
            re.search(p, payload)
        times.append((time.perf_counter_ns() - start) / 1_000_000)  # ms
    return times


def compute_metrics(times: List[float]):
    times.sort()
    p50 = times[int(len(times) * 0.50)]
    p95 = times[int(len(times) * 0.95)]
    p99 = times[int(len(times) * 0.99)]
    avg = statistics.mean(times)
    return avg, p50, p95, p99


def main():
    print("=" * 65)
    print(" AW-1 CIRCUIT BREAKER -- RUNTIME BENCHMARK TELEMETRY")
    print(f" Sample Size: 1,000 runs per test | Target: Sub-millisecond (< 1.0 ms)")
    print("=" * 65)

    cases = [
        ("AST Inspection (Benign Payload)", benchmark_ast(BENIGN_CODE)),
        ("AST Inspection (Adversarial Exploit)", benchmark_ast(ADVERSARIAL_CODE)),
        ("Regex Argument Inspection (Shell)", benchmark_shell(SHELL_PAYLOAD)),
    ]

    print(f"\n| {'Evaluation Target':<38} | {'p50 (ms)':<8} | {'p95 (ms)':<8} | {'p99 (ms)':<8} |")
    print(f"|{'-'*40}|{'-'*10}|{'-'*10}|{'-'*10}|")

    for label, times in cases:
        _, p50, p95, p99 = compute_metrics(times)
        print(f"| {label:<38} | {p50:<8.4f} | {p95:<8.4f} | {p99:<8.4f} |")

    print("\nBenchmark completed cleanly.\n")


if __name__ == "__main__":
    main()
