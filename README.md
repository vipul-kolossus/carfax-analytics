# carfax_analytics

Reusable Python package for the Carfax data analytics platform.
Provides parameterized query functions, territory analytics, visualization helpers, and typed data models.

---

## Installation

```bash
pip install -r requirements.txt
```

Credentials are supplied through environment variables — never hardcode them.

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_HOST` | PostgreSQL host |
| `WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_PORT` | PostgreSQL port |
| `WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_DATABASE` | Database name |
| `WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_USERNAME` | Username |
| `WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_PASSWORD` | Password |
| `WORKFORCE_CRED_FF884749_POSTGRES_CARFAX_CORE_SSL_MODE` | SSL mode (default: `require`) |

---

## Package Structure

```
carfax_analytics/
  connections.py          # Env-var based DB connection factory
  queries/
    net_revenue.py        # Net Revenue by Territory query
    catalog.py            # Business Glossary + semantic catalog queries
  analytics/
    territory.py          # Territory summary, ranking, top-N functions
  visualizations/
    lineage.py            # Net Revenue lineage diagram (PNG)
    charts.py             # Bar chart helpers
  models/
    entities.py           # TerritoryRevenue, DealerFinancial dataclasses
  setup.py
  requirements.txt
  README.md
```

---

## Usage Examples

### Net Revenue by Territory

```python
from carfax_analytics.queries import get_net_revenue_by_territory

# All territories
rows = get_net_revenue_by_territory()
for row in rows:
    print(row['territory_code'], row['net_revenue'])

# Filtered to specific territories
rows = get_net_revenue_by_territory(territories=['EAST', 'WEST'])
```

### Territory Analytics

```python
from carfax_analytics.analytics import (
    get_territory_summary,
    get_top_territories,
    get_territory_ranking,
)

# High-level summary
summary = get_territory_summary()
print(f"Top territory: {summary['top_territory']} — ${summary['top_territory_revenue']:,.2f}")

# Top 5 by revenue
top5 = get_top_territories(n=5)

# Ranked list
ranked = get_territory_ranking()
for t in ranked:
    print(f"#{t['rank']} {t['territory_code']}: ${t['net_revenue']:,.2f}")
```

### Business Glossary & Catalog

```python
from carfax_analytics.queries import (
    get_glossary_terms,
    get_table_columns,
    get_table_relationships,
)

# Finance-related glossary terms
terms = get_glossary_terms(category='finance')

# Column metadata for dlr_fin
cols = get_table_columns('carfax_operations', 'dlr_fin')

# Relationships involving dlr tables
rels = get_table_relationships(table_name='dlr_fin')
```

### Visualizations

```python
from carfax_analytics.queries import get_net_revenue_by_territory
from carfax_analytics.visualizations import (
    render_net_revenue_lineage,
    bar_chart_territory_revenue,
)

# Net Revenue lineage diagram
path = render_net_revenue_lineage('/tmp/lineage.png')
print(f"Lineage diagram saved to: {path}")

# Bar chart from query results
rows = get_net_revenue_by_territory()
chart_path = bar_chart_territory_revenue(rows, top_n=10)
print(f"Chart saved to: {chart_path}")
```

### Typed Models

```python
from carfax_analytics.queries import get_net_revenue_by_territory
from carfax_analytics.models import TerritoryRevenue

rows = get_net_revenue_by_territory()
territories = [TerritoryRevenue.from_dict(r) for r in rows]

for t in territories:
    print(f"{t.territory_code}: ${t.net_revenue:,.2f} | Discount rate: {t.discount_rate:.1f}%")
```

---

## Metric Definitions

| Metric | Formula | Grain |
|---|---|---|
| **Net Revenue** | `SUM(inv_amt) − SUM(dsc_amt) − SUM(refund_amt)` | Territory (`trt_cd`) |

Source tables: `carfax_operations.dlr_fin` (fact) × `carfax_operations.dlr_dim` (dimension).
Join key: `dealer_id`.

---

## License

MIT
