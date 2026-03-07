# Migration Playbook Schema

> Defines the structure for phased migration playbooks (`migration-playbook.xml`)

## Overview

The migration playbook schema captures phased migration plans produced by `/reforge.migrate`. It classifies modules by 5R strategy (Rehost, Replatform, Refactor, Rearchitect, Retire), sequences them into dependency-aware phases, and includes a risk register with mitigation strategies.

## Common Elements

This schema extends the [Common Extraction Schema](./common-schema.md), which defines shared structural elements used across all extraction types:

- **Root attributes**: `project-id`, `version`, `schema-version`, `generated`, `xmlns`
- **Metadata container**: `<metadata>` with `<total-count>`, `<confidence-distribution>`, `<extraction-timestamp>`
- **Source references**: Canonical `<source>` format with `file`, `line-start`, `line-end` attributes
- **Confidence vocabulary**: `high`, `medium`, `low` enumeration
- **ID patterns**: `MIG-{CATEGORY}-{SEQUENCE}` (migration items), `RISK-{CATEGORY}-{SEQUENCE}` (risk register items)

See `common-schema.md` for complete definitions. Elements defined there MUST NOT be redefined in this schema.

## Root Element

```xml
<migration-playbook xmlns="http://reforge.dev/schema/extraction"
                    project-id="my-app" version="1.0.0"
                    schema-version="1.0.0"
                    generated="2024-01-15T10:30:00Z">
  <metadata>...</metadata>
  <phases>...</phases>
  <risk-register>...</risk-register>
  <strategy-summary>...</strategy-summary>
</migration-playbook>
```

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `xmlns` | URI | Yes | Must be `http://reforge.dev/schema/extraction` |
| `project-id` | string | Yes | Reference to analysis project |
| `version` | string | Yes | Extraction version (semver) |
| `schema-version` | string | Yes | Common schema version (initial: `1.0.0`) |
| `generated` | dateTime | Yes | Extraction timestamp (ISO-8601) |

> Root attributes and `<metadata>` are defined by the [Common Extraction Schema](./common-schema.md). The `<metadata>` element is required as the first child of the root element. The metadata `<total-count>` equals the total count of migration items across all phases.

## Elements

### `<phases>`

Container for migration phases, ordered by execution sequence.

```xml
<phases count="3">
  <phase>...</phase>
</phases>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of phases in this container |

### `<phase>`

Individual migration phase containing a set of modules to migrate together.

```xml
<phase id="phase-1" name="Foundation" order="1">
  <description>Migrate shared libraries and data access layers with no upstream dependencies</description>
  <prerequisites>
    <prerequisite>Database connection strings externalized to environment variables</prerequisite>
    <prerequisite>CI/CD pipeline configured for target platform</prerequisite>
  </prerequisites>
  <modules count="3">
    <module>...</module>
  </modules>
  <success-criteria>
    <criterion>All unit tests pass on target platform</criterion>
    <criterion>Data access layer responds within 200ms SLA</criterion>
  </success-criteria>
  <estimated-duration unit="person-weeks">4</estimated-duration>
</phase>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Phase identifier (e.g., `phase-1`) |
| `name` | string | Yes | Human-readable phase name |
| `order` | integer | Yes | Execution order (1-based) |

### `<description>` (phase)

Description of the phase's purpose and scope.

### `<prerequisites>`

Container for preconditions that must be met before a phase can begin.

### `<prerequisite>`

Individual precondition text.

### `<modules>` (phase)

Container for modules included in this phase.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of modules in this phase |

### `<module>`

Individual module with its assigned migration strategy.

```xml
<module id="MIG-SVC-001" name="OrderService" strategy="refactor" confidence="high">
  <description>Order processing service requiring business logic restructuring</description>
  <rationale>Complex business rules tightly coupled to legacy ORM; requires refactoring for clean separation</rationale>
  <current-stack>Java 8, Hibernate 3, Spring MVC</current-stack>
  <target-stack>Java 17, Spring Boot 3, JPA</target-stack>
  <effort-estimate unit="person-days">15</effort-estimate>
  <dependencies>
    <dependency ref="MIG-REPO-001">CustomerRepository</dependency>
    <dependency ref="MIG-LIB-001">PaymentGatewayClient</dependency>
  </dependencies>
  <source file="src/service/OrderService.java" line-start="1" line-end="450"/>
</module>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique migration item identifier (`MIG-{CATEGORY}-{SEQUENCE}`) |
| `name` | string | Yes | Module or component name |
| `strategy` | string | Yes | 5R strategy: `rehost`, `replatform`, `refactor`, `rearchitect`, `retire` |
| `confidence` | ConfidenceType | Yes | Confidence in strategy assignment |

### `<description>` (module)

Brief description of the module and its migration context.

### `<rationale>`

Explanation of why the chosen 5R strategy was assigned to this module.

### `<current-stack>`

Current technology stack of the module.

### `<target-stack>`

Target technology stack after migration. For `retire` strategy, this should state "N/A - module to be decommissioned".

### `<effort-estimate>` (module)

Estimated effort for this module's migration.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `unit` | string | Yes | Effort unit: `person-hours`, `person-days`, `person-weeks` |

### `<dependencies>` (module)

Container for dependencies that must be migrated before or alongside this module.

### `<dependency>`

Reference to another migration item this module depends on.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `ref` | string | Yes | ID reference to another `<module>` item |

### `<success-criteria>`

Container for measurable criteria that define phase completion.

### `<criterion>`

Individual success criterion text.

### `<estimated-duration>`

Estimated calendar duration for the phase.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `unit` | string | Yes | Duration unit: `person-days`, `person-weeks`, `person-months` |

### `<source>`

Source code location of the module. Uses the canonical format defined in the [Common Extraction Schema](./common-schema.md#source-references).

### `<risk-register>`

Container for identified migration risks with mitigation strategies.

```xml
<risk-register count="3">
  <risk>...</risk>
</risk-register>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | Yes | Number of risk items |

### `<risk>`

Individual migration risk with impact assessment and mitigation plan.

```xml
<risk id="RISK-DATA-001" category="data-migration" severity="high"
      probability="medium" confidence="high">
  <title>Customer data schema incompatibility</title>
  <description>Legacy customer table uses denormalized address fields incompatible with target normalized schema</description>
  <impact>Data loss or corruption during migration if address fields not properly mapped</impact>
  <affected-modules>
    <module-ref ref="MIG-REPO-001">CustomerRepository</module-ref>
  </affected-modules>
  <mitigation>Create ETL transformation script to normalize address data before migration; validate with sample dataset</mitigation>
  <contingency>Maintain legacy address format in target with deprecation timeline</contingency>
</risk>
```

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique risk identifier (`RISK-{CATEGORY}-{SEQUENCE}`) |
| `category` | string | Yes | Risk category |
| `severity` | string | Yes | Impact severity: `critical`, `high`, `medium`, `low` |
| `probability` | string | Yes | Likelihood: `high`, `medium`, `low` |
| `confidence` | ConfidenceType | Yes | Confidence in risk assessment |

### `<title>` (risk)

Short, descriptive title of the risk.

### `<description>` (risk)

Full description of the risk and its context.

### `<impact>`

Description of the consequences if the risk materializes.

### `<affected-modules>`

Container for modules affected by this risk.

### `<module-ref>`

Reference to a migration module affected by this risk.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `ref` | string | Yes | ID reference to a `<module>` item |

### `<mitigation>`

Primary strategy for reducing the risk's probability or impact.

### `<contingency>`

Fallback plan if the mitigation strategy fails.

### `<strategy-summary>`

Aggregated summary of migration strategies across all modules.

```xml
<strategy-summary>
  <total-modules>12</total-modules>
  <by-strategy>
    <rehost count="2"/>
    <replatform count="3"/>
    <refactor count="4"/>
    <rearchitect count="1"/>
    <retire count="2"/>
  </by-strategy>
  <total-phases>3</total-phases>
  <total-effort unit="person-weeks">24</total-effort>
  <total-risks>5</total-risks>
</strategy-summary>
```

| Element | Type | Required | Description |
|---------|------|----------|-------------|
| `total-modules` | integer | Yes | Total modules in the playbook |
| `by-strategy` | container | Yes | Count per 5R strategy |
| `total-phases` | integer | Yes | Number of migration phases |
| `total-effort` | decimal | Yes | Aggregate effort estimate (with `unit` attribute) |
| `total-risks` | integer | Yes | Number of identified risks |

## Common Categories

### Migration Module Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `SVC` | Service modules | Business logic services, API handlers |
| `REPO` | Data access | Repositories, DAOs, data layers |
| `LIB` | Shared libraries | Utility libraries, common frameworks |
| `UI` | User interface | Frontend components, views, templates |
| `INT` | Integrations | External API clients, messaging adapters |
| `INFRA` | Infrastructure | Configuration, deployment, monitoring |

### Risk Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `DATA` | Data migration | Schema incompatibility, data loss |
| `PERF` | Performance | Degradation, SLA violations |
| `COMPAT` | Compatibility | API breaking changes, protocol mismatches |
| `SKILL` | Team skills | Knowledge gaps, training needs |
| `VENDOR` | Vendor/license | License changes, vendor lock-in |
| `SCOPE` | Scope/schedule | Timeline risk, scope creep |

### 5R Strategy Definitions

| Strategy | Description | When to Apply |
|----------|-------------|---------------|
| `rehost` | Lift and shift with no code changes | Cloud migration with compatible runtime |
| `replatform` | Minor adjustments for new platform | Database swap, container adoption |
| `refactor` | Restructure code while preserving behavior | Technical debt reduction, modernization |
| `rearchitect` | Redesign with new architecture patterns | Monolith-to-microservices, event-driven |
| `retire` | Decommission unused or replaced modules | Dead code, superseded functionality |

## Example Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<migration-playbook xmlns="http://reforge.dev/schema/extraction"
                    project-id="ecommerce-legacy" version="1.0.0"
                    schema-version="1.0.0"
                    generated="2024-01-15T10:30:00Z">

  <metadata>
    <total-count>3</total-count>
    <confidence-distribution>
      <high>2</high>
      <medium>1</medium>
      <low>0</low>
    </confidence-distribution>
    <extraction-timestamp>2024-01-15T10:30:00Z</extraction-timestamp>
  </metadata>

  <phases count="2">
    <phase id="phase-1" name="Foundation" order="1">
      <description>Migrate shared data access and utility libraries with no upstream dependencies</description>
      <prerequisites>
        <prerequisite>Target database provisioned and accessible</prerequisite>
        <prerequisite>CI/CD pipeline configured for target platform</prerequisite>
      </prerequisites>
      <modules count="2">
        <module id="MIG-REPO-001" name="CustomerRepository" strategy="replatform" confidence="high">
          <description>Customer data access layer with legacy JDBC queries</description>
          <rationale>Well-isolated data layer; replatform to Spring Data JPA with minimal logic changes</rationale>
          <current-stack>Java 8, raw JDBC, custom connection pool</current-stack>
          <target-stack>Java 17, Spring Data JPA, HikariCP</target-stack>
          <effort-estimate unit="person-days">8</effort-estimate>
          <dependencies/>
          <source file="src/repository/CustomerRepository.java" line-start="1" line-end="200"/>
        </module>

        <module id="MIG-LIB-001" name="PaymentGatewayClient" strategy="refactor" confidence="medium">
          <description>Payment gateway integration client using deprecated SDK</description>
          <rationale>SDK deprecated; refactor to new REST API with async support</rationale>
          <current-stack>Java 8, Stripe SDK v1</current-stack>
          <target-stack>Java 17, Stripe SDK v3, WebClient</target-stack>
          <effort-estimate unit="person-days">12</effort-estimate>
          <dependencies/>
          <source file="src/integration/PaymentGatewayClient.java" line-start="1" line-end="180"/>
        </module>
      </modules>
      <success-criteria>
        <criterion>All repository unit tests pass against target database</criterion>
        <criterion>Payment gateway integration tests pass with sandbox</criterion>
      </success-criteria>
      <estimated-duration unit="person-weeks">3</estimated-duration>
    </phase>

    <phase id="phase-2" name="Core Services" order="2">
      <description>Migrate core business services that depend on Phase 1 components</description>
      <prerequisites>
        <prerequisite>Phase 1 modules deployed and validated in staging</prerequisite>
      </prerequisites>
      <modules count="1">
        <module id="MIG-SVC-001" name="OrderService" strategy="refactor" confidence="high">
          <description>Order processing service with payment integration</description>
          <rationale>Complex business rules tightly coupled to legacy ORM; requires refactoring for clean separation</rationale>
          <current-stack>Java 8, Hibernate 3, Spring MVC</current-stack>
          <target-stack>Java 17, Spring Boot 3, JPA</target-stack>
          <effort-estimate unit="person-days">15</effort-estimate>
          <dependencies>
            <dependency ref="MIG-REPO-001">CustomerRepository</dependency>
            <dependency ref="MIG-LIB-001">PaymentGatewayClient</dependency>
          </dependencies>
          <source file="src/service/OrderService.java" line-start="1" line-end="450"/>
        </module>
      </modules>
      <success-criteria>
        <criterion>Order placement end-to-end test passes</criterion>
        <criterion>Response time within 200ms SLA</criterion>
      </success-criteria>
      <estimated-duration unit="person-weeks">3</estimated-duration>
    </phase>
  </phases>

  <risk-register count="1">
    <risk id="RISK-DATA-001" category="data-migration" severity="high"
          probability="medium" confidence="high">
      <title>Customer data schema incompatibility</title>
      <description>Legacy customer table uses denormalized address fields incompatible with target normalized schema</description>
      <impact>Data loss or corruption during migration if address fields not properly mapped</impact>
      <affected-modules>
        <module-ref ref="MIG-REPO-001">CustomerRepository</module-ref>
      </affected-modules>
      <mitigation>Create ETL transformation script to normalize address data before migration; validate with sample dataset</mitigation>
      <contingency>Maintain legacy address format in target with deprecation timeline</contingency>
    </risk>
  </risk-register>

  <strategy-summary>
    <total-modules>3</total-modules>
    <by-strategy>
      <rehost count="0"/>
      <replatform count="1"/>
      <refactor count="2"/>
      <rearchitect count="0"/>
      <retire count="0"/>
    </by-strategy>
    <total-phases>2</total-phases>
    <total-effort unit="person-weeks">6</total-effort>
    <total-risks>1</total-risks>
  </strategy-summary>

</migration-playbook>
```

## Related Schemas

- [Common Schema](./common-schema.md) — Shared elements (root attributes, metadata, source references, confidence)
- [architecture.md](./architecture.md) — Architectural components informing module boundaries and strategies
- [dependencies.md](./dependencies.md) — Dependency graphs used for phase sequencing
- [issues.md](./issues.md) — Issues and technical debt informing strategy selection
- [effort-estimate.md](./effort-estimate.md) — Detailed effort estimates per module
