# Research — 17 October 2026

User: Chess study authors auditing recorded clock annotations in a short standard-start game.

Pain: Missing annotations or an unexplained clock increase should not silently become zero thinking time.

Smallest useful capability: Reconstruct per-ply clock differences from a bounded annotated PGN mainline without hiding missing evidence.

Acceptance: Reproduce increment arithmetic, fractional milliseconds, per-side missing-clock resynchronization, ignored variations, and reject duplicate/leading clocks, malformed controls, wrong move numbers and result conflicts.

Demand is inferred from the workflow and adjacent public evidence, not a verified request for this product. Discovery path: descriptive GitHub topics, a runnable invented example and the chronological portfolio index. No unsolicited outreach or activity manipulation.

## Current alternatives

Live GitHub repository search, sorted **Most stars**, query `PGN parser` and the related broad queries recorded in [provenance](RESEARCH_PROVENANCE.json). Highest-star relevant comparable found in this inspected scope: **niklasf/python-chess**. This is not an exhaustive global ranking.

| Repository | Stars observed | Last push observed (UTC) | Archived | API license classification |
| --- | ---: | --- | --- | --- |
| [niklasf/python-chess](https://github.com/niklasf/python-chess) | 2892 | 2026-08-22T13:17:47Z | False | GPL-3.0 |
| [bhlangonijr/chesslib](https://github.com/bhlangonijr/chesslib) | 297 | 2026-07-06T13:53:40Z | False | Apache-2.0 |
| [mliebelt/pgn-parser](https://github.com/mliebelt/pgn-parser) | 78 | 2026-10-14T15:29:14Z | False | Apache-2.0 |

python-chess already supports PGN clock and elapsed annotations and legal move handling. Chesslib offers a broader Java chess model; mliebelt/pgn-parser produces a structured PGN representation. Their broader capabilities are not replaced. Our dependency-free evidence ledger has stricter bounded input and deliberately does not validate legal chess.

Use python-chess clock accessors, Chesslib or pgn-parser and implement the desired accounting convention.

Current README, selected source semantics and up to five issue/PR records were read. Exact observation times, source blob identities, queries and public issue URLs are in provenance. API NOASSERTION means unclassified license, not permission to copy. No third-party implementation or fixtures are bundled.

Our small Python wheel installs with one command after checkout and includes a direct example. Established alternatives have broader APIs, formats, documentation, examples and support communities. Competitor installations, time to first useful result, reliability, support response and performance were not measured. Our example only proves our documented behavior. Stars inform discovery, not quality or performance.

Portfolio distinction: No existing owned chess/PGN project was found. Other timing tools handle different input domains and do not parse chess mainlines and per-side clock evidence.

No technical performance benchmark, speed/memory superiority or exhaustive feature-gap claim is made. Standard file formats and algorithms are not inventions of this project. Source references informed semantic review; implementation, prose and invented fixtures are original. No copied branding or sample user data is included.
