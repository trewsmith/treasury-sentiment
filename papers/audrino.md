# audrino (2023) — The imapct of macroeconomic news sentiment on interest rates

## 1. Research Question

What are the authors actually trying to determine?
-inclusion of sentiment to short rate yield analysis, integrate empirical analysis with a theoretical foundation. able to provide out-of-sample predictive ablity?
2. Why It Matters

What economic problem motivates the paper?
-provide a theoretical foundation to a new form of fixed income analysis

## 3. Data

- Source: articles from 2000-2020 dow jones newswire database
- Frequency: 1d-30y
- Asset/yield: us treasury bills/notes/bonds

## 4. Text / Sentiment Construction

How do they convert text into a variable?

- dictionary: bag of words method for easy classification based on positive/negative scores, lexicon for scores
- machine learning? multiple models, random forest
- human labels? yes, based on emotion not market outcome
- topic classification? yes, sentiment classification as well
- sentiment score? based on confidence, highest reported in high 70s

## 5. Empirical Design

multiple models, regime 1/2, early predictor of economic recessions


## 6. Main Results

1. sentiment related to intrest rate news have a significant effect on 3 month treasury yield.
2. positive effect on slope
3. improves out of sample forecast accuracy of short-term yields

## 7. Mechanism

Why do the authors think this happens? irrational human behavior

## 8. Limitations

What can their design NOT establish? intraday windows and social media data

## 9. What I Can Steal

- multiple sentiment values
- mutliple models to compare
