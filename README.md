<p align="center">
    <img src="https://www.onlinelogomaker.com/blog/wp-content/uploads/2017/06/music-logo-design.jpg" alt="ILYrics Logo" width="200" />
</p>

# ILYrics, a minimal lyrics search engine
<!-- [![GitHub license](https://img.shields.io/github/license/smeelock/ilyrics)](https://github.com/smeelock/ilyrics/blob/main/LICENSE) -->

**ILYrics** is minimal lyrics search engine based on Django as the frontend, ElasticSearch as the backend, working with an AWS postgreSQL database and deployed on heroku [here](https://www.ilyrics.herokuapp.com "ILYrics"). 

This project is part of Tsinghua's 2021 WebIR Course taught by Prof. and inspired by [Genius](https://genius.com). In addition to the present code, the report and presentation slides are available [here](/report/WebIR%20A%20lyrics%20search%20engine%20-%20report.pdf "Report") and [here](/report/WebIR%20A%20lyrics%20search%20engine%20-%20slides.pdf "Slides")

## Components
ILYrics is composed of the following:
- **Django** (2.2.5)
- **ElasticSearch** (7.12.1) hosted inside a free tier AWS instance like [this one](https://aws.amazon.com/elasticsearch-service/ "AWS Elasticsearch Service")
- **PostgreSQL** online database with 20Go SSD storage, also hosted inside a free tier AWS instance like [this one](https://aws.amazon.com/rds/ "AWS RDS")
- **Heroku** is used to deploy the application as a 24/7 available website

## Features
ILYrics can find songs based a song name, an artist name. Thanks to the power of [ElasticSearch](https://www.elastic.co/) (based on Lucene), it can also **find songs based on part of lyrics**.

Feel free to experiment on https://www.ilyrics.herokuapp.com with queries like: *la vie en rose* or *bruno mars* or even *she's just a girl who claims that I am the one*.

## Offline deployment
As long as you have access tokens to each online component (e.g. within a `credentials.json` file), all you need to do is:
1. Make sure you have *git* and *pip* installed
2. Clone this repository using ```git clone https://github.com/smeelock/ilyrics```

3. Install required dependencies using ``pip install -r requirements.txt``

4. Run the application using ``python manage.py runserver``

5. Navigate to [localhost:8000](localhost:8000)
6. Enjoy :)

## Possible improvements
- **Scoring function** (currently using Lucene's bm25 but experimenting with more scoring functions can reveal more efficient methods)
- **Parsing** (currently not using parsing whatsoever but removing stopwords, stemming words, using pos-tagging... can greatly improve performance. Spacy would definitely be the go-to library.)
- **Query understanding** (e.g. using pretrained language models such as BERT or GPT-3)
- **Security** (e.g. with fully integrated IAM connection on AWS)
