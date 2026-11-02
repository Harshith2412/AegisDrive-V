# v0.4.0 security and safety evaluation

846 runs: 180 attack-matrix, 72 safety-security interaction, 90 attack-free, 360 locked-v0.3 hold-out, 144 new security hold-out.
A = existing unauthenticated payloads/E2E, B = authentication + strict freshness, C = authentication + bounded authenticated resynchronization.
All policies use matched inputs/seeds and the same bounded frame-budget fabric. Original v0.3 behavior is reproduced separately in baseline/.

| Split / case | Mode | n | Collisions | Unnecessary braking | Minimum gap (m) | Legitimate rejections / offered | Attack rejected / offered | Native attack accepted / offered (primary only) |
|---|---|---|---|---|---|---|---|---|
| attack_matrix/A01 | A | 5 | 0 | 5 | 459.373 | 0 / 30000 | 0 / 0 | 0 / 0 |
| attack_matrix/A01 | B | 5 | 0 | 0 | 291.667 | 0 / 30000 | 0 / 0 | 0 / 0 |
| attack_matrix/A01 | C | 5 | 0 | 0 | 291.667 | 0 / 30000 | 0 / 0 | 0 / 0 |
| attack_matrix/A02 | A | 5 | 0 | 0 | 4.416 | 0 / 23500 | 0 / 6500 | 6500 / 6500 |
| attack_matrix/A02 | B | 5 | 5 | 0 | 0.000 | 0 / 9640 | 1880 / 1880 | 0 / 0 |
| attack_matrix/A02 | C | 5 | 5 | 0 | 0.000 | 0 / 9640 | 1880 / 1880 | 0 / 0 |
| attack_matrix/A03 | A | 5 | 0 | 5 | 459.373 | 0 / 23500 | 0 / 6500 | 6500 / 6500 |
| attack_matrix/A03 | B | 5 | 0 | 0 | 291.667 | 0 / 23500 | 6500 / 6500 | 0 / 0 |
| attack_matrix/A03 | C | 5 | 0 | 0 | 291.667 | 0 / 23500 | 6500 / 6500 | 0 / 0 |
| attack_matrix/A04 | A | 5 | 0 | 5 | 459.373 | 0 / 23500 | 0 / 6500 | 6500 / 6500 |
| attack_matrix/A04 | B | 5 | 0 | 0 | 291.667 | 0 / 23500 | 6500 / 6500 | 0 / 0 |
| attack_matrix/A04 | C | 5 | 0 | 0 | 291.667 | 0 / 23500 | 6500 / 6500 | 0 / 0 |
| attack_matrix/A05 | A | 5 | 0 | 0 | 4.270 | 0 / 23500 | 0 / 6400 | 6400 / 6400 |
| attack_matrix/A05 | B | 5 | 5 | 0 | 0.000 | 0 / 9640 | 1780 / 1780 | 0 / 0 |
| attack_matrix/A05 | C | 5 | 5 | 0 | 0.000 | 0 / 9640 | 1780 / 1780 | 0 / 0 |
| attack_matrix/A06 | A | 5 | 0 | 0 | 5.344 | 0 / 30000 | 0 / 6500 | 6500 / 6500 |
| attack_matrix/A06 | B | 5 | 5 | 0 | 0.000 | 1880 / 11520 | 1880 / 1880 | 0 / 0 |
| attack_matrix/A06 | C | 5 | 0 | 0 | 5.344 | 0 / 30000 | 0 / 6500 | 6500 / 6500 |
| attack_matrix/A07 | A | 5 | 0 | 0 | 5.344 | 0 / 29170 | 0 / 0 | 0 / 0 |
| attack_matrix/A07 | B | 5 | 0 | 0 | 5.344 | 18790 / 29170 | 0 / 0 | 0 / 0 |
| attack_matrix/A07 | C | 5 | 0 | 0 | 5.344 | 12535 / 29170 | 0 / 0 | 0 / 0 |
| attack_matrix/A08 | A | 5 | 0 | 0 | 4.941 | 0 / 23500 | 0 / 6470 | 6470 / 6470 |
| attack_matrix/A08 | B | 5 | 0 | 0 | 4.941 | 0 / 23500 | 0 / 6470 | 6470 / 6470 |
| attack_matrix/A08 | C | 5 | 0 | 0 | 4.941 | 0 / 23500 | 0 / 6470 | 6470 / 6470 |
| attack_matrix/A09 | A | 5 | 0 | 0 | 5.280 | 0 / 26750 | 0 / 3250 | 0 / 3250 |
| attack_matrix/A09 | B | 5 | 0 | 0 | 5.280 | 0 / 26750 | 3250 / 3250 | 0 / 0 |
| attack_matrix/A09 | C | 5 | 0 | 0 | 5.280 | 0 / 26750 | 3250 / 3250 | 0 / 0 |
| attack_matrix/A10 | A | 5 | 0 | 0 | 5.344 | 0 / 30000 | 0 / 5500 | 5500 / 5500 |
| attack_matrix/A10 | B | 5 | 5 | 0 | 0.000 | 2084 / 12168 | 1042 / 1042 | 0 / 0 |
| attack_matrix/A10 | C | 5 | 0 | 0 | 4.430 | 200 / 30000 | 100 / 5500 | 5395 / 5400 |
| attack_matrix/A11 | A | 5 | 5 | 0 | 0.000 | 0 / 11520 | 0 / 0 | 0 / 0 |
| attack_matrix/A11 | B | 5 | 5 | 0 | 0.000 | 0 / 11520 | 0 / 0 | 0 / 0 |
| attack_matrix/A11 | C | 5 | 5 | 0 | 0.000 | 0 / 11520 | 0 / 0 | 0 / 0 |
| attack_matrix/A12 | A | 5 | 0 | 5 | 459.373 | 0 / 23500 | 0 / 6500 | 6500 / 6500 |
| attack_matrix/A12 | B | 5 | 0 | 5 | 459.373 | 0 / 23500 | 0 / 6500 | 6500 / 6500 |
| attack_matrix/A12 | C | 5 | 0 | 5 | 459.373 | 0 / 23500 | 0 / 6500 | 6500 / 6500 |
| coengineering/C01_forged_rejected | A | 3 | 0 | 3 | 459.373 | 0 / 18597 | 0 / 3900 | 0 / 0 |
| coengineering/C01_forged_rejected | B | 3 | 0 | 0 | 291.667 | 0 / 18597 | 3900 / 3900 | 0 / 0 |
| coengineering/C01_forged_rejected | C | 3 | 0 | 0 | 291.667 | 0 / 18597 | 3900 / 3900 | 0 / 0 |
| coengineering/C02_legitimate_bad_auth | A | 3 | 0 | 0 | 5.344 | 0 / 18000 | 0 / 0 | 0 / 0 |
| coengineering/C02_legitimate_bad_auth | B | 3 | 3 | 0 | 0.000 | 1128 / 6912 | 1128 / 1128 | 0 / 0 |
| coengineering/C02_legitimate_bad_auth | C | 3 | 3 | 0 | 0.000 | 1128 / 6912 | 1128 / 1128 | 0 / 0 |
| coengineering/C03_desync | A | 3 | 0 | 0 | 5.344 | 0 / 18000 | 0 / 3900 | 3900 / 3900 |
| coengineering/C03_desync | B | 3 | 3 | 0 | 0.000 | 1128 / 6912 | 1128 / 1128 | 0 / 0 |
| coengineering/C03_desync | C | 3 | 0 | 0 | 5.344 | 0 / 18000 | 0 / 3900 | 3900 / 3900 |
| coengineering/C04_flood | A | 3 | 0 | 0 | 5.344 | 0 / 21840 | 0 / 0 | 0 / 0 |
| coengineering/C04_flood | B | 3 | 0 | 0 | 5.344 | 15012 / 21840 | 0 / 0 | 0 / 0 |
| coengineering/C04_flood | C | 3 | 0 | 0 | 5.344 | 11259 / 21840 | 0 / 0 | 0 / 0 |
| coengineering/C05_gateway_down | A | 3 | 3 | 0 | 0.000 | 0 / 3000 | 0 / 0 | 0 / 0 |
| coengineering/C05_gateway_down | B | 3 | 3 | 0 | 0.000 | 0 / 3000 | 0 / 0 | 0 / 0 |
| coengineering/C05_gateway_down | C | 3 | 3 | 0 | 0.000 | 0 / 3000 | 0 / 0 | 0 / 0 |
| coengineering/C06_primary_bad_backup_healthy | A | 3 | 0 | 0 | 5.344 | 0 / 22497 | 0 / 0 | 0 / 0 |
| coengineering/C06_primary_bad_backup_healthy | B | 3 | 0 | 0 | 5.272 | 3900 / 22497 | 3900 / 3900 | 0 / 0 |
| coengineering/C06_primary_bad_backup_healthy | C | 3 | 0 | 0 | 5.272 | 3900 / 22497 | 3900 / 3900 | 0 / 0 |
| coengineering/C07_shared_compromise | A | 3 | 0 | 3 | 459.373 | 0 / 14700 | 0 / 7797 | 0 / 0 |
| coengineering/C07_shared_compromise | B | 3 | 0 | 3 | 459.373 | 0 / 14700 | 0 / 7797 | 0 / 0 |
| coengineering/C07_shared_compromise | C | 3 | 0 | 3 | 459.373 | 0 / 14700 | 0 / 7797 | 0 / 0 |
| coengineering/C08_trusted_ecu | A | 3 | 0 | 3 | 459.373 | 0 / 14700 | 0 / 7797 | 0 / 0 |
| coengineering/C08_trusted_ecu | B | 3 | 0 | 3 | 459.373 | 0 / 14700 | 0 / 7797 | 0 / 0 |
| coengineering/C08_trusted_ecu | C | 3 | 0 | 3 | 459.373 | 0 / 14700 | 0 / 7797 | 0 / 0 |
| attack_free/FI01 | A | 5 | 0 | 0 | 5.534 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/FI01 | B | 5 | 0 | 0 | 5.534 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/FI01 | C | 5 | 0 | 0 | 5.534 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/FI02 | A | 5 | 0 | 0 | 5.350 | 0 / 32095 | 0 / 0 | 0 / 0 |
| attack_free/FI02 | B | 5 | 0 | 0 | 5.350 | 0 / 32095 | 0 / 0 | 0 / 0 |
| attack_free/FI02 | C | 5 | 0 | 0 | 5.350 | 0 / 32095 | 0 / 0 | 0 / 0 |
| attack_free/S01 | A | 5 | 0 | 0 | 40.000 | 0 / 49995 | 0 / 0 | 0 / 0 |
| attack_free/S01 | B | 5 | 0 | 0 | 40.000 | 0 / 49995 | 0 / 0 | 0 / 0 |
| attack_free/S01 | C | 5 | 0 | 0 | 40.000 | 0 / 49995 | 0 / 0 | 0 / 0 |
| attack_free/S02 | A | 5 | 0 | 0 | 7.354 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/S02 | B | 5 | 0 | 0 | 7.354 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/S02 | C | 5 | 0 | 0 | 7.354 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/S03 | A | 5 | 0 | 0 | 5.344 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/S03 | B | 5 | 0 | 0 | 5.344 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/S03 | C | 5 | 0 | 0 | 5.344 | 0 / 37495 | 0 / 0 | 0 / 0 |
| attack_free/S04 | A | 5 | 0 | 0 | 20.263 | 0 / 49995 | 0 / 0 | 0 / 0 |
| attack_free/S04 | B | 5 | 0 | 0 | 20.263 | 0 / 49995 | 0 / 0 | 0 / 0 |
| attack_free/S04 | C | 5 | 0 | 0 | 20.263 | 0 / 49995 | 0 / 0 | 0 / 0 |
| locked_v3_holdout/locked_v3_holdout | A | 120 | 29 | 0 | 0.000 | 0 / 946460 | 0 / 0 | 0 / 0 |
| locked_v3_holdout/locked_v3_holdout | B | 120 | 29 | 0 | 0.000 | 0 / 946460 | 0 / 0 | 0 / 0 |
| locked_v3_holdout/locked_v3_holdout | C | 120 | 29 | 0 | 0.000 | 0 / 946460 | 0 / 0 | 0 / 0 |
| new_security_holdout/new_security_holdout | A | 48 | 0 | 15 | 2.673 | 0 / 258677 | 0 / 49660 | 22113 / 22706 |
| new_security_holdout/new_security_holdout | B | 48 | 12 | 3 | 0.000 | 21805 / 218115 | 24001 / 34466 | 4190 / 4191 |
| new_security_holdout/new_security_holdout | C | 48 | 6 | 3 | 0.000 | 12578 / 242885 | 21422 / 43284 | 7886 / 7888 |

| Case/config | Gateway command availability | Verification CPU mean/max (µs) | Tx CPU mean (µs) | First request / achieved brake (s) | First observed event / C++ DTC (s) | Mean unavailable (s) | Queue drops |
|---|---|---|---|---|---|---|---|
| attack_matrix/A01/A | 0.9993337774816788 | None / 0 | None | 2.0 / 2.01 | None / None | 0.0 | 0 |
| attack_matrix/A01/B | 0.9993337774816788 | 4.786768957082499 / 130.0 | 4.103930712858094 | None / None | 2.0 / 2.0 | 0.0 | 0 |
| attack_matrix/A01/C | 0.9993337774816788 | 4.7338670224594175 / 94.0 | 4.086786586719964 | None / None | 2.0 / 2.0 | 0.0 | 0 |
| attack_matrix/A02/A | 0.9993337774816788 | None / 0 | None | 3.524 / 3.704 | None / None | 0.0 | 0 |
| attack_matrix/A02/B | 0.3466204506065858 | 5.233739130434783 / 44.0 | 4.170190641247834 | 3.524 / None | 2.01 / 2.02 | 3.6400000000000388 | 0 |
| attack_matrix/A02/C | 0.3466204506065858 | 5.556637681159421 / 57.0 | 4.462391681109185 | 3.524 / None | 2.01 / 2.02 | 3.6400000000000388 | 0 |
| attack_matrix/A03/A | 0.9993337774816788 | None / 0 | None | None / 2.01 | None / None | 0.0 | 0 |
| attack_matrix/A03/B | 0.13324450366422386 | 4.7446964643095395 / 79.0 | 4.11072618254497 | None / None | 2.01 / 2.02 | 12.87999999999977 | 0 |
| attack_matrix/A03/C | 0.13324450366422386 | 4.730642650655993 / 39.0 | 4.107439484787919 | None / None | 2.01 / 2.02 | 12.87999999999977 | 0 |
| attack_matrix/A04/A | 0.9993337774816788 | None / 0 | None | None / 2.01 | None / None | 0.0 | 0 |
| attack_matrix/A04/B | 0.13324450366422386 | 5.119368467867467 / 27.0 | 4.145636242504997 | None / None | 2.01 / 2.02 | 12.87999999999977 | 0 |
| attack_matrix/A04/C | 0.13324450366422386 | 5.129241716700022 / 65.0 | 4.153675327559405 | None / None | 2.01 / 2.02 | 12.87999999999977 | 0 |
| attack_matrix/A05/A | 0.9860093271152565 | None / 0 | None | 3.524 / 3.744 | None / None | 12.87999999999977 | 0 |
| attack_matrix/A05/B | 0.3466204506065858 | 5.201807580174927 / 48.0 | 4.142345465049105 | 3.524 / None | 2.21 / 2.22 | 3.6400000000000388 | 0 |
| attack_matrix/A05/C | 0.3466204506065858 | 5.194110787172011 / 37.0 | 4.124667822068169 | 3.524 / None | 2.21 / 2.22 | 3.6400000000000388 | 0 |
| attack_matrix/A06/A | 0.9993337774816788 | None / 0 | None | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_matrix/A06/B | 0.3466204506065858 | 5.244405797101449 / 41.0 | 4.140265742345465 | 3.524 / None | 2.01 / 2.02 | 3.6400000000000388 | 0 |
| attack_matrix/A06/C | 0.9993337774816788 | 5.221503224371803 / 26.0 | 4.142793693093493 | 3.524 / 3.544 | 2.01 / 2.02 | 0.0 | 0 |
| attack_matrix/A07/A | 0.9866755496335776 | None / 0 | None | 3.524 / 3.544 | 2.03 / None | 12.88999999999977 | 32230 |
| attack_matrix/A07/B | 0.983344437041972 | 5.366946080652469 / 86.0 | 4.2945147679324895 | 3.524 / 3.544 | 2.03 / 2.03 | 12.88999999999977 | 32230 |
| attack_matrix/A07/C | 0.983344437041972 | 5.389895786135026 / 66.0 | 4.319964468132357 | 3.524 / 3.544 | 2.03 / 2.03 | 12.88999999999977 | 32230 |
| attack_matrix/A08/A | 0.9953364423717521 | None / 0 | None | 3.524 / 3.604 | None / None | 0.0 | 0 |
| attack_matrix/A08/B | 0.9953364423717521 | 5.212839341344014 / 50.0 | 4.138041305796136 | 3.524 / 3.604 | None / None | 0.0 | 0 |
| attack_matrix/A08/C | 0.9953364423717521 | 5.194904316866934 / 82.0 | 4.122940262047524 | 3.524 / 3.604 | None / None | 0.0 | 0 |
| attack_matrix/A09/A | 0.9993337774816788 | None / 0 | None | 3.524 / 3.552 | None / None | 12.969999999999768 | 0 |
| attack_matrix/A09/B | 0.5662891405729513 | 5.281298643540138 / 92.0 | 4.210393071285809 | 3.524 / 3.552 | 2.02 / 2.03 | 0.0 | 0 |
| attack_matrix/A09/C | 0.5662891405729513 | 5.241850122303758 / 35.0 | 4.170597379524762 | 3.524 / 3.552 | 2.02 / 2.03 | 0.0 | 0 |
| attack_matrix/A10/A | 0.9993337774816788 | None / 0 | None | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_matrix/A10/B | 0.6563833278634723 | 5.285391018305862 / 68.0 | 4.216104674651997 | 3.524 / 3.544 | 4.01 / 4.02 | 1.9704862049667358 | 0 |
| attack_matrix/A10/C | 0.9860093271152565 | 5.266377585056705 / 59.0 | 4.192671552298467 | 3.524 / 3.544 | 4.01 / 4.02 | 10.879999999999812 | 0 |
| attack_matrix/A11/A | 0.9982668977469671 | None / 0 | None | None / None | None / None | 3.760000000000036 | 0 |
| attack_matrix/A11/B | 0.9982668977469671 | 5.2101449275362315 / 48.0 | 4.118197573656846 | None / None | None / None | 3.760000000000036 | 0 |
| attack_matrix/A11/C | 0.9982668977469671 | 5.233623188405797 / 30.0 | 4.1606008087810515 | None / None | None / None | 3.760000000000036 | 0 |
| attack_matrix/A12/A | 0.9993337774816788 | None / 0 | None | None / 2.01 | None / None | 0.0 | 0 |
| attack_matrix/A12/B | 0.9993337774816788 | 5.252990882810763 / 150.0 | 4.219720186542305 | None / 2.01 | None / None | 0.0 | 0 |
| attack_matrix/A12/C | 0.9993337774816788 | 5.230553702468312 / 160.0 | 4.21376859871197 | None / 2.01 | None / None | 0.0 | 0 |
| coengineering/C01_forged_rejected/A | 0.9990006662225184 | None / 0 | None | None / 2.01 | None / None | 0.0 | 0 |
| coengineering/C01_forged_rejected/B | 0.5659560293137909 | 4.8019949807808375 / 50.0 | 4.077670441927603 | None / None | 2.01 / 2.02 | 0.0 | 0 |
| coengineering/C01_forged_rejected/C | 0.5659560293137909 | 4.814320658216589 / 28.0 | 4.11892071952032 | None / None | 2.01 / 2.02 | 0.0 | 0 |
| coengineering/C02_legitimate_bad_auth/A | 0.9993337774816788 | None / 0 | None | 3.52 / 3.54 | None / None | 0.0 | 0 |
| coengineering/C02_legitimate_bad_auth/B | 0.3466204506065858 | 5.252463768115942 / 54.0 | 4.170036587714231 | 3.52 / None | 2.01 / 2.02 | 3.6400000000000388 | 0 |
| coengineering/C02_legitimate_bad_auth/C | 0.3466204506065858 | 5.341642512077295 / 95.0 | 4.211245907953014 | 3.52 / None | 2.01 / 2.02 | 3.6400000000000388 | 0 |
| coengineering/C03_desync/A | 0.9993337774816788 | None / 0 | None | 3.52 / 3.54 | None / None | 0.0 | 0 |
| coengineering/C03_desync/B | 0.3466204506065858 | 5.608309178743961 / 89.0 | 4.289813210090506 | 3.52 / None | 2.01 / 2.02 | 3.6400000000000388 | 0 |
| coengineering/C03_desync/C | 0.9993337774816788 | 5.778148395226447 / 103.0 | 4.505958990302761 | 3.52 / 3.54 | 2.01 / 2.02 | 0.0 | 0 |
| coengineering/C04_flood/A | 0.975016655562958 | None / 0 | None | 3.52 / 3.54 | 2.03 / None | 12.88999999999977 | 30888 |
| coengineering/C04_flood/B | 0.558294470353098 | 5.354324832911557 / 139.0 | 4.191872085276483 | 3.52 / 3.54 | 2.03 / 2.03 | 12.88999999999977 | 30888 |
| coengineering/C04_flood/C | 0.558294470353098 | 5.335215106093051 / 119.0 | 4.199755718409949 | 3.52 / 3.54 | 2.03 / 2.03 | 12.88999999999977 | 30888 |
| coengineering/C05_gateway_down/A | 0.3466204506065858 | None / 0 | None | 3.52 / None | None / None | 3.6500000000000385 | 0 |
| coengineering/C05_gateway_down/B | 0.3466204506065858 | 5.464274619447034 / 116.0 | 4.1691666666666665 | 3.52 / None | None / None | 3.6500000000000385 | 0 |
| coengineering/C05_gateway_down/C | 0.3466204506065858 | 5.481360671015843 / 86.0 | 4.2283333333333335 | 3.52 / None | None / None | 3.6500000000000385 | 0 |
| coengineering/C06_primary_bad_backup_healthy/A | 0.9990006662225184 | None / 0 | None | 3.52 / 3.54 | None / None | 0.0 | 0 |
| coengineering/C06_primary_bad_backup_healthy/B | 0.5659560293137909 | 5.369293814924235 / 86.0 | 4.254274927825894 | 3.52 / 3.55 | 2.01 / 2.02 | 0.0 | 0 |
| coengineering/C06_primary_bad_backup_healthy/C | 0.5659560293137909 | 5.293814924235204 / 60.0 | 4.187375083277815 | 3.52 / 3.55 | 2.01 / 2.02 | 0.0 | 0 |
| coengineering/C07_shared_compromise/A | 0.9990006662225184 | None / 0 | None | None / 2.01 | None / None | 0.0 | 0 |
| coengineering/C07_shared_compromise/B | 0.9990006662225184 | 5.243463896565965 / 80.0 | 4.1620586275816125 | None / 2.01 | None / None | 0.0 | 0 |
| coengineering/C07_shared_compromise/C | 0.9990006662225184 | 5.243305060516535 / 60.0 | 4.159560293137908 | None / 2.01 | None / None | 0.0 | 0 |
| coengineering/C08_trusted_ecu/A | 0.9990006662225184 | None / 0 | None | None / 2.01 | None / None | 0.0 | 0 |
| coengineering/C08_trusted_ecu/B | 0.9990006662225184 | 5.325868039010134 / 92.0 | 4.22035309793471 | None / 2.01 | None / None | 0.0 | 0 |
| coengineering/C08_trusted_ecu/C | 0.9990006662225184 | 5.402617618094602 / 90.0 | 4.263268931823229 | None / 2.01 | None / None | 0.0 | 0 |
| attack_free/FI01/A | 0.9990006662225184 | None / 0 | None | 3.52 / 3.54 | None / None | 0.0 | 0 |
| attack_free/FI01/B | 0.9990006662225184 | 5.325893452778042 / 97.0 | 4.1990672884743505 | 3.52 / 3.54 | None / None | 0.0 | 0 |
| attack_free/FI01/C | 0.9990006662225184 | 5.377070427904317 / 99.0 | 4.238441039307128 | 3.52 / 3.54 | None / None | 0.0 | 0 |
| attack_free/FI02/A | 0.6392405063291139 | None / 0 | None | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_free/FI02/B | 0.6392405063291139 | 5.523701264209073 / 93.0 | 4.249133910726183 | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_free/FI02/C | 0.6392405063291139 | 5.466928715606077 / 108.0 | 4.215489673550966 | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_free/S01/A | 0.9992503748125937 | None / 0 | None | None / None | None / None | 0.0 | 0 |
| attack_free/S01/B | 0.9992503748125937 | 5.2873865504180655 / 68.0 | 4.189130434782609 | None / None | None / None | 0.0 | 0 |
| attack_free/S01/C | 0.9992503748125937 | 5.457142857142857 / 122.0 | 4.275962018990504 | None / None | None / None | 0.0 | 0 |
| attack_free/S02/A | 0.9990006662225184 | None / 0 | None | 2.158 / 2.178 | None / None | 0.0 | 0 |
| attack_free/S02/B | 0.9990006662225184 | 5.646087868102545 / 146.0 | 4.355163224516988 | 2.158 / 2.178 | None / None | 0.0 | 0 |
| attack_free/S02/C | 0.9990006662225184 | 5.554941389497761 / 143.0 | 4.30506329113924 | 2.158 / 2.178 | None / None | 0.0 | 0 |
| attack_free/S03/A | 0.9990006662225184 | None / 0 | None | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_free/S03/B | 0.9990006662225184 | 5.52476889354808 / 115.0 | 4.31055962691539 | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_free/S03/C | 0.9990006662225184 | 5.409758886876966 / 71.0 | 4.254230512991339 | 3.524 / 3.544 | None / None | 0.0 | 0 |
| attack_free/S04/A | 0.9992503748125937 | None / 0 | None | 4.662 / 4.6819999999999995 | None / None | 0.0 | 0 |
| attack_free/S04/B | 0.9992503748125937 | 5.343014364325019 / 68.0 | 4.1908545727136435 | 4.662 / 4.6819999999999995 | None / None | 0.0 | 0 |
| attack_free/S04/C | 0.9992503748125937 | 5.413178017580218 / 91.0 | 4.239055472263868 | 4.662 / 4.6819999999999995 | None / None | 0.0 | 0 |
| locked_v3_holdout/locked_v3_holdout/A | 0.998286479532657 | None / 0 | None | 3.304642857142857 / 3.34625 | None / None | 0.11776912847865673 | 0 |
| locked_v3_holdout/locked_v3_holdout/B | 0.998286479532657 | 5.318827490861647 / 474.0 | 4.18397955616687 | 3.304642857142857 / 3.34625 | None / None | 0.11776912847865673 | 0 |
| locked_v3_holdout/locked_v3_holdout/C | 0.998286479532657 | 5.304932689245704 / 740.0 | 4.165526096693947 | 3.304642857142857 / 3.34625 | None / None | 0.11776912847865673 | 0 |
| new_security_holdout/new_security_holdout/A | 0.9960756755770126 | None / 0 | None | 2.2830555555555554 / 2.2302083333333336 | 2.375 / None | 5.903749999999895 | 39377 |
| new_security_holdout/new_security_holdout/B | 0.7144597844859556 | 5.3218297062837925 / 107.0 | 4.237433699903076 | 2.2475757575757576 / 1.6017241379310345 | 2.3164864864864865 / 2.324054054054054 | 6.772881010655751 | 39377 |
| new_security_holdout/new_security_holdout/C | 0.7749450080913205 | 5.279199749587578 / 117.0 | 4.212456377041747 | 2.2475757575757576 / 1.7867741935483872 | 2.3164864864864865 / 2.324054054054054 | 7.229539157898674 | 39377 |

Metrics and interpretation:
- Message rates are descriptive, not independent Bernoulli trials: cached sensor PDUs, repeated commands and broadcast subscriptions are correlated.
- Native acceptance is reported only with no backup so the accepted channel is unambiguous. Gateway delivery is not proof of CRC acceptance or safe actuation.
- Sensor attack accepted/rejected counts are separate in raw JSON; A01/11 do not inject a command directly. Unnecessary braking measures achieved braking with no actual target, including injected actuation invisible to ADAS request state.
- In attack-free runs, correctly formed in-policy legitimate offers measure false rejection. Operational legitimate-demand loss under tag/freshness faults is a different quantity. Bad-tag rejection is correct cryptographic behavior, even when it removes a legitimate driver-assistance demand.
- Legitimate rejection includes explicitly valid producer/freshness faults and bad-tag transmission, and counts verifier offers; withheld or queue-dropped messages are separately recorded, not silently called accepted.
- Command availability = gateway-delivered command frames / generated frames across configured paths; it is not physical braking availability. Body/ADAS broadcast subscribers are counted separately in verifier offer statistics.
- First-event and DTC times use simulation start; subtract each stored injection onset for response latency. Gateway-down injection itself is not an observed detection; existing native feedback timeout provides that signal.
- First request and achieved-brake columns together support intervention/build-up latency; None means undefined, never zero. CPU measurements are host process timings including Python parsing, HMAC, FFI and concurrent host effects, not target ECU WCET.
- Protected packets are 64 CAN FD bytes versus 8 legacy payload bytes: 56 added bytes per command/status. Sensor messages have 21 bytes payload plus 43 envelope/padding/tag bytes. Sensor crypto/transport scheduling is not physically modeled; measured CPU is not injected into logical time.
- No aggregate attack probability is inferred. For repeated per-case seeds, safety counts are conditional on the toy noise model. New security hold-outs use a fixed artificial parameter/attack mixture; no real-world frequency claim.
- Original 120 hold-outs are unchanged and already known; the 48 new security cases were fixed before execution, not described as hidden from the implementer. No thresholds were tuned against their outcomes.
