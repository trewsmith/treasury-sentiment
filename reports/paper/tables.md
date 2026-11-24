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
