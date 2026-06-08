from .models import Article, ArticleSection, Source, TimelineEvent


ARTICLES: list[Article] = [
    Article(
        slug="quantum-computing",
        title="Quantum Computing",
        summary=(
            "Quantum computing uses superposition, interference, and entanglement to process information "
            "with qubits, enabling different computational tradeoffs from classical systems."
        ),
        confidence_score=0.92,
        verification_status="verified",
        last_verified_at="2026-06-07",
        related_topics=["Quantum Mechanics", "Cryptography", "Algorithms"],
        revision_count=18,
        sections=[
            ArticleSection(
                heading="Overview",
                content=(
                    "Quantum computers represent information with qubits rather than bits. "
                    "A qubit can be prepared in a superposition, and quantum algorithms exploit "
                    "interference patterns to amplify useful outcomes."
                ),
                citations=["src-nist", "src-ibm"],
            ),
            ArticleSection(
                heading="Practical Constraints",
                content=(
                    "Useful quantum computation remains limited by decoherence, gate fidelity, "
                    "error-correction overhead, and the difficulty of scaling hardware."
                ),
                citations=["src-nature", "src-nist"],
            ),
        ],
        timeline=[
            TimelineEvent(
                date="1981",
                title="Quantum Simulation Proposal",
                description="Richard Feynman argues for computers designed to simulate quantum systems.",
            ),
            TimelineEvent(
                date="1994",
                title="Shor's Algorithm",
                description="A quantum factoring algorithm demonstrates a major theoretical advantage.",
            ),
        ],
        sources=[
            Source(
                id="src-nist",
                title="Post-Quantum Cryptography",
                publisher="NIST",
                tier="A",
                url="https://www.nist.gov/",
                published_at="2025-08-13",
            ),
            Source(
                id="src-ibm",
                title="Quantum Computing Basics",
                publisher="IBM Quantum",
                tier="B",
                url="https://www.ibm.com/quantum",
                published_at="2025-01-11",
            ),
            Source(
                id="src-nature",
                title="Quantum Advantage in Practice",
                publisher="Nature",
                tier="A",
                url="https://www.nature.com/",
                published_at="2024-11-02",
            ),
        ],
    ),
    Article(
        slug="inflation-in-brazil",
        title="Inflation in Brazil",
        summary=(
            "Inflation in Brazil reflects the interaction of monetary policy, exchange-rate movements, "
            "commodity conditions, fiscal expectations, and administered prices."
        ),
        confidence_score=0.89,
        verification_status="verified",
        last_verified_at="2026-06-07",
        related_topics=["Brazilian Economy", "Central Banking", "Consumer Prices"],
        revision_count=11,
        sections=[
            ArticleSection(
                heading="Historical Context",
                content=(
                    "Brazil experienced prolonged inflation instability before the Real Plan and later "
                    "inflation-targeting frameworks improved price stability."
                ),
                citations=["src-bcb", "src-imf"],
            ),
            ArticleSection(
                heading="Current Drivers",
                content=(
                    "Recent inflation trends often reflect food and energy prices, administered price "
                    "changes, currency effects, and domestic policy choices."
                ),
                citations=["src-bcb", "src-worldbank"],
            ),
        ],
        timeline=[
            TimelineEvent(
                date="1994",
                title="Plano Real",
                description="The Real Plan helps break a period of chronic high inflation.",
            ),
            TimelineEvent(
                date="1999",
                title="Inflation Targeting",
                description="Brazil adopts an inflation-targeting regime after the exchange-rate shift.",
            ),
        ],
        sources=[
            Source(
                id="src-bcb",
                title="Inflation Report",
                publisher="Banco Central do Brasil",
                tier="A",
                url="https://www.bcb.gov.br/",
                published_at="2026-03-28",
            ),
            Source(
                id="src-imf",
                title="Brazil: Staff Report",
                publisher="IMF",
                tier="B",
                url="https://www.imf.org/",
                published_at="2025-09-18",
            ),
            Source(
                id="src-worldbank",
                title="Brazil Economic Outlook",
                publisher="World Bank",
                tier="B",
                url="https://www.worldbank.org/",
                published_at="2025-12-14",
            ),
        ],
    ),
]

