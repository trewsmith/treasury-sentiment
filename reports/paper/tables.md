# Paper tables (auto-generated; do not edit)

## T1 Daily 10y, news and Reddit, 2025+
| controls | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|
| no_2y | news_sent_wmean | -0.062 | 0.257 | 0.810 | 1.000 | 472 |
| no_2y | news_ydir_wmean | -0.261 | 0.139 | 0.061 | 0.850 | 472 |
| no_2y | reddit_sent_wmean | 0.621 | 0.208 | 0.003 | 0.042 | 472 |
| no_2y | reddit_ydir_wmean | 0.309 | 0.279 | 0.267 | 1.000 | 472 |
| no_2y | WALD:reddit_sent_wmean+reddit_ydir_wmean |  |  | 0.008 |  | 472 |
| with_2y | news_sent_wmean | 0.084 | 0.173 | 0.626 | 1.000 | 472 |
| with_2y | news_ydir_wmean | -0.123 | 0.082 | 0.135 | 1.000 | 472 |
| with_2y | reddit_sent_wmean | -0.019 | 0.129 | 0.884 | 1.000 | 472 |
| with_2y | reddit_ydir_wmean | 0.047 | 0.172 | 0.784 | 1.000 | 472 |
| with_2y | WALD:reddit_sent_wmean+reddit_ydir_wmean |  |  | 0.949 |  | 472 |

## T2 Long news-only sample
| controls | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|
| no_2y | news_sent_wmean | -0.135 | 0.086 | 0.116 | 1.000 | 5,212 |
| no_2y | news_ydir_wmean | -0.085 | 0.088 | 0.336 | 1.000 | 5,212 |
| with_2y | news_sent_wmean | -0.018 | 0.061 | 0.773 | 1.000 | 5,212 |
| with_2y | news_ydir_wmean | -0.100 | 0.057 | 0.081 | 1.000 | 5,212 |

## T3 News vs. Reddit by window (joint block tests)
| window | controls | var | p | p_holm | n |
|---|---|---|---|---|---|
| all_2025+ (secondary) | no_2y | news_block|reddit | 0.248 | 1.000 | 472 |
| all_2025+ (secondary) | no_2y | reddit_block|news | 0.009 | 0.106 | 472 |
| all_2025+ (secondary) | no_2y | press_block|reddit | 0.344 | 1.000 | 472 |
| all_2025+ (secondary) | no_2y | reddit_block|press | 0.011 | 0.122 | 472 |
| all_2025+ (secondary) | with_2y | news_block|reddit | 0.249 | 1.000 | 472 |
| all_2025+ (secondary) | with_2y | reddit_block|news | 0.948 | 1.000 | 472 |
| all_2025+ (secondary) | with_2y | press_block|reddit | 0.132 | 1.000 | 472 |
| all_2025+ (secondary) | with_2y | reddit_block|press | 0.981 | 1.000 | 472 |
| press_covered_2025-11-24+ (main) | no_2y | news_block|reddit | 0.521 | 1.000 | 249 |
| press_covered_2025-11-24+ (main) | no_2y | reddit_block|news | 0.026 | 0.252 | 249 |
| press_covered_2025-11-24+ (main) | no_2y | press_block|reddit | 0.436 | 1.000 | 249 |
| press_covered_2025-11-24+ (main) | no_2y | reddit_block|press | 0.025 | 0.252 | 249 |
| press_covered_2025-11-24+ (main) | with_2y | news_block|reddit | 0.297 | 1.000 | 249 |
| press_covered_2025-11-24+ (main) | with_2y | reddit_block|news | 0.869 | 1.000 | 249 |
| press_covered_2025-11-24+ (main) | with_2y | press_block|reddit | 0.227 | 1.000 | 249 |
| press_covered_2025-11-24+ (main) | with_2y | reddit_block|press | 0.921 | 1.000 | 249 |
| before_2025-11-24 | no_2y | news_block|reddit | <0.001 | <0.001 | 223 |
| before_2025-11-24 | no_2y | reddit_block|news | 0.234 | 1.000 | 223 |
| before_2025-11-24 | no_2y | press_block|reddit | <0.001 | 0.003 | 223 |
| before_2025-11-24 | no_2y | reddit_block|press | 0.274 | 1.000 | 223 |
| before_2025-11-24 | with_2y | news_block|reddit | 0.015 | 0.218 | 223 |
| before_2025-11-24 | with_2y | reddit_block|news | 0.905 | 1.000 | 223 |
| before_2025-11-24 | with_2y | press_block|reddit | 0.007 | 0.108 | 223 |
| before_2025-11-24 | with_2y | reddit_block|press | 0.931 | 1.000 | 223 |
| excl_2025Q2Q3 | no_2y | news_block|reddit | 0.426 | 1.000 | 346 |
| excl_2025Q2Q3 | no_2y | reddit_block|news | 0.007 | 0.093 | 346 |
| excl_2025Q2Q3 | no_2y | press_block|reddit | 0.331 | 1.000 | 346 |
| excl_2025Q2Q3 | no_2y | reddit_block|press | 0.007 | 0.095 | 346 |
| excl_2025Q2Q3 | with_2y | news_block|reddit | 0.290 | 1.000 | 346 |
| excl_2025Q2Q3 | with_2y | reddit_block|news | 0.934 | 1.000 | 346 |
| excl_2025Q2Q3 | with_2y | press_block|reddit | 0.186 | 1.000 | 346 |
| excl_2025Q2Q3 | with_2y | reddit_block|press | 0.969 | 1.000 | 346 |

## T4 Main window 2025-11-24+, coefficients
| controls | var | coef_bp_per_sd | se | p | p_holm | mde80 | n |
|---|---|---|---|---|---|---|---|
| no_2y | press_sent_mean | 0.317 | 0.274 | 0.247 | 1.000 | 0.766 | 249 |
| no_2y | press_ydir_mean | -0.218 | 0.327 | 0.506 | 1.000 | 0.916 | 249 |
| no_2y | reddit_sent_wmean | 0.708 | 0.261 | 0.007 | 0.172 | 0.731 | 249 |
| no_2y | reddit_ydir_wmean | 0.138 | 0.343 | 0.688 | 1.000 | 0.961 | 249 |
| with_2y | press_sent_mean | 0.248 | 0.157 | 0.114 | 1.000 | 0.440 | 249 |
| with_2y | press_ydir_mean | -0.147 | 0.195 | 0.450 | 1.000 | 0.545 | 249 |
| with_2y | reddit_sent_wmean | -0.066 | 0.162 | 0.685 | 1.000 | 0.454 | 249 |
| with_2y | reddit_ydir_wmean | -0.028 | 0.220 | 0.899 | 1.000 | 0.616 | 249 |

## T5 Reddit robustness
| measure | spec | outcome | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|---|---|
| weighted | outcome | d10y_bp | r | 0.667 | 0.219 | 0.002 | 0.080 | 472 |
| weighted | outcome | d2y_bp | r | 0.904 | 0.194 | <0.001 | <0.001 | 472 |
| weighted | outcome | dslope_bp | r | -0.237 | 0.129 | 0.065 | 1.000 | 472 |
| weighted | with_2y | d10y_bp | r | -0.012 | 0.134 | 0.927 | 1.000 | 472 |
| weighted | lags | d10y_bp | r_lag1 | -0.349 | 0.215 | 0.105 | 1.000 | 470 |
| weighted | lags | d10y_bp | r | 0.671 | 0.212 | 0.002 | 0.059 | 470 |
| weighted | lags | d10y_bp | r_lead1 | 0.219 | 0.200 | 0.272 | 1.000 | 470 |
| weighted | pre_split_fed_only_news | d10y_bp | r | 0.530 | 0.320 | 0.098 | 1.000 | 223 |
| weighted | post_split | d10y_bp | r | 0.715 | 0.276 | 0.010 | 0.318 | 249 |
| weighted | press_control | d10y_bp | r | 0.642 | 0.215 | 0.003 | 0.097 | 472 |
| weighted | press_control | d10y_bp | press_sent_mean | 0.301 | 0.284 | 0.289 | 1.000 | 472 |
| weighted | press_control | d10y_bp | press_ydir_mean | -0.207 | 0.240 | 0.388 | 1.000 | 472 |
| weighted | lowvol_interaction | d10y_bp | r | 0.583 | 0.391 | 0.136 | 1.000 | 472 |
| weighted | lowvol_interaction | d10y_bp | r_x_lowvol | 0.180 | 0.471 | 0.702 | 1.000 | 472 |
| weighted | block_boot | d10y_bp | r | 0.667 |  | 0.003 |  | 472 |
| unweighted | outcome | d10y_bp | r | 0.534 | 0.215 | 0.013 | 0.407 | 472 |
| unweighted | outcome | d2y_bp | r | 0.784 | 0.196 | <0.001 | 0.003 | 472 |
| unweighted | outcome | dslope_bp | r | -0.250 | 0.126 | 0.046 | 1.000 | 472 |
| unweighted | with_2y | d10y_bp | r | -0.057 | 0.129 | 0.659 | 1.000 | 472 |
| unweighted | lags | d10y_bp | r_lag1 | -0.410 | 0.227 | 0.071 | 1.000 | 470 |
| unweighted | lags | d10y_bp | r | 0.530 | 0.207 | 0.010 | 0.334 | 470 |
| unweighted | lags | d10y_bp | r_lead1 | 0.304 | 0.196 | 0.121 | 1.000 | 470 |
| unweighted | pre_split_fed_only_news | d10y_bp | r | 0.434 | 0.351 | 0.216 | 1.000 | 223 |
| unweighted | post_split | d10y_bp | r | 0.636 | 0.261 | 0.015 | 0.428 | 249 |
| unweighted | press_control | d10y_bp | r | 0.511 | 0.214 | 0.017 | 0.469 | 472 |
| unweighted | press_control | d10y_bp | press_sent_mean | 0.291 | 0.282 | 0.301 | 1.000 | 472 |
| unweighted | press_control | d10y_bp | press_ydir_mean | -0.179 | 0.236 | 0.448 | 1.000 | 472 |
| unweighted | lowvol_interaction | d10y_bp | r | 0.595 | 0.373 | 0.110 | 1.000 | 472 |
| unweighted | lowvol_interaction | d10y_bp | r_x_lowvol | -0.051 | 0.461 | 0.912 | 1.000 | 472 |
| unweighted | block_boot | d10y_bp | r | 0.534 |  | 0.012 |  | 472 |
| unweighted_exwsb | outcome | d10y_bp | r | 0.645 | 0.206 | 0.002 | 0.066 | 472 |
| unweighted_exwsb | outcome | d2y_bp | r | 0.805 | 0.201 | <0.001 | 0.003 | 472 |
| unweighted_exwsb | outcome | dslope_bp | r | -0.159 | 0.128 | 0.214 | 1.000 | 472 |
| unweighted_exwsb | with_2y | d10y_bp | r | 0.042 | 0.127 | 0.739 | 1.000 | 472 |
| unweighted_exwsb | lags | d10y_bp | r_lag1 | -0.445 | 0.212 | 0.036 | 0.938 | 470 |
| unweighted_exwsb | lags | d10y_bp | r | 0.623 | 0.202 | 0.002 | 0.077 | 470 |
| unweighted_exwsb | lags | d10y_bp | r_lead1 | 0.466 | 0.195 | 0.017 | 0.469 | 470 |
| unweighted_exwsb | pre_split_fed_only_news | d10y_bp | r | 0.623 | 0.346 | 0.072 | 1.000 | 223 |
| unweighted_exwsb | post_split | d10y_bp | r | 0.603 | 0.244 | 0.013 | 0.407 | 249 |
| unweighted_exwsb | press_control | d10y_bp | r | 0.627 | 0.205 | 0.002 | 0.080 | 472 |
| unweighted_exwsb | press_control | d10y_bp | press_sent_mean | 0.302 | 0.281 | 0.282 | 1.000 | 472 |
| unweighted_exwsb | press_control | d10y_bp | press_ydir_mean | -0.208 | 0.231 | 0.369 | 1.000 | 472 |
| unweighted_exwsb | lowvol_interaction | d10y_bp | r | 0.573 | 0.320 | 0.074 | 1.000 | 472 |
| unweighted_exwsb | lowvol_interaction | d10y_bp | r_x_lowvol | 0.202 | 0.412 | 0.625 | 1.000 | 472 |
| unweighted_exwsb | block_boot | d10y_bp | r | 0.645 |  | 0.002 |  | 472 |

## T6 Lead/lag, 2025+
| measure | k | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|
| press_all_dir | -2 | 0.556 | 0.271 | 0.040 | 1.000 | 298 |
| press_all_dir | -1 | 0.946 | 0.212 | <0.001 | <0.001 | 298 |
| press_all_dir | 0 | -0.071 | 0.251 | 0.779 | 1.000 | 298 |
| press_all_dir | 1 | 0.273 | 0.186 | 0.142 | 1.000 | 297 |
| press_all_dir | 2 | -0.130 | 0.237 | 0.584 | 1.000 | 296 |
| press_all_tone | -2 | -0.092 | 0.230 | 0.689 | 1.000 | 298 |
| press_all_tone | -1 | 0.023 | 0.217 | 0.915 | 1.000 | 298 |
| press_all_tone | 0 | 0.282 | 0.276 | 0.306 | 1.000 | 298 |
| press_all_tone | 1 | 0.321 | 0.208 | 0.124 | 1.000 | 297 |
| press_all_tone | 2 | 0.203 | 0.210 | 0.334 | 1.000 | 296 |
| press_timed_dir | -2 | 0.324 | 0.354 | 0.360 | 1.000 | 86 |
| press_timed_dir | -1 | 0.296 | 0.368 | 0.420 | 1.000 | 86 |
| press_timed_dir | 0 | 0.273 | 0.330 | 0.408 | 1.000 | 86 |
| press_timed_dir | 1 | -0.487 | 0.440 | 0.268 | 1.000 | 85 |
| press_timed_dir | 2 | 0.590 | 0.633 | 0.352 | 1.000 | 84 |
| press_timed_tone | -2 | 0.389 | 0.348 | 0.264 | 1.000 | 86 |
| press_timed_tone | -1 | 0.197 | 0.607 | 0.745 | 1.000 | 86 |
| press_timed_tone | 0 | 0.430 | 0.691 | 0.534 | 1.000 | 86 |
| press_timed_tone | 1 | -0.262 | 0.353 | 0.458 | 1.000 | 85 |
| press_timed_tone | 2 | -1.058 | 0.386 | 0.006 | 0.321 | 84 |
| press_placeholder_dir | -2 | 0.629 | 0.289 | 0.029 | 1.000 | 265 |
| press_placeholder_dir | -1 | 1.040 | 0.218 | <0.001 | <0.001 | 265 |
| press_placeholder_dir | 0 | -0.091 | 0.262 | 0.728 | 1.000 | 265 |
| press_placeholder_dir | 1 | 0.265 | 0.187 | 0.156 | 1.000 | 264 |
| press_placeholder_dir | 2 | -0.129 | 0.248 | 0.602 | 1.000 | 263 |
| press_placeholder_tone | -2 | 0.090 | 0.261 | 0.730 | 1.000 | 265 |
| press_placeholder_tone | -1 | 0.178 | 0.221 | 0.420 | 1.000 | 265 |
| press_placeholder_tone | 0 | 0.084 | 0.299 | 0.779 | 1.000 | 265 |
| press_placeholder_tone | 1 | 0.257 | 0.226 | 0.256 | 1.000 | 264 |
| press_placeholder_tone | 2 | 0.463 | 0.204 | 0.024 | 1.000 | 263 |
| fed_dir | -2 | -0.009 | 0.262 | 0.974 | 1.000 | 293 |
| fed_dir | -1 | -0.461 | 0.189 | 0.015 | 0.752 | 293 |
| fed_dir | 0 | -0.254 | 0.341 | 0.455 | 1.000 | 293 |
| fed_dir | 1 | 0.057 | 0.256 | 0.825 | 1.000 | 292 |
| fed_dir | 2 | 0.325 | 0.215 | 0.131 | 1.000 | 291 |
| fed_tone | -2 | 0.269 | 0.237 | 0.256 | 1.000 | 293 |
| fed_tone | -1 | 0.567 | 0.270 | 0.035 | 1.000 | 293 |
| fed_tone | 0 | -0.156 | 0.217 | 0.473 | 1.000 | 293 |
| fed_tone | 1 | -0.373 | 0.253 | 0.141 | 1.000 | 292 |
| fed_tone | 2 | 0.053 | 0.268 | 0.844 | 1.000 | 291 |
| reddit_dir | -2 | 0.509 | 0.178 | 0.004 | 0.242 | 472 |
| reddit_dir | -1 | 0.719 | 0.222 | 0.001 | 0.071 | 472 |
| reddit_dir | 0 | 0.274 | 0.224 | 0.222 | 1.000 | 472 |
| reddit_dir | 1 | -0.415 | 0.204 | 0.042 | 1.000 | 471 |
| reddit_dir | 2 | -0.022 | 0.157 | 0.887 | 1.000 | 470 |
| reddit_tone | -2 | 0.362 | 0.176 | 0.040 | 1.000 | 472 |
| reddit_tone | -1 | 0.341 | 0.198 | 0.085 | 1.000 | 472 |
| reddit_tone | 0 | 0.509 | 0.214 | 0.017 | 0.851 | 472 |
| reddit_tone | 1 | -0.192 | 0.226 | 0.394 | 1.000 | 471 |
| reddit_tone | 2 | 0.035 | 0.205 | 0.863 | 1.000 | 470 |
| reddit_exwsb_dir | -2 | 0.500 | 0.179 | 0.005 | 0.288 | 472 |
| reddit_exwsb_dir | -1 | 0.643 | 0.227 | 0.005 | 0.254 | 472 |
| reddit_exwsb_dir | 0 | 0.122 | 0.228 | 0.593 | 1.000 | 472 |
| reddit_exwsb_dir | 1 | -0.448 | 0.188 | 0.017 | 0.851 | 471 |
| reddit_exwsb_dir | 2 | 0.013 | 0.164 | 0.938 | 1.000 | 470 |
| reddit_exwsb_tone | -2 | 0.414 | 0.179 | 0.021 | 1.000 | 472 |
| reddit_exwsb_tone | -1 | 0.506 | 0.191 | 0.008 | 0.413 | 472 |
| reddit_exwsb_tone | 0 | 0.628 | 0.205 | 0.002 | 0.122 | 472 |
| reddit_exwsb_tone | 1 | -0.274 | 0.213 | 0.197 | 1.000 | 471 |
| reddit_exwsb_tone | 2 | -0.057 | 0.213 | 0.788 | 1.000 | 470 |

## T7 Out of sample
| spec | controls | var | value | n |
|---|---|---|---|---|
| oos_rolling250_news | no_2y | OOS_R2_full_vs_base | -0.019 | 472 |
| oos_rolling250_news | no_2y | dir_acc_base | 0.578 | 472 |
| oos_rolling250_news | no_2y | dir_acc_full | 0.576 | 472 |
| oos_rolling250_reddit | no_2y | OOS_R2_full_vs_base | 0.020 | 192 |
| oos_rolling250_reddit | no_2y | dir_acc_base | 0.635 | 192 |
| oos_rolling250_reddit | no_2y | dir_acc_full | 0.609 | 192 |
| oos_rolling250_news | with_2y | OOS_R2_full_vs_base | -0.003 | 472 |
| oos_rolling250_news | with_2y | dir_acc_base | 0.797 | 472 |
| oos_rolling250_news | with_2y | dir_acc_full | 0.794 | 472 |
| oos_rolling250_reddit | with_2y | OOS_R2_full_vs_base | -0.012 | 192 |
| oos_rolling250_reddit | with_2y | dir_acc_base | 0.807 | 192 |
| oos_rolling250_reddit | with_2y | dir_acc_full | 0.807 | 192 |

## T8 Hourly, predictive horizons
| spec | outcome | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|---|
| all_reddit | y1 | press_ydir_mean | -0.232 | 0.369 | 0.529 | 1.000 | 9,678 |
| all_reddit | y1 | press_sent_mean | -0.314 | 0.296 | 0.288 | 1.000 | 9,678 |
| all_reddit | y1 | reddit_ydir_mean | 0.049 | 0.070 | 0.484 | 1.000 | 9,678 |
| all_reddit | y1 | reddit_sent_mean | 0.061 | 0.073 | 0.404 | 1.000 | 9,678 |
| all_reddit | y2 | press_ydir_mean | -0.721 | 0.465 | 0.121 | 1.000 | 9,572 |
| all_reddit | y2 | press_sent_mean | -0.196 | 0.410 | 0.633 | 1.000 | 9,572 |
| all_reddit | y2 | reddit_ydir_mean | 0.059 | 0.108 | 0.585 | 1.000 | 9,572 |
| all_reddit | y2 | reddit_sent_mean | 0.180 | 0.108 | 0.095 | 1.000 | 9,572 |
| all_reddit | y4 | press_ydir_mean | -0.536 | 0.582 | 0.357 | 1.000 | 9,353 |
| all_reddit | y4 | press_sent_mean | -0.479 | 0.667 | 0.472 | 1.000 | 9,353 |
| all_reddit | y4 | reddit_ydir_mean | -0.006 | 0.165 | 0.971 | 1.000 | 9,353 |
| all_reddit | y4 | reddit_sent_mean | 0.096 | 0.161 | 0.550 | 1.000 | 9,353 |
| ex_wsb | y1 | press_ydir_mean | -0.235 | 0.369 | 0.525 | 1.000 | 9,678 |
| ex_wsb | y1 | press_sent_mean | -0.312 | 0.295 | 0.291 | 1.000 | 9,678 |
| ex_wsb | y1 | reddit_exwsb_ydir_mean | 0.079 | 0.084 | 0.344 | 1.000 | 9,678 |
| ex_wsb | y1 | reddit_exwsb_sent_mean | 0.049 | 0.082 | 0.549 | 1.000 | 9,678 |
| ex_wsb | y2 | press_ydir_mean | -0.720 | 0.466 | 0.122 | 1.000 | 9,572 |
| ex_wsb | y2 | press_sent_mean | -0.187 | 0.409 | 0.647 | 1.000 | 9,572 |
| ex_wsb | y2 | reddit_exwsb_ydir_mean | 0.025 | 0.127 | 0.846 | 1.000 | 9,572 |
| ex_wsb | y2 | reddit_exwsb_sent_mean | 0.161 | 0.117 | 0.170 | 1.000 | 9,572 |
| ex_wsb | y4 | press_ydir_mean | -0.536 | 0.581 | 0.356 | 1.000 | 9,353 |
| ex_wsb | y4 | press_sent_mean | -0.476 | 0.666 | 0.475 | 1.000 | 9,353 |
| ex_wsb | y4 | reddit_exwsb_ydir_mean | -0.007 | 0.172 | 0.968 | 1.000 | 9,353 |
| ex_wsb | y4 | reddit_exwsb_sent_mean | 0.099 | 0.168 | 0.555 | 1.000 | 9,353 |

## T9 Event study
| horizon_min | n_events | n_baseline | event_mean_bp | baseline_mean_bp | slot_matched_diff_bp | perm_p_one_sided |
|---|---|---|---|---|---|---|
| 5 | 17 | 100 | 17.625 | 2.435 | 14.886 | <0.001 |
| 30 | 17 | 100 | 18.580 | 4.771 | 12.527 | <0.001 |
| 60 | 17 | 100 | 19.951 | 6.621 | 12.280 | <0.001 |

## T10 Yield-direction classifier vs. hand labels
| model | A_hand_macro_f1 | A_hand_ci_lo | A_hand_ci_hi | A_hand_kappa | A_hand_down_f1 | C_batch3_macro_f1 |
|---|---|---|---|---|---|---|
| rules_only | 0.463 | 0.401 | 0.518 | 0.198 | 0.279 | 0.350 |
| lr 500ch (default) | 0.641 | 0.571 | 0.705 | 0.545 | 0.367 | 0.674 |
| lr 2000ch (old default) | 0.601 | 0.531 | 0.666 | 0.487 | 0.316 | 0.596 |
| lr 300ch | 0.633 | 0.560 | 0.697 | 0.518 | 0.379 | 0.644 |
| lr C=1 | 0.626 | 0.560 | 0.690 | 0.528 | 0.356 | 0.663 |
| lr C=16 | 0.612 | 0.539 | 0.680 | 0.491 | 0.364 | 0.675 |
| lr 500ch + finbert | 0.607 | 0.541 | 0.669 | 0.520 | 0.286 | 0.615 |

## T11 Information categories
| spec | controls | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|
| cat_news_inflation | no_2y | -0.222 | 0.192 | 0.246 | 1.000 | 5,212 |
| cat_reddit_inflation_2025+ | no_2y | 0.186 | 0.228 | 0.416 | 1.000 | 472 |
| cat_news_fed | no_2y | -0.090 | 0.103 | 0.380 | 1.000 | 5,212 |
| cat_reddit_fed_2025+ | no_2y | 0.273 | 0.188 | 0.146 | 1.000 | 472 |
| cat_news_growth | no_2y | -0.218 | 0.203 | 0.283 | 1.000 | 5,212 |
| cat_reddit_growth_2025+ | no_2y | 0.025 | 0.242 | 0.919 | 1.000 | 472 |
| cat_news_labor | no_2y | -0.339 | 0.221 | 0.125 | 1.000 | 5,212 |
| cat_reddit_labor_2025+ | no_2y | -0.139 | 0.189 | 0.464 | 1.000 | 472 |
| cat_news_fiscal | no_2y | 0.045 | 0.241 | 0.853 | 1.000 | 5,212 |
| cat_reddit_fiscal_2025+ | no_2y | -0.518 | 0.221 | 0.019 | 0.191 | 472 |
| cat_news_inflation | with_2y | -0.184 | 0.114 | 0.107 | 0.858 | 5,212 |
| cat_reddit_inflation_2025+ | with_2y | -0.022 | 0.148 | 0.884 | 1.000 | 472 |
| cat_news_fed | with_2y | -0.083 | 0.065 | 0.202 | 1.000 | 5,212 |
| cat_reddit_fed_2025+ | with_2y | 0.050 | 0.133 | 0.709 | 1.000 | 472 |
| cat_news_growth | with_2y | -0.127 | 0.129 | 0.326 | 1.000 | 5,212 |
| cat_reddit_growth_2025+ | with_2y | -0.144 | 0.134 | 0.281 | 1.000 | 472 |
| cat_news_labor | with_2y | -0.193 | 0.127 | 0.130 | 0.908 | 5,212 |
| cat_reddit_labor_2025+ | with_2y | -0.269 | 0.106 | 0.011 | 0.098 | 472 |
| cat_news_fiscal | with_2y | -0.144 | 0.148 | 0.331 | 1.000 | 5,212 |
| cat_reddit_fiscal_2025+ | with_2y | -0.382 | 0.105 | <0.001 | 0.003 | 472 |

## T12 Market regimes
| spec | controls | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|---|
| reg_vix_high_news | no_2y | news_sent_wmean | -0.073 | 0.136 | 0.591 | 1.000 | 2,369 |
| reg_vix_high_news | no_2y | news_ydir_wmean | -0.075 | 0.139 | 0.588 | 1.000 | 2,369 |
| reg_vix_high_news+reddit_2025+ | no_2y | news_sent_wmean | -0.126 | 0.308 | 0.682 | 1.000 | 259 |
| reg_vix_high_news+reddit_2025+ | no_2y | news_ydir_wmean | -0.260 | 0.192 | 0.175 | 1.000 | 259 |
| reg_vix_high_news+reddit_2025+ | no_2y | reddit_sent_wmean | 0.382 | 0.318 | 0.229 | 1.000 | 259 |
| reg_vix_high_news+reddit_2025+ | no_2y | reddit_ydir_wmean | 0.077 | 0.435 | 0.860 | 1.000 | 259 |
| reg_vix_low_news | no_2y | news_sent_wmean | -0.193 | 0.112 | 0.084 | 1.000 | 2,724 |
| reg_vix_low_news | no_2y | news_ydir_wmean | -0.086 | 0.116 | 0.457 | 1.000 | 2,724 |
| reg_vix_low_news+reddit_2025+ | no_2y | news_sent_wmean | -0.125 | 0.355 | 0.724 | 1.000 | 213 |
| reg_vix_low_news+reddit_2025+ | no_2y | news_ydir_wmean | -0.106 | 0.175 | 0.544 | 1.000 | 213 |
| reg_vix_low_news+reddit_2025+ | no_2y | reddit_sent_wmean | 0.719 | 0.244 | 0.003 | 0.087 | 213 |
| reg_vix_low_news+reddit_2025+ | no_2y | reddit_ydir_wmean | 0.148 | 0.397 | 0.710 | 1.000 | 213 |
| reg_rate_vol_high_news | no_2y | news_sent_wmean | -0.078 | 0.146 | 0.591 | 1.000 | 2,500 |
| reg_rate_vol_high_news | no_2y | news_ydir_wmean | 0.017 | 0.131 | 0.896 | 1.000 | 2,500 |
| reg_rate_vol_high_news+reddit_2025+ | no_2y | news_sent_wmean | -0.141 | 0.357 | 0.693 | 1.000 | 223 |
| reg_rate_vol_high_news+reddit_2025+ | no_2y | news_ydir_wmean | -0.149 | 0.199 | 0.455 | 1.000 | 223 |
| reg_rate_vol_high_news+reddit_2025+ | no_2y | reddit_sent_wmean | 0.530 | 0.364 | 0.146 | 1.000 | 223 |
| reg_rate_vol_high_news+reddit_2025+ | no_2y | reddit_ydir_wmean | 0.109 | 0.397 | 0.783 | 1.000 | 223 |
| reg_rate_vol_low_news | no_2y | news_sent_wmean | -0.145 | 0.105 | 0.169 | 1.000 | 2,574 |
| reg_rate_vol_low_news | no_2y | news_ydir_wmean | -0.154 | 0.115 | 0.182 | 1.000 | 2,574 |
| reg_rate_vol_low_news+reddit_2025+ | no_2y | news_sent_wmean | -0.048 | 0.352 | 0.892 | 1.000 | 249 |
| reg_rate_vol_low_news+reddit_2025+ | no_2y | news_ydir_wmean | -0.331 | 0.218 | 0.130 | 1.000 | 249 |
| reg_rate_vol_low_news+reddit_2025+ | no_2y | reddit_sent_wmean | 0.725 | 0.223 | 0.001 | 0.032 | 249 |
| reg_rate_vol_low_news+reddit_2025+ | no_2y | reddit_ydir_wmean | 0.644 | 0.426 | 0.130 | 1.000 | 249 |
| reg_event_news | no_2y | news_sent_wmean | -0.253 | 0.274 | 0.355 | 1.000 | 684 |
| reg_event_news | no_2y | news_ydir_wmean | -0.355 | 0.147 | 0.016 | 0.417 | 684 |
| reg_nonevent_news | no_2y | news_sent_wmean | -0.116 | 0.088 | 0.188 | 1.000 | 4,528 |
| reg_nonevent_news | no_2y | news_ydir_wmean | 0.103 | 0.103 | 0.316 | 1.000 | 4,528 |
| reg_vix_high_news | with_2y | news_sent_wmean | 0.135 | 0.100 | 0.175 | 1.000 | 2,369 |
| reg_vix_high_news | with_2y | news_ydir_wmean | -0.083 | 0.089 | 0.347 | 1.000 | 2,369 |
| reg_vix_high_news+reddit_2025+ | with_2y | news_sent_wmean | 0.246 | 0.246 | 0.319 | 1.000 | 259 |
| reg_vix_high_news+reddit_2025+ | with_2y | news_ydir_wmean | -0.104 | 0.116 | 0.373 | 1.000 | 259 |
| reg_vix_high_news+reddit_2025+ | with_2y | reddit_sent_wmean | -0.102 | 0.187 | 0.585 | 1.000 | 259 |
| reg_vix_high_news+reddit_2025+ | with_2y | reddit_ydir_wmean | -0.053 | 0.230 | 0.818 | 1.000 | 259 |
| reg_vix_low_news | with_2y | news_sent_wmean | -0.152 | 0.077 | 0.049 | 1.000 | 2,724 |
| reg_vix_low_news | with_2y | news_ydir_wmean | -0.125 | 0.080 | 0.117 | 1.000 | 2,724 |
| reg_vix_low_news+reddit_2025+ | with_2y | news_sent_wmean | -0.096 | 0.219 | 0.661 | 1.000 | 213 |
| reg_vix_low_news+reddit_2025+ | with_2y | news_ydir_wmean | -0.084 | 0.114 | 0.462 | 1.000 | 213 |
| reg_vix_low_news+reddit_2025+ | with_2y | reddit_sent_wmean | 0.063 | 0.190 | 0.740 | 1.000 | 213 |
| reg_vix_low_news+reddit_2025+ | with_2y | reddit_ydir_wmean | 0.064 | 0.230 | 0.780 | 1.000 | 213 |
| reg_rate_vol_high_news | with_2y | news_sent_wmean | 0.059 | 0.102 | 0.560 | 1.000 | 2,500 |
| reg_rate_vol_high_news | with_2y | news_ydir_wmean | -0.045 | 0.086 | 0.599 | 1.000 | 2,500 |
| reg_rate_vol_high_news+reddit_2025+ | with_2y | news_sent_wmean | -0.187 | 0.253 | 0.460 | 1.000 | 223 |
| reg_rate_vol_high_news+reddit_2025+ | with_2y | news_ydir_wmean | -0.035 | 0.123 | 0.777 | 1.000 | 223 |
| reg_rate_vol_high_news+reddit_2025+ | with_2y | reddit_sent_wmean | -0.369 | 0.231 | 0.111 | 1.000 | 223 |
| reg_rate_vol_high_news+reddit_2025+ | with_2y | reddit_ydir_wmean | 0.061 | 0.255 | 0.810 | 1.000 | 223 |
| reg_rate_vol_low_news | with_2y | news_sent_wmean | -0.071 | 0.077 | 0.351 | 1.000 | 2,574 |
| reg_rate_vol_low_news | with_2y | news_ydir_wmean | -0.134 | 0.077 | 0.083 | 1.000 | 2,574 |
| reg_rate_vol_low_news+reddit_2025+ | with_2y | news_sent_wmean | 0.303 | 0.223 | 0.175 | 1.000 | 249 |
| reg_rate_vol_low_news+reddit_2025+ | with_2y | news_ydir_wmean | -0.153 | 0.116 | 0.188 | 1.000 | 249 |
| reg_rate_vol_low_news+reddit_2025+ | with_2y | reddit_sent_wmean | 0.232 | 0.140 | 0.098 | 1.000 | 249 |
| reg_rate_vol_low_news+reddit_2025+ | with_2y | reddit_ydir_wmean | 0.043 | 0.212 | 0.839 | 1.000 | 249 |
| reg_event_news | with_2y | news_sent_wmean | 0.085 | 0.175 | 0.629 | 1.000 | 684 |
| reg_event_news | with_2y | news_ydir_wmean | -0.208 | 0.094 | 0.027 | 0.746 | 684 |
| reg_nonevent_news | with_2y | news_sent_wmean | -0.035 | 0.065 | 0.591 | 1.000 | 4,528 |
| reg_nonevent_news | with_2y | news_ydir_wmean | -0.037 | 0.069 | 0.586 | 1.000 | 4,528 |

## T13 Intraday 5/30/60 minutes (about three months; p not multiplicity-adjusted)
| spec | horizon_min | var | coef_bp_per_sd | se | p | n |
|---|---|---|---|---|---|---|
| news_only | 5 | news_ydir | -0.017 | 0.020 | 0.395 | 16,089 |
| news_only | 5 | ydir_pressure | -0.016 | 0.019 | 0.401 | 16,089 |
| news_plus_reddit | 5 | news_ydir | -0.018 | 0.020 | 0.363 | 16,089 |
| news_plus_reddit | 5 | reddit_ydir | -0.005 | 0.019 | 0.796 | 16,089 |
| news_plus_reddit | 5 | shock_score | -0.003 | 0.019 | 0.879 | 16,089 |
| news_only | 30 | news_ydir | 0.027 | 0.061 | 0.652 | 15,753 |
| news_only | 30 | ydir_pressure | -0.036 | 0.071 | 0.614 | 15,753 |
| news_plus_reddit | 30 | news_ydir | 0.021 | 0.060 | 0.723 | 15,753 |
| news_plus_reddit | 30 | reddit_ydir | -0.034 | 0.061 | 0.577 | 15,753 |
| news_plus_reddit | 30 | shock_score | 0.040 | 0.074 | 0.589 | 15,753 |
| news_only | 60 | news_ydir | -0.072 | 0.093 | 0.442 | 15,361 |
| news_only | 60 | ydir_pressure | -0.082 | 0.108 | 0.446 | 15,361 |
| news_plus_reddit | 60 | news_ydir | -0.076 | 0.095 | 0.425 | 15,361 |
| news_plus_reddit | 60 | reddit_ydir | -0.055 | 0.090 | 0.540 | 15,361 |
| news_plus_reddit | 60 | shock_score | -0.034 | 0.126 | 0.790 | 15,361 |

## T14 Hourly, same hour (y0) and prior hour (y-1, placebo); p not multiplicity-adjusted
| spec | outcome | var | coef_bp_per_sd | se | p | n |
|---|---|---|---|---|---|---|
| all_reddit | y0 | press_ydir_mean | -0.104 | 0.370 | 0.779 | 10,312 |
| all_reddit | y0 | press_sent_mean | 0.063 | 0.326 | 0.846 | 10,312 |
| all_reddit | y0 | reddit_ydir_mean | 0.041 | 0.078 | 0.603 | 10,312 |
| all_reddit | y0 | reddit_sent_mean | -0.042 | 0.066 | 0.532 | 10,312 |
| all_reddit | y-1 | press_ydir_mean | -0.275 | 0.313 | 0.380 | 9,826 |
| all_reddit | y-1 | press_sent_mean | -0.009 | 0.369 | 0.981 | 9,826 |
| all_reddit | y-1 | reddit_ydir_mean | 0.188 | 0.082 | 0.022 | 9,826 |
| all_reddit | y-1 | reddit_sent_mean | 0.047 | 0.063 | 0.463 | 9,826 |
| ex_wsb | y0 | press_ydir_mean | -0.103 | 0.369 | 0.781 | 10,312 |
| ex_wsb | y0 | press_sent_mean | 0.063 | 0.326 | 0.846 | 10,312 |
| ex_wsb | y0 | reddit_exwsb_ydir_mean | 0.035 | 0.083 | 0.672 | 10,312 |
| ex_wsb | y0 | reddit_exwsb_sent_mean | -0.042 | 0.075 | 0.574 | 10,312 |
| ex_wsb | y-1 | press_ydir_mean | -0.270 | 0.314 | 0.390 | 9,826 |
| ex_wsb | y-1 | press_sent_mean | -0.003 | 0.369 | 0.993 | 9,826 |
| ex_wsb | y-1 | reddit_exwsb_ydir_mean | 0.090 | 0.090 | 0.317 | 9,826 |
| ex_wsb | y-1 | reddit_exwsb_sent_mean | 0.092 | 0.071 | 0.196 | 9,826 |

## T15 News robustness
| variant | sample | controls | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|---|---|
| baseline | 2006+ | no_2y | news_sent_wmean | -0.135 | 0.086 | 0.116 | 1.000 | 5,212 |
| baseline | 2006+ | no_2y | news_ydir_wmean | -0.085 | 0.088 | 0.336 | 1.000 | 5,212 |
| baseline | 2006+ | with_2y | news_sent_wmean | -0.018 | 0.061 | 0.773 | 1.000 | 5,212 |
| baseline | 2006+ | with_2y | news_ydir_wmean | -0.100 | 0.057 | 0.081 | 1.000 | 5,212 |
| baseline | 2010+ | no_2y | news_sent_wmean | -0.137 | 0.091 | 0.132 | 1.000 | 4,211 |
| baseline | 2010+ | no_2y | news_ydir_wmean | -0.113 | 0.088 | 0.200 | 1.000 | 4,211 |
| baseline | 2010+ | with_2y | news_sent_wmean | -0.049 | 0.068 | 0.471 | 1.000 | 4,211 |
| baseline | 2010+ | with_2y | news_ydir_wmean | -0.084 | 0.057 | 0.140 | 1.000 | 4,211 |
| fed_midnight_next_day | 2006+ | no_2y | news_sent_wmean | -0.138 | 0.086 | 0.108 | 1.000 | 5,212 |
| fed_midnight_next_day | 2006+ | no_2y | news_ydir_wmean | -0.083 | 0.088 | 0.348 | 1.000 | 5,212 |
| fed_midnight_next_day | 2006+ | with_2y | news_sent_wmean | -0.020 | 0.061 | 0.742 | 1.000 | 5,212 |
| fed_midnight_next_day | 2006+ | with_2y | news_ydir_wmean | -0.090 | 0.057 | 0.116 | 1.000 | 5,212 |
| fed_midnight_next_day | 2010+ | no_2y | news_sent_wmean | -0.137 | 0.091 | 0.132 | 1.000 | 4,211 |
| fed_midnight_next_day | 2010+ | no_2y | news_ydir_wmean | -0.113 | 0.088 | 0.200 | 1.000 | 4,211 |
| fed_midnight_next_day | 2010+ | with_2y | news_sent_wmean | -0.049 | 0.068 | 0.471 | 1.000 | 4,211 |
| fed_midnight_next_day | 2010+ | with_2y | news_ydir_wmean | -0.084 | 0.057 | 0.140 | 1.000 | 4,211 |
| fed_midnight_dropped | 2006+ | no_2y | news_sent_wmean | -0.134 | 0.092 | 0.147 | 1.000 | 5,212 |
| fed_midnight_dropped | 2006+ | no_2y | news_ydir_wmean | -0.087 | 0.093 | 0.349 | 1.000 | 5,212 |
| fed_midnight_dropped | 2006+ | with_2y | news_sent_wmean | -0.024 | 0.067 | 0.717 | 1.000 | 5,212 |
| fed_midnight_dropped | 2006+ | with_2y | news_ydir_wmean | -0.103 | 0.061 | 0.088 | 1.000 | 5,212 |
| fed_midnight_dropped | 2010+ | no_2y | news_sent_wmean | -0.140 | 0.092 | 0.126 | 1.000 | 4,211 |
| fed_midnight_dropped | 2010+ | no_2y | news_ydir_wmean | -0.119 | 0.093 | 0.202 | 1.000 | 4,211 |
| fed_midnight_dropped | 2010+ | with_2y | news_sent_wmean | -0.048 | 0.068 | 0.482 | 1.000 | 4,211 |
| fed_midnight_dropped | 2010+ | with_2y | news_ydir_wmean | -0.089 | 0.060 | 0.139 | 1.000 | 4,211 |
| topical_news_only | 2006+ | no_2y | news_sent_wmean | -0.135 | 0.095 | 0.154 | 1.000 | 5,208 |
| topical_news_only | 2006+ | no_2y | news_ydir_wmean | -0.094 | 0.097 | 0.334 | 1.000 | 5,208 |
| topical_news_only | 2006+ | with_2y | news_sent_wmean | -0.035 | 0.070 | 0.614 | 1.000 | 5,208 |
| topical_news_only | 2006+ | with_2y | news_ydir_wmean | -0.098 | 0.063 | 0.119 | 1.000 | 5,208 |
| topical_news_only | 2010+ | no_2y | news_sent_wmean | -0.111 | 0.093 | 0.236 | 1.000 | 4,211 |
| topical_news_only | 2010+ | no_2y | news_ydir_wmean | -0.131 | 0.097 | 0.179 | 1.000 | 4,211 |
| topical_news_only | 2010+ | with_2y | news_sent_wmean | -0.044 | 0.070 | 0.536 | 1.000 | 4,211 |
| topical_news_only | 2010+ | with_2y | news_ydir_wmean | -0.085 | 0.063 | 0.176 | 1.000 | 4,211 |
| topical_news_only | 2025+ | no_2y | news_sent_wmean | -0.068 | 0.227 | 0.763 | 1.000 | 472 |
| topical_news_only | 2025+ | no_2y | news_ydir_wmean | -0.143 | 0.117 | 0.225 | 1.000 | 472 |
| topical_news_only | 2025+ | with_2y | news_sent_wmean | 0.104 | 0.166 | 0.531 | 1.000 | 472 |
| topical_news_only | 2025+ | with_2y | news_ydir_wmean | -0.104 | 0.079 | 0.191 | 1.000 | 472 |

## T16 Event-day interaction and daily lags
| spec | controls | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|---|
| placebo_lead | no_2y | news_ydir_lead1 | 0.140 | 0.080 | 0.080 | 1.000 | 5,211 |
| event_interact | no_2y | news_sent_wmean | -0.176 | 0.287 | 0.539 | 1.000 | 472 |
| event_interact | no_2y | news_ydir_wmean | -0.047 | 0.125 | 0.707 | 1.000 | 472 |
| event_interact | no_2y | news_sent_wmean_x_event | 0.780 | 0.756 | 0.302 | 1.000 | 472 |
| event_interact | no_2y | news_ydir_wmean_x_event | -0.629 | 0.387 | 0.104 | 1.000 | 472 |
| reddit_lags_2025+ | no_2y | reddit_sent_lag1 | -0.377 | 0.218 | 0.084 | 1.000 | 471 |
| reddit_lags_2025+ | no_2y | reddit_sent_wmean | 0.646 | 0.209 | 0.002 | 0.032 | 471 |
| reddit_lags_2025+ | no_2y | reddit_sent_lead1 | 0.208 | 0.196 | 0.289 | 1.000 | 471 |
| placebo_lead | with_2y | news_ydir_lead1 | -0.058 | 0.055 | 0.291 | 1.000 | 5,211 |
| event_interact | with_2y | news_sent_wmean | 0.130 | 0.197 | 0.509 | 1.000 | 472 |
| event_interact | with_2y | news_ydir_wmean | -0.124 | 0.091 | 0.177 | 1.000 | 472 |
| event_interact | with_2y | news_sent_wmean_x_event | -0.270 | 0.518 | 0.602 | 1.000 | 472 |
| event_interact | with_2y | news_ydir_wmean_x_event | 0.101 | 0.250 | 0.686 | 1.000 | 472 |
| reddit_lags_2025+ | with_2y | reddit_sent_lag1 | -0.009 | 0.139 | 0.947 | 1.000 | 471 |
| reddit_lags_2025+ | with_2y | reddit_sent_wmean | -0.077 | 0.135 | 0.567 | 1.000 | 471 |
| reddit_lags_2025+ | with_2y | reddit_sent_lead1 | 0.154 | 0.127 | 0.228 | 1.000 | 471 |

## T17 Lead result (2y) checks, exploratory
block_boot floor p = 0.0005; circ_shift floor p = 0.002. OOS uses same-day controls, so it is not a forecast.

| measure | spec | var | coef_bp_per_sd | se | p | p_holm | n |
|---|---|---|---|---|---|---|---|
| weighted | no_controls | r | 0.959 | 0.208 | <0.001 | <0.001 | 472 |
| weighted | baseline | r | 0.904 | 0.194 | <0.001 | <0.001 | 472 |
| weighted | lagged_yield | r | 0.919 | 0.196 | <0.001 | <0.001 | 472 |
| weighted | volume | r | 0.920 | 0.193 | <0.001 | <0.001 | 472 |
| weighted | volume | log_n | 0.124 | 0.232 | 0.592 | 1.000 | 472 |
| weighted | press_control | r | 0.888 | 0.191 | <0.001 | <0.001 | 472 |
| weighted | press_control | press_sent_mean | 0.044 | 0.265 | 0.867 | 1.000 | 472 |
| weighted | press_control | press_ydir_mean | -0.071 | 0.237 | 0.764 | 1.000 | 472 |
| weighted | lags | r_lag1 | -0.470 | 0.215 | 0.029 | 0.948 | 470 |
| weighted | lags | r | 0.978 | 0.200 | <0.001 | <0.001 | 470 |
| weighted | lags | r_lead1 | 0.078 | 0.204 | 0.703 | 1.000 | 470 |
| weighted | pre_split | r | 0.559 | 0.267 | 0.036 | 1.000 | 223 |
| weighted | post_split | r | 1.093 | 0.266 | <0.001 | 0.002 | 249 |
| weighted | no_event_days | r | 0.805 | 0.197 | <0.001 | 0.003 | 413 |
| weighted | lowvol_interaction | r | 1.071 | 0.318 | <0.001 | 0.033 | 472 |
| weighted | lowvol_interaction | r_x_lowvol | -0.253 | 0.397 | 0.524 | 1.000 | 472 |
| weighted | lead_lag | k=-2 | 0.486 | 0.175 | 0.006 | 0.215 | 472 |
| weighted | lead_lag | k=-1 | 0.205 | 0.201 | 0.308 | 1.000 | 472 |
| weighted | lead_lag | k=0 | 0.884 | 0.190 | <0.001 | <0.001 | 472 |
| weighted | lead_lag | k=1 | -0.225 | 0.214 | 0.291 | 1.000 | 471 |
| weighted | lead_lag | k=2 | 0.062 | 0.201 | 0.758 | 1.000 | 470 |
| weighted | hac10 | r | 0.904 | 0.184 | <0.001 |  | 472 |
| weighted | hac20 | r | 0.904 | 0.169 | <0.001 |  | 472 |
| weighted | loqo_min | r | 0.758 |  |  |  |  |
| weighted | loqo_max | r | 1.050 |  | <0.001 |  |  |
| weighted | block_boot | r | 0.904 |  | <0.001 |  | 472 |
| weighted | circ_shift | r | 0.904 |  | 0.002 |  | 472 |
| weighted | oos_r2 | OOS_R2 | 0.056 |  |  |  | 192 |
| unweighted | no_controls | r | 0.800 | 0.216 | <0.001 | 0.010 | 472 |
| unweighted | baseline | r | 0.784 | 0.196 | <0.001 | 0.004 | 472 |
| unweighted | lagged_yield | r | 0.792 | 0.198 | <0.001 | 0.004 | 472 |
| unweighted | volume | r | 0.799 | 0.195 | <0.001 | 0.003 | 472 |
| unweighted | volume | log_n | 0.115 | 0.234 | 0.622 | 1.000 | 472 |
| unweighted | press_control | r | 0.763 | 0.192 | <0.001 | 0.004 | 472 |
| unweighted | press_control | press_sent_mean | 0.028 | 0.263 | 0.915 | 1.000 | 472 |
| unweighted | press_control | press_ydir_mean | -0.038 | 0.232 | 0.871 | 1.000 | 472 |
| unweighted | lags | r_lag1 | -0.435 | 0.235 | 0.064 | 1.000 | 470 |
| unweighted | lags | r | 0.863 | 0.198 | <0.001 | <0.001 | 470 |
| unweighted | lags | r_lead1 | 0.038 | 0.198 | 0.850 | 1.000 | 470 |
| unweighted | pre_split | r | 0.462 | 0.289 | 0.110 | 1.000 | 223 |
| unweighted | post_split | r | 1.034 | 0.266 | <0.001 | 0.005 | 249 |
| unweighted | no_event_days | r | 0.692 | 0.201 | <0.001 | 0.026 | 413 |
| unweighted | lowvol_interaction | r | 1.123 | 0.312 | <0.001 | 0.015 | 472 |
| unweighted | lowvol_interaction | r_x_lowvol | -0.530 | 0.393 | 0.178 | 1.000 | 472 |
| unweighted | timing_separate | overnight | 0.524 | 0.226 | 0.020 | 0.726 | 472 |
| unweighted | timing_separate | session | 0.562 | 0.189 | 0.003 | 0.123 | 472 |
| unweighted | timing_joint | overnight | 0.411 | 0.244 | 0.092 | 1.000 | 472 |
| unweighted | timing_joint | session | 0.462 | 0.204 | 0.024 | 0.802 | 472 |
| unweighted | lead_lag | k=-2 | 0.351 | 0.174 | 0.044 | 1.000 | 472 |
| unweighted | lead_lag | k=-1 | 0.143 | 0.197 | 0.468 | 1.000 | 472 |
| unweighted | lead_lag | k=0 | 0.762 | 0.193 | <0.001 | 0.004 | 472 |
| unweighted | lead_lag | k=1 | -0.202 | 0.231 | 0.381 | 1.000 | 471 |
| unweighted | lead_lag | k=2 | 0.057 | 0.220 | 0.796 | 1.000 | 470 |
| unweighted | hac10 | r | 0.784 | 0.191 | <0.001 |  | 472 |
| unweighted | hac20 | r | 0.784 | 0.182 | <0.001 |  | 472 |
| unweighted | loqo_min | r | 0.580 |  |  |  |  |
| unweighted | loqo_max | r | 0.943 |  | 0.005 |  |  |
| unweighted | block_boot | r | 0.784 |  | <0.001 |  | 472 |
| unweighted | circ_shift | r | 0.784 |  | 0.002 |  | 472 |
| unweighted | oos_r2 | OOS_R2 | 0.050 |  |  |  | 192 |
| unweighted_exwsb | no_controls | r | 0.855 | 0.231 | <0.001 | 0.010 | 472 |
| unweighted_exwsb | baseline | r | 0.805 | 0.201 | <0.001 | 0.004 | 472 |
| unweighted_exwsb | lagged_yield | r | 0.849 | 0.201 | <0.001 | 0.002 | 472 |
| unweighted_exwsb | volume | r | 0.828 | 0.205 | <0.001 | 0.003 | 472 |
| unweighted_exwsb | volume | log_n | 0.144 | 0.238 | 0.545 | 1.000 | 472 |
| unweighted_exwsb | press_control | r | 0.791 | 0.199 | <0.001 | 0.004 | 472 |
| unweighted_exwsb | press_control | press_sent_mean | 0.048 | 0.263 | 0.855 | 1.000 | 472 |
| unweighted_exwsb | press_control | press_ydir_mean | -0.064 | 0.225 | 0.777 | 1.000 | 472 |
| unweighted_exwsb | lags | r_lag1 | -0.472 | 0.223 | 0.035 | 1.000 | 470 |
| unweighted_exwsb | lags | r | 0.818 | 0.207 | <0.001 | 0.004 | 470 |
| unweighted_exwsb | lags | r_lead1 | 0.330 | 0.189 | 0.081 | 1.000 | 470 |
| unweighted_exwsb | pre_split | r | 0.559 | 0.310 | 0.071 | 1.000 | 223 |
| unweighted_exwsb | post_split | r | 0.900 | 0.256 | <0.001 | 0.020 | 249 |
| unweighted_exwsb | no_event_days | r | 0.664 | 0.189 | <0.001 | 0.021 | 413 |
| unweighted_exwsb | lowvol_interaction | r | 1.013 | 0.323 | 0.002 | 0.071 | 472 |
| unweighted_exwsb | lowvol_interaction | r_x_lowvol | -0.344 | 0.376 | 0.361 | 1.000 | 472 |
| unweighted_exwsb | timing_separate | overnight | 0.506 | 0.221 | 0.022 | 0.779 | 472 |
| unweighted_exwsb | timing_separate | session | 0.611 | 0.217 | 0.005 | 0.192 | 472 |
| unweighted_exwsb | timing_joint | overnight | 0.398 | 0.231 | 0.085 | 1.000 | 472 |
| unweighted_exwsb | timing_joint | session | 0.531 | 0.222 | 0.017 | 0.615 | 472 |
| unweighted_exwsb | lead_lag | k=-2 | 0.450 | 0.182 | 0.014 | 0.517 | 472 |
| unweighted_exwsb | lead_lag | k=-1 | 0.398 | 0.189 | 0.035 | 1.000 | 472 |
| unweighted_exwsb | lead_lag | k=0 | 0.787 | 0.198 | <0.001 | 0.004 | 472 |
| unweighted_exwsb | lead_lag | k=1 | -0.283 | 0.226 | 0.212 | 1.000 | 471 |
| unweighted_exwsb | lead_lag | k=2 | 0.057 | 0.223 | 0.798 | 1.000 | 470 |
| unweighted_exwsb | hac10 | r | 0.805 | 0.193 | <0.001 |  | 472 |
| unweighted_exwsb | hac20 | r | 0.805 | 0.181 | <0.001 |  | 472 |
| unweighted_exwsb | loqo_min | r | 0.680 |  |  |  |  |
| unweighted_exwsb | loqo_max | r | 0.951 |  | <0.001 |  |  |
| unweighted_exwsb | block_boot | r | 0.805 |  | <0.001 |  | 472 |
| unweighted_exwsb | circ_shift | r | 0.805 |  | 0.002 |  | 472 |
| unweighted_exwsb | oos_r2 | OOS_R2 | 0.043 |  |  |  | 192 |

## T18 Descriptive statistics (text in raw units)
| window | var | n | mean | sd | min | median | max |
|---|---|---|---|---|---|---|---|
| 2006+ | d10y_bp | 5,226 | 0.010 | 5.681 | -51.000 | 0.000 | 29.000 |
| 2006+ | d2y_bp | 5,226 | 0.004 | 5.181 | -57.000 | 0.000 | 38.000 |
| 2006+ | dslope_bp | 5,226 | 0.006 | 3.970 | -28.000 | 0.000 | 42.000 |
| 2006+ | dvix | 5,226 | 0.005 | 1.953 | -18.710 | -0.100 | 24.860 |
| 2006+ | dsp500 | 5,226 | 0.033 | 1.222 | -12.765 | 0.073 | 10.424 |
| 2006+ | ddollar | 5,223 | 0.004 | 0.340 | -2.562 | -0.002 | 1.896 |
| 2006+ | doil | 5,215 | 0.021 | 2.812 | -28.138 | 0.037 | 42.583 |
| 2006+ | event_day | 5,226 | 0.131 | 0.337 | 0.000 | 0.000 | 1.000 |
| 2006+ | news_sent_wmean | 3,620 | -0.042 | 0.355 | -0.962 | 0.007 | 0.944 |
| 2006+ | news_ydir_wmean | 3,620 | 0.027 | 0.110 | -0.813 | 0.013 | 0.877 |
| 2006+ | press_sent_mean | 327 | -0.092 | 0.326 | -0.962 | -0.079 | 0.939 |
| 2006+ | press_ydir_mean | 327 | 0.163 | 0.229 | -0.929 | 0.138 | 0.894 |
| 2006+ | n_news_relevant | 5,226 | 1.974 | 5.699 | 0.000 | 1.000 | 134.000 |
| 2006+ | n_press | 5,226 | 0.796 | 5.589 | 0.000 | 0.000 | 133.000 |
| 2025+ | d10y_bp | 472 | 0.072 | 4.806 | -17.000 | 0.000 | 15.000 |
| 2025+ | d2y_bp | 472 | 0.081 | 5.284 | -25.000 | 0.000 | 20.000 |
| 2025+ | dslope_bp | 472 | -0.008 | 3.173 | -12.000 | 0.000 | 14.000 |
| 2025+ | dvix | 472 | 0.039 | 2.085 | -18.710 | -0.110 | 15.290 |
| 2025+ | dsp500 | 472 | 0.034 | 1.066 | -6.161 | 0.079 | 9.089 |
| 2025+ | ddollar | 472 | -0.010 | 0.298 | -1.314 | 0.008 | 0.863 |
| 2025+ | doil | 472 | 0.045 | 3.097 | -17.516 | 0.067 | 15.350 |
| 2025+ | event_day | 472 | 0.125 | 0.331 | 0.000 | 0.000 | 1.000 |
| 2025+ | news_sent_wmean | 416 | -0.063 | 0.282 | -0.917 | -0.030 | 0.898 |
| 2025+ | news_ydir_wmean | 416 | 0.120 | 0.190 | -0.769 | 0.065 | 0.816 |
| 2025+ | press_sent_mean | 298 | -0.087 | 0.264 | -0.961 | -0.076 | 0.858 |
| 2025+ | press_ydir_mean | 298 | 0.177 | 0.230 | -0.929 | 0.154 | 0.894 |
| 2025+ | reddit_sent_wmean | 472 | -0.158 | 0.108 | -0.468 | -0.156 | 0.292 |
| 2025+ | reddit_ydir_wmean | 472 | 0.044 | 0.056 | -0.101 | 0.032 | 0.335 |
| 2025+ | reddit_sent_mean | 472 | -0.127 | 0.087 | -0.394 | -0.128 | 0.221 |
| 2025+ | reddit_exwsb_sent_mean | 472 | -0.143 | 0.104 | -0.437 | -0.143 | 0.211 |
| 2025+ | n_news_relevant | 472 | 9.773 | 16.719 | 0.000 | 3.000 | 134.000 |
| 2025+ | n_press | 472 | 8.742 | 16.640 | 0.000 | 2.000 | 133.000 |
| 2025+ | n_reddit_relevant | 472 | 99.644 | 71.229 | 27.000 | 82.000 | 872.000 |
| 2025-11-24+ | d10y_bp | 249 | 0.345 | 4.556 | -17.000 | 1.000 | 15.000 |
| 2025-11-24+ | d2y_bp | 249 | 0.450 | 5.066 | -16.000 | 0.000 | 17.000 |
| 2025-11-24+ | dslope_bp | 249 | -0.104 | 2.933 | -9.000 | -0.000 | 10.000 |
| 2025-11-24+ | dvix | 249 | 0.050 | 1.793 | -5.720 | -0.120 | 11.570 |
| 2025-11-24+ | dsp500 | 249 | 0.018 | 0.904 | -4.453 | 0.016 | 2.871 |
| 2025-11-24+ | ddollar | 249 | 0.006 | 0.270 | -1.053 | 0.006 | 0.841 |
| 2025-11-24+ | doil | 249 | 0.168 | 3.813 | -17.516 | 0.267 | 15.350 |
| 2025-11-24+ | event_day | 249 | 0.129 | 0.335 | 0.000 | 0.000 | 1.000 |
| 2025-11-24+ | news_sent_wmean | 246 | -0.095 | 0.241 | -0.874 | -0.086 | 0.555 |
| 2025-11-24+ | news_ydir_wmean | 246 | 0.185 | 0.203 | -0.417 | 0.181 | 0.815 |
| 2025-11-24+ | press_sent_mean | 237 | -0.081 | 0.247 | -0.852 | -0.084 | 0.809 |
| 2025-11-24+ | press_ydir_mean | 237 | 0.206 | 0.236 | -0.929 | 0.216 | 0.894 |
| 2025-11-24+ | reddit_sent_wmean | 249 | -0.153 | 0.112 | -0.468 | -0.150 | 0.153 |
| 2025-11-24+ | reddit_ydir_wmean | 249 | 0.060 | 0.066 | -0.065 | 0.047 | 0.335 |
| 2025-11-24+ | reddit_sent_mean | 249 | -0.132 | 0.089 | -0.394 | -0.131 | 0.155 |
| 2025-11-24+ | reddit_exwsb_sent_mean | 249 | -0.139 | 0.111 | -0.437 | -0.135 | 0.130 |
| 2025-11-24+ | n_news_relevant | 249 | 13.530 | 19.185 | 0.000 | 6.000 | 134.000 |
| 2025-11-24+ | n_press | 249 | 12.522 | 18.987 | 0.000 | 5.000 | 133.000 |
| 2025-11-24+ | n_reddit_relevant | 249 | 76.807 | 38.461 | 27.000 | 68.000 | 241.000 |

## T19 Documents by source (after cleaning)
| source_type | source_name | docs | relevant | date_only_share | first | last | finbert_mean | ydir_mean |
|---|---|---|---|---|---|---|---|---|
| news | cnbc | 531 | 531 | 0.136 | 2025-01-01 | 2026-11-24 | -0.082 | 0.091 |
| news | federal_reserve | 6,158 | 6,158 | 0.112 | 2006-01-03 | 2026-11-20 | -0.013 | 0.015 |
| news | google_news | 2,820 | 2,820 | 0.831 | 2025-10-18 | 2026-11-24 | -0.086 | 0.275 |
| news | guardian | 68 | 68 | 0.000 | 2014-08-14 | 2026-11-21 | -0.148 | 0.072 |
| news | investing | 274 | 274 | 0.011 | 2025-01-01 | 2026-11-24 | 0.007 | 0.063 |
| news | marketwatch | 98 | 98 | 0.000 | 2024-02-27 | 2026-11-24 | -0.103 | 0.021 |
| news | seeking_alpha | 121 | 121 | 0.000 | 2026-10-16 | 2026-11-24 | 0.027 | 0.034 |
| news | yahoo_finance | 601 | 601 | 0.003 | 2025-01-01 | 2025-03-18 | -0.051 | 0.082 |
| reddit | r/bonds | 3,263 | 1,435 | 0.000 | 2025-01-01 | 2026-11-23 | -0.161 | 0.128 |
| reddit | r/economics | 18,805 | 8,953 | 0.000 | 2025-01-01 | 2026-11-23 | -0.201 | 0.095 |
| reddit | r/investing | 22,510 | 7,790 | 0.000 | 2025-01-01 | 2026-11-23 | -0.105 | 0.002 |
| reddit | r/securityanalysis | 544 | 88 | 0.000 | 2025-01-01 | 2026-11-22 | -0.032 | 0.022 |
| reddit | r/stocks | 22,893 | 9,990 | 0.000 | 2025-01-01 | 2026-11-23 | -0.156 | -0.001 |
| reddit | r/wallstreetbets | 88,958 | 19,022 | 0.000 | 2025-01-01 | 2026-11-24 | -0.106 | 0.007 |

## T20 Label distribution
| set | down | neutral | up | All |
|---|---|---|---|---|
| hand_batch1 | 8 | 62 | 30 | 100 |
| hand_batch2 | 9 | 84 | 27 | 120 |
| hand_batch3 | 11 | 88 | 21 | 120 |
| silver | 72 | 606 | 172 | 850 |
| All | 100 | 840 | 250 | 1,190 |

## T21 Classifier confusion, silver-trained default model vs. hand labels (rows = hand)
| hand | up | down | neutral |
|---|---|---|---|
| up | 49 | 10 | 19 |
| down | 4 | 11 | 13 |
| neutral | 14 | 11 | 209 |
