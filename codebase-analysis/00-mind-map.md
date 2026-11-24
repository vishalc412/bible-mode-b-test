# Mind map

The whole system and its component detail. Each leaf names the analysis page with its evidence.

```mermaid
mindmap
  root((bible-mode-b test))
    People and outside systems
      Repository operator, hld/01-system-context.md
      Repository reviewer, hld/01-system-context.md
      GitHub and Actions, hld/01-system-context.md
      Copilot coding agent, hld/01-system-context.md
      Supplier One feed, hld/03-integrations.md
      Payment partner, hld/03-integrations.md
      Local settle fake development only, hld/01-system-context.md
      Image CDN URL only, hld/01-system-context.md
    Components
      catalog, lld/catalog/README.md
        Product lookups, lld/catalog/catalog.md
        HTTP health and price endpoints, lld/api/catalog/catalog.md
      orders, lld/orders/README.md
        Totals validation and settlement, lld/orders/orders.md
        Remote price client, lld/orders/catalog_client.md
      bible-mode-b, lld/bible-mode-b/README.md
        GitHub queue, lld/bible-mode-b/bible_queue.md
        Workflow entry points, hld/03-integrations.md
      tools, lld/tools/README.md
        Component plan, lld/tools/plan.md
        Artifact gate, lld/tools/gate.md
        Issue fanout, lld/tools/fanout.md
    Data and state
      In-memory products, hld/04-data-architecture.md
      GitHub workflow records, hld/04-data-architecture.md
      Plan and component artifacts, lld/data-dictionary.md
      Temporary gate workspace, hld/04-data-architecture.md
    Journeys and operation
      End-to-end flows, hld/05-key-flows.md
      Configuration, reference/configuration.md
      Risks and surprises, reference/risks-and-surprises.md
```

## catalog

```mermaid
mindmap
  root((catalog))
    Modules
      catalog.py, lld/catalog/catalog.md
        Product lookups and feed update
      service.py, lld/catalog/service.md
        GET health and price handlers
      test_catalog.py, lld/catalog/test_catalog.md
    Data
      Product map, hld/04-data-architecture.md
    Routes
      GET health, lld/api/catalog/catalog.md
      GET price SKU, lld/api/catalog/catalog.md
    Outbound
      Supplier One feed, hld/03-integrations.md
      Image CDN URL only, hld/01-system-context.md
```

## orders

```mermaid
mindmap
  root((orders))
    Modules
      orders.py, lld/orders/orders.md
        Line and order totals
        Stock validation
        Settlement request
      catalog_client.py, lld/orders/catalog_client.md
        Remote price lookup
      test_orders.py, lld/orders/test_orders.md
      test_catalog_client.py, lld/orders/test_catalog_client.md
    Catalog access
      Direct in-process calls, hld/05-key-flows.md
      HTTP client for separate service mode, hld/05-key-flows.md
    Outbound
      Catalog service, hld/03-integrations.md
      Payment partner, hld/03-integrations.md
      Local settle fake development only, hld/01-system-context.md
```

## bible-mode-b

```mermaid
mindmap
  root((bible-mode-b))
    Modules
      bible_queue.py, lld/bible-mode-b/bible_queue.md
        Start reconcile and delta commands
        GitHub REST and GraphQL client
    Workflow adapters
      bible-plan.yml, hld/03-integrations.md
      bible-queue.yml, hld/03-integrations.md
      bible-delta.yml, hld/03-integrations.md
      poc-assign-copilot.yml, hld/05-key-flows.md
    GitHub state
      Tracker and session issues, hld/04-data-architecture.md
      Branches and pull requests, hld/04-data-architecture.md
      Component artifacts, lld/data-dictionary.md
```

## tools

```mermaid
mindmap
  root((tools))
    Modules
      plan.py, lld/tools/plan.md
        Component inventory
      gate.py, lld/tools/gate.md
        Artifact and test checks
      fanout.sh, lld/tools/fanout.md
        Labels and component issues
    Data
      plan.json, hld/04-data-architecture.md
      Component pass artifacts, lld/data-dictionary.md
    Outbound
      GitHub CLI, hld/03-integrations.md
```

## As a list

- bible-mode-b test repository
  - People and outside systems
    - Repository operator ([hld/01-system-context.md](hld/01-system-context.md))
    - Repository reviewer ([hld/01-system-context.md](hld/01-system-context.md))
    - GitHub and Actions ([hld/01-system-context.md](hld/01-system-context.md))
    - Copilot coding agent ([hld/01-system-context.md](hld/01-system-context.md))
    - Supplier One feed ([hld/03-integrations.md](hld/03-integrations.md))
    - Payment partner ([hld/03-integrations.md](hld/03-integrations.md))
    - Image CDN URL only ([hld/01-system-context.md](hld/01-system-context.md))
  - Components
    - catalog ([lld/catalog/README.md](lld/catalog/README.md))
      - Product lookups ([lld/catalog/catalog.md](lld/catalog/catalog.md))
      - HTTP health and price endpoints ([lld/api/catalog/catalog.md](lld/api/catalog/catalog.md))
    - orders ([lld/orders/README.md](lld/orders/README.md))
      - Totals, validation, and settlement ([lld/orders/orders.md](lld/orders/orders.md))
      - Remote price client ([lld/orders/catalog_client.md](lld/orders/catalog_client.md))
    - bible-mode-b ([lld/bible-mode-b/README.md](lld/bible-mode-b/README.md))
      - GitHub queue ([lld/bible-mode-b/bible_queue.md](lld/bible-mode-b/bible_queue.md))
      - Workflow entry points ([hld/03-integrations.md](hld/03-integrations.md))
    - tools ([lld/tools/README.md](lld/tools/README.md))
      - Component plan ([lld/tools/plan.md](lld/tools/plan.md))
      - Artifact gate ([lld/tools/gate.md](lld/tools/gate.md))
      - Issue fanout ([lld/tools/fanout.md](lld/tools/fanout.md))
  - Data and state
    - In-memory products ([hld/04-data-architecture.md](hld/04-data-architecture.md))
    - GitHub workflow records ([hld/04-data-architecture.md](hld/04-data-architecture.md))
    - Plan and component artifacts ([lld/data-dictionary.md](lld/data-dictionary.md))
    - Temporary gate workspace ([hld/04-data-architecture.md](hld/04-data-architecture.md))
  - Journeys and operation
    - End-to-end flows ([hld/05-key-flows.md](hld/05-key-flows.md))
    - Configuration ([reference/configuration.md](reference/configuration.md))
    - Risks and surprises ([reference/risks-and-surprises.md](reference/risks-and-surprises.md))
