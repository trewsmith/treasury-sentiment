# Gotthelf, 2019, News Sentiment - A New Yield Curve Factor

## 1. Research Question

What are the authors actually trying to determine?
-the two questions the authors are trying to answer are does the sentiment derived from newspaper articles impact sovereign bond investors and thus the US government bond yield curve? Does the significance of this effect vary depending on the duration of the bond takne into consideration?
## 2. Why It Matters

What economic problem motivates the paper?
-introduce a new curve factor: news sentiment that is different from traditional slope and curvature measures

## 3. Data

- Source: reuters sentiment analysis tools
- Frequency: 1d-30y
- Number of observations: 134 * 4 across categories
- Asset/yield: us treasury bills/notes/bonds

## 4. Text / Sentiment Construction

How do they convert text into a variable?

- dictionary: bag of words method for easy classification based on positive/negative leaning words
- machine learning? reuters articles NLP trained on human finance professionals scoring the model -1/0/1
- human labels? yes, finance professionals
- topic classification? yes, politics/debt/monetary news
- sentiment score? -1/0/1

## 5. Empirical Design

news sentiment is always positive coeffienct in the equation


## 6. Main Results

1. 10% significance on 7, 10, and 30 year periods
2. 1% significance on shorter periods
3. news sentiment is always negative to slope

## 7. Mechanism

Why do the authors think this happens? pyschological factors such as overconfidence and self-attribution

## 8. Limitations

What can their design NOT establish? proper causal connections and more detailed intraday analysis

## 9. What I Can Steal

- news sentiment as a coeffienct
- compare with traditional methods


## 10. What My Project Does Differently

- intraday windows
- compare with social media
- more documents and traditional NLP using agents to score and improve model
## 11. Citation Use

I can cite this paper when saying:

> introducing the topic

