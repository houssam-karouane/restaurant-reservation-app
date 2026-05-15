FROM timberio/vector:0.40.0-alpine

# Railway injects $PORT for the *primary* HTTP service. Vector's HTTP
# source binds to 9000; we tell Railway to route :PORT -> :9000 via
# the start command. Prom exporter stays on 9598 (separate Railway
# domain or internal-only).
EXPOSE 9000 9598

COPY vector.aggregator.yaml /etc/vector/vector.yaml

# --config-yaml is correct for YAML configs (vs --config for TOML).
CMD ["vector", "--config-yaml", "/etc/vector/vector.yaml"]
