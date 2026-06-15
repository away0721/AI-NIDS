# Day7 Error Analysis Summary

## 1. Model Error Overview

This summary compares the error patterns of CNN, Random Forest, and Clipped Weighted CNN.

| model | total_errors | attack_to_benign_errors | benign_to_attack_errors | attack_to_attack_errors |
| --- | --- | --- | --- | --- |
| CNN | 1933 | 800 | 1097 | 36 |
| Random Forest | 636 | 316 | 305 | 15 |
| Clipped Weighted CNN | 24757 | 61 | 24522 | 174 |

## 2. Key Findings

| finding | model | meaning |
| --- | --- | --- |
| Total errors fewest | Random Forest | 整体错误数量最少，综合稳定性最好 |
| Attack -> BENIGN errors fewest | Clipped Weighted CNN | 攻击漏报最少，更适合减少漏报 |
| BENIGN -> Attack errors fewest | Random Forest | 正常流量误报最少，更适合降低告警噪声 |
| Total errors most | Clipped Weighted CNN | 整体错误数量最多，需要关注误报或漏报副作用 |

## 3. Highest Error Classes by Model

| model | highest_error_class | highest_error_rate | highest_error_count | highest_error_support | highest_attack_to_benign_class | highest_attack_to_benign_rate | highest_attack_to_benign_count | highest_attack_to_benign_support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CNN | WebAttack | 0.8945 | 390 | 436 | Infiltration | 0.8571 | 6 | 7 |
| Random Forest | Infiltration | 0.4286 | 3 | 7 | Infiltration | 0.4286 | 3 | 7 |
| Clipped Weighted CNN | Infiltration | 0.1429 | 1 | 7 | WebAttack | 0.0092 | 4 | 436 |

## 4. Main Observations

- Random Forest has the fewest total errors and the fewest BENIGN -> Attack false positives.
- Clipped Weighted CNN has the fewest Attack -> BENIGN false negatives, which means it is more sensitive to attacks.
- CNN has higher total errors than Random Forest and shows obvious minority-class false negatives, especially for WebAttack and Bot.
- Clipped Weighted CNN greatly reduces attack missed detection, but it introduces many BENIGN -> Attack false positives.
- The results confirm a clear trade-off: reducing false negatives usually increases false positives.

## 5. Generated Result Files

```txt
results/multiclass/cnn_error_patterns/
results/multiclass/random_forest_error_patterns/
results/multiclass/clipped_weighted_cnn_error_patterns/
results/multiclass/error_pattern_comparison/
results/multiclass/class_error_rate_comparison/
results/multiclass/error_analysis_summary/
```
