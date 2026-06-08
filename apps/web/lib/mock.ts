import type { Article, SearchResult } from "@/lib/types";

export const fallbackArticles: Article[] = [
  {
    slug: "quantum-computing",
    title: "Quantum Computing",
    summary:
      "Quantum computing uses quantum-mechanical phenomena such as superposition and entanglement to process information in ways that differ from classical computing.",
    confidence_score: 0.92,
    verification_status: "verified",
    last_verified_at: "2026-06-07",
    related_topics: ["Quantum Mechanics", "Cryptography", "Algorithms"],
    revision_count: 18,
    sections: [
      {
        heading: "Overview",
        content:
          "Quantum computers operate on qubits, which can represent probability amplitudes over multiple states until measurement.",
        citations: ["src-nist", "src-ibm"]
      },
      {
        heading: "Why It Matters",
        content:
          "Certain classes of algorithms can achieve asymptotic improvements over classical approaches, although practical constraints remain substantial.",
        citations: ["src-nature", "src-nist"]
      }
    ],
    timeline: [
      {
        date: "1981",
        title: "Feynman Proposes Quantum Simulation",
        description: "Richard Feynman describes the need for computers that can simulate quantum systems efficiently."
      },
      {
        date: "1994",
        title: "Shor's Algorithm",
        description: "Peter Shor introduces a quantum algorithm for factoring integers efficiently."
      }
    ],
    sources: [
      {
        id: "src-nist",
        title: "Post-Quantum Cryptography",
        publisher: "NIST",
        tier: "A",
        url: "https://www.nist.gov/",
        published_at: "2025-08-13"
      },
      {
        id: "src-ibm",
        title: "Quantum Computing Basics",
        publisher: "IBM",
        tier: "B",
        url: "https://www.ibm.com/quantum",
        published_at: "2025-01-11"
      },
      {
        id: "src-nature",
        title: "Quantum Advantage in Practice",
        publisher: "Nature",
        tier: "A",
        url: "https://www.nature.com/",
        published_at: "2024-11-02"
      }
    ]
  },
  {
    slug: "inflation-in-brazil",
    title: "Inflation in Brazil",
    summary:
      "Inflation in Brazil has historically been shaped by monetary policy, fiscal conditions, exchange-rate dynamics, and commodity cycles.",
    confidence_score: 0.89,
    verification_status: "verified",
    last_verified_at: "2026-06-07",
    related_topics: ["Brazilian Economy", "Central Banking", "Consumer Prices"],
    revision_count: 11,
    sections: [
      {
        heading: "Historical Context",
        content:
          "Brazil experienced periods of very high inflation before stabilization reforms and inflation-targeting frameworks improved price stability.",
        citations: ["src-bcb", "src-imf"]
      },
      {
        heading: "Current Drivers",
        content:
          "Recent inflation patterns often reflect a mix of food prices, administered prices, global energy conditions, and domestic monetary policy.",
        citations: ["src-bcb", "src-worldbank"]
      }
    ],
    timeline: [
      {
        date: "1994",
        title: "Plano Real",
        description: "Brazil launches the Real Plan to stabilize prices and reduce chronic inflation."
      },
      {
        date: "1999",
        title: "Inflation Targeting",
        description: "Brazil formalizes an inflation-targeting regime after the exchange-rate transition."
      }
    ],
    sources: [
      {
        id: "src-bcb",
        title: "Inflation Report",
        publisher: "Banco Central do Brasil",
        tier: "A",
        url: "https://www.bcb.gov.br/",
        published_at: "2026-03-28"
      },
      {
        id: "src-imf",
        title: "Brazil: Staff Report",
        publisher: "IMF",
        tier: "B",
        url: "https://www.imf.org/",
        published_at: "2025-09-18"
      },
      {
        id: "src-worldbank",
        title: "Brazil Economic Outlook",
        publisher: "World Bank",
        tier: "B",
        url: "https://www.worldbank.org/",
        published_at: "2025-12-14"
      }
    ]
  }
];

export const fallbackSearch: SearchResult = {
  answer:
    "Quantum computing is an emerging computing paradigm that uses qubits and quantum effects to solve some problems more efficiently than classical computers, though practical systems remain constrained by error rates and hardware scale.",
  confidence_score: 0.92,
  sources: fallbackArticles[0].sources,
  articles: fallbackArticles.map(({ slug, title, summary, confidence_score, last_verified_at }) => ({
    slug,
    title,
    summary,
    confidence_score,
    last_verified_at
  }))
};

