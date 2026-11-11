"""Locust Load Testing Suite for Parcl Buyer Intelligence Platform.

SLO Performance Targets:
- Health & Liveness probes: p95 < 15ms
- Analytical Overview & Segments: p95 < 50ms
- Filtered Client Query & Pagination: p95 < 70ms
- NBO & Opportunity Scoring: p95 < 80ms
- Marketing Campaign Simulator: p95 < 80ms
- Overall Throughput: >= 250 requests/sec with zero 5xx errors
"""

from locust import HttpUser, between, task


class ParclEnterpriseUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        """Authenticate user and obtain JWT bearer token."""
        resp = self.client.post("/api/v1/auth/demo-token", json={"role": "analyst"})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(5)
    def test_health_ready(self) -> None:
        """Kubernetes readiness probe."""
        self.client.get("/health/ready")

    @task(10)
    def test_overview(self) -> None:
        """Macro executive portfolio metrics."""
        self.client.get("/api/v1/overview", headers=self.headers)

    @task(8)
    def test_segments_catalog(self) -> None:
        """4 grounded cluster profiles."""
        self.client.get("/api/v1/segments", headers=self.headers)

    @task(6)
    def test_clients_pagination(self) -> None:
        """Filtered cohort client lookups."""
        self.client.get("/api/v1/clients?page=1&page_size=20&country=USA", headers=self.headers)

    @task(4)
    def test_nbo_recommendations(self) -> None:
        """Client next-best-offer recommendations."""
        self.client.get("/api/v1/recommendations/nbo/C0001", headers=self.headers)

    @task(3)
    def test_campaign_simulator(self) -> None:
        """Campaign simulation budget allocation."""
        self.client.post(
            "/api/v1/campaigns/scenario",
            json={
                "total_budget_inr": 150000.0,
                "channel_allocations": {"Website": 0.50, "Agency": 0.35, "Client": 0.15},
                "channel_cpas_inr": {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0},
            },
            headers=self.headers,
        )
