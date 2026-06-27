# Referência: Java / Kotlin — Pre-Commit Quality Gate

## Mapeamento Completo por Step

| # | Categoria | Ferramenta | Comando base |
|---|-----------|-----------|--------------|
| 1 | Formatter | `google-java-format` / `spotless` | `mvn spotless:check` ou `./gradlew spotlessCheck` |
| 2 | Linter | `checkstyle` + `spotbugs` + `pmd` | `mvn checkstyle:check spotbugs:check pmd:check` |
| 3 | Security | `dependency-check` (OWASP) | `mvn dependency-check:check` |
| 4 | Dead code | `spotbugs` (URF rules) + `unused-imports` | embutido no spotbugs / IDE plugin |
| 5 | Modernizer | `modernizer-maven-plugin` | `mvn modernizer:modernizer` (report-only) |
| 6 | Conventions | custom grep / ArchUnit | ver seção abaixo |
| 7 | Module hygiene | `mvn dependency:analyze` | `mvn dependency:analyze -DfailOnWarning=true` |
| 8 | Tests + cov | `mvn test` + JaCoCo | `mvn test jacoco:check` |
| 9 | Race/concurrency | `jcstress` / thread sanitizer | `mvn test -Pjcstress` (soft-skip sem profile) |
| 10 | Integration | docker-compose + Testcontainers/WireMock | ver seção abaixo |
| 11 | Mutation | `pitest` | `mvn pitest:mutationCoverage` |
| 12 | Performance | `k6` ou `gatling` | `mvn gatling:test` ou `k6 run performance/smoke.js` |
| 13 | Schema pipeline | `openapi-generator` / `protoc` / `avro` | `mvn generate-sources && git diff --exit-code` |
| 14 | Docker build | `docker build` | `docker build -t test-build .` |

---

## Detecção: Maven vs Gradle

| Arquivo | Build tool | Wrapper |
|---------|-----------|---------|
| `pom.xml` | Maven | `./mvnw` (fallback: `mvn`) |
| `build.gradle` / `build.gradle.kts` | Gradle | `./gradlew` (fallback: `gradle`) |

Usar wrapper quando presente. Verificar com `test -f ./mvnw` ou `test -f ./gradlew`.

Se `settings.xml` existir no projeto, adicionar `-s settings.xml` a todos os comandos Maven.

---

## Instalação de Ferramentas

Ferramentas Java são declaradas como plugins Maven/Gradle — não requerem instalação global.

Plugins Maven recomendados no `pom.xml`:

```xml
<!-- Formatter -->
<plugin>
  <groupId>com.diffplug.spotless</groupId>
  <artifactId>spotless-maven-plugin</artifactId>
</plugin>

<!-- Linter -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-checkstyle-plugin</artifactId>
</plugin>
<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
</plugin>

<!-- Security -->
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
</plugin>

<!-- Coverage -->
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
</plugin>

<!-- Mutation -->
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
</plugin>
```

Ferramentas externas (instalação global):

```bash
# Gitleaks
brew install gitleaks                          # macOS
# ou: https://github.com/gitleaks/gitleaks

# Performance
brew install k6                                # macOS
# ou Gatling via Maven plugin (já declarado)

# Proto / OpenAPI
brew install bufbuild/buf/buf                  # proto
npm install -g @openapitools/openapi-generator-cli  # openapi
```

---

## Step 6 — Convention Guards

### Via grep (simples)

```bash
# Proibir System.out.println em src/main/
if grep -rn "System\.out\.print" --include="*.java" src/main/; then
  echo "[FAIL] System.out.print proibido — use SLF4J logger"
  exit 1
fi

# Proibir @Autowired em campo (preferir injeção por construtor)
if grep -rn "@Autowired" --include="*.java" src/main/ | grep -v "constructor"; then
  echo "[FAIL] @Autowired em campo proibido — use injeção por construtor"
  exit 1
fi

# Domain não importa infra
if grep -rn "import.*infrastructure" --include="*.java" src/main/java/*/domain/; then
  echo "[FAIL] domain/ não pode importar infrastructure/"
  exit 1
fi
```

### Via ArchUnit (robusto)

```java
// src/test/java/arch/ArchitectureTest.java
@AnalyzeClasses(packages = "com.example")
class ArchitectureTest {
    @ArchTest
    static final ArchRule domainIndependence =
        noClasses().that().resideInAPackage("..domain..")
            .should().dependOnClassesThat()
            .resideInAPackage("..infrastructure..");

    @ArchTest
    static final ArchRule noFieldInjection =
        noFields().should().beAnnotatedWith(Autowired.class);
}
```

ArchUnit testes rodam no step 8 (são testes unitários). Step 6 grep cobre o que ArchUnit não alcança (sync de env-keys, padrões em configs não-Java).

---

## Step 8 — Cobertura com JaCoCo

```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <executions>
    <execution>
      <goals><goal>prepare-agent</goal></goals>
    </execution>
    <execution>
      <id>check</id>
      <goals><goal>check</goal></goals>
      <configuration>
        <rules>
          <rule>
            <element>BUNDLE</element>
            <limits>
              <limit>
                <counter>LINE</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.90</minimum>
              </limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

Comando no hook:

```bash
MVN_CMD="./mvnw"
[[ ! -f ./mvnw ]] && MVN_CMD="mvn"
SETTINGS_ARG=""
[[ -f settings.xml ]] && SETTINGS_ARG="-s settings.xml"

$MVN_CMD test jacoco:check $SETTINGS_ARG
```

---

## Step 10 — Integration tests com Testcontainers/WireMock

```bash
# Testcontainers gerencia Docker automaticamente — basta Docker estar disponível
$MVN_CMD test -Pintegration $SETTINGS_ARG

# Ou via docker-compose + WireMock manual:
docker-compose -f docker-compose.test.yml up -d wiremock
trap 'docker-compose -f docker-compose.test.yml down --remove-orphans' EXIT
timeout 30 bash -c 'until curl -sf http://localhost:8080/__admin/health; do sleep 1; done'
$MVN_CMD test -Pintegration $SETTINGS_ARG
```

---

## Step 11 — Mutation com PIT

```bash
$MVN_CMD pitest:mutationCoverage $SETTINGS_ARG

# PIT gera relatório em target/pit-reports/
# Threshold configurado no pom.xml:
```

```xml
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <configuration>
    <mutationThreshold>70</mutationThreshold>
    <excludedClasses>
      <param>*.dto.*</param>
      <param>*.config.*</param>
    </excludedClasses>
  </configuration>
</plugin>
```

---

## Notas Específicas de Java/Kotlin

- **`settings.xml`**: se presente, incluir `-s settings.xml` em todos os comandos Maven
- **Multi-module**: usar `-pl :module-name` ou `--projects` para escopar ao módulo modificado
- **Kotlin**: substituir `google-java-format` por `ktlint` ou `ktfmt`; `detekt` substitui `checkstyle`
- **Spring Boot**: `@SpringBootTest` testes são integração (step 10), não unitários (step 8) — separar via profiles Maven
- **Flyway/Liquibase**: se migrations existirem, step 7 pode validar migration checksums
- **Geração de código (MapStruct, Lombok)**: rodar `mvn compile` antes dos testes se há processadores de anotação
